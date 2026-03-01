import type { AppContext } from "../types";
import type { OAuthProvider } from "../schema";
import { getUserByEmail, createUser } from "../db/user";
import { getOAuthAccount, createOAuthAccount, updateOAuthTokens } from "../db/oauth";
import { createSession } from "../db/session";
import { generateId } from "../utils/helpers";
import { success, error } from "../utils/responses";

const SESSION_TTL_MS = 30 * 24 * 60 * 60 * 1000; // 30 days

interface OAuthUserInfo {
  email: string;
  name: string;
  avatar_url: string | null;
  provider_user_id: string;
}

// ── Google ──

function googleAuthUrl(c: AppContext): string {
  const params = new URLSearchParams({
    client_id: c.env.GOOGLE_CLIENT_ID,
    redirect_uri: c.env.OAUTH_REDIRECT_URL,
    response_type: "code",
    scope: "openid email profile",
    state: "google",
    access_type: "offline",
    prompt: "consent",
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
}

async function exchangeGoogleCode(c: AppContext, code: string) {
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      code,
      client_id: c.env.GOOGLE_CLIENT_ID,
      client_secret: c.env.GOOGLE_CLIENT_SECRET,
      redirect_uri: c.env.OAUTH_REDIRECT_URL,
      grant_type: "authorization_code",
    }),
  });
  if (!res.ok) throw new Error("Google token exchange failed");
  return (await res.json()) as { access_token: string; refresh_token?: string; expires_in: number };
}

async function getGoogleUser(accessToken: string): Promise<OAuthUserInfo> {
  const res = await fetch("https://www.googleapis.com/oauth2/v2/userinfo", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!res.ok) throw new Error("Failed to fetch Google user info");
  const data = (await res.json()) as { id: string; email: string; name: string; picture?: string };
  return {
    email: data.email,
    name: data.name,
    avatar_url: data.picture ?? null,
    provider_user_id: data.id,
  };
}

// ── GitHub ──

function githubAuthUrl(c: AppContext): string {
  const params = new URLSearchParams({
    client_id: c.env.GITHUB_CLIENT_ID,
    redirect_uri: c.env.OAUTH_REDIRECT_URL,
    scope: "read:user user:email",
    state: "github",
  });
  return `https://github.com/login/oauth/authorize?${params}`;
}

async function exchangeGithubCode(c: AppContext, code: string) {
  const res = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({
      client_id: c.env.GITHUB_CLIENT_ID,
      client_secret: c.env.GITHUB_CLIENT_SECRET,
      code,
      redirect_uri: c.env.OAUTH_REDIRECT_URL,
    }),
  });
  if (!res.ok) throw new Error("GitHub token exchange failed");
  return (await res.json()) as { access_token: string; refresh_token?: string; expires_in?: number };
}

async function getGithubUser(accessToken: string): Promise<OAuthUserInfo> {
  const [userRes, emailRes] = await Promise.all([
    fetch("https://api.github.com/user", {
      headers: { Authorization: `Bearer ${accessToken}`, "User-Agent": "podd-worker" },
    }),
    fetch("https://api.github.com/user/emails", {
      headers: { Authorization: `Bearer ${accessToken}`, "User-Agent": "podd-worker" },
    }),
  ]);

  if (!userRes.ok) throw new Error("Failed to fetch GitHub user info");
  const userData = (await userRes.json()) as { id: number; login: string; name?: string; avatar_url?: string };

  let email = "";
  if (emailRes.ok) {
    const emails = (await emailRes.json()) as { email: string; primary: boolean; verified: boolean }[];
    const primary = emails.find((e) => e.primary && e.verified);
    email = primary?.email ?? emails[0]?.email ?? "";
  }

  return {
    email,
    name: userData.name || userData.login,
    avatar_url: userData.avatar_url ?? null,
    provider_user_id: String(userData.id),
  };
}

// ── Shared: find-or-create user, issue session token ──

async function findOrCreateUser(
  db: D1Database,
  provider: OAuthProvider,
  userInfo: OAuthUserInfo,
  accessToken: string,
  refreshToken: string | null,
  expiresAt: string | null,
) {
  const existing = await getOAuthAccount(db, provider, userInfo.provider_user_id);

  if (existing) {
    await updateOAuthTokens(db, provider, userInfo.provider_user_id, accessToken, refreshToken, expiresAt);
    return existing.user_id;
  }

  let user = await getUserByEmail(db, userInfo.email);
  if (!user) {
    const userId = generateId();
    await createUser(db, userId, {
      email: userInfo.email,
      name: userInfo.name,
      avatar_url: userInfo.avatar_url,
    });
    user = { id: userId } as any;
  }

  await createOAuthAccount(
    db,
    generateId(),
    user!.id,
    provider,
    userInfo.provider_user_id,
    accessToken,
    refreshToken,
    expiresAt,
  );

  return user!.id;
}

function issueSessionToken(): { token: string; expiresAt: string } {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  const token = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
  const expiresAt = new Date(Date.now() + SESSION_TTL_MS).toISOString();
  return { token, expiresAt };
}

// ── Public Handlers ──

export async function googleRedirect(c: AppContext) {
  return c.redirect(googleAuthUrl(c));
}

export async function githubRedirect(c: AppContext) {
  return c.redirect(githubAuthUrl(c));
}

export async function oauthCallback(c: AppContext) {
  const { code, state } = c.req.query();
  if (!code || !state) return error(c, "Missing code or state", 400);

  const provider = state as OAuthProvider;
  const db = c.env.DB;

  try {
    let accessToken: string;
    let refreshToken: string | null = null;
    let expiresAt: string | null = null;
    let userInfo: OAuthUserInfo;

    if (provider === "google") {
      const tokens = await exchangeGoogleCode(c, code);
      accessToken = tokens.access_token;
      refreshToken = tokens.refresh_token ?? null;
      expiresAt = tokens.expires_in
        ? new Date(Date.now() + tokens.expires_in * 1000).toISOString()
        : null;
      userInfo = await getGoogleUser(accessToken);
    } else if (provider === "github") {
      const tokens = await exchangeGithubCode(c, code);
      accessToken = tokens.access_token;
      refreshToken = tokens.refresh_token ?? null;
      expiresAt = tokens.expires_in
        ? new Date(Date.now() + tokens.expires_in * 1000).toISOString()
        : null;
      userInfo = await getGithubUser(accessToken);
    } else {
      return error(c, `Unsupported provider: ${state}`, 400);
    }

    if (!userInfo.email) return error(c, "Could not retrieve email from provider", 400);

    const userId = await findOrCreateUser(db, provider, userInfo, accessToken, refreshToken, expiresAt);

    const session = issueSessionToken();
    await createSession(db, generateId(), userId, session.token, session.expiresAt);

    return success(c, {
      token: session.token,
      expires_at: session.expiresAt,
      user_id: userId,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "OAuth failed";
    return error(c, message, 500);
  }
}
