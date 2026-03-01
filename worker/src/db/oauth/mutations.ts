import type { OAuthProvider } from "../../schema";

export async function createOAuthAccount(
  db: D1Database,
  id: string,
  userId: string,
  provider: OAuthProvider,
  providerUserId: string,
  accessToken: string,
  refreshToken: string | null,
  expiresAt: string | null,
) {
  await db
    .prepare(
      `INSERT INTO oauth_accounts (id, user_id, provider, provider_user_id, access_token, refresh_token, expires_at, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    )
    .bind(id, userId, provider, providerUserId, accessToken, refreshToken, expiresAt, new Date().toISOString())
    .run();
}

export async function updateOAuthTokens(
  db: D1Database,
  provider: OAuthProvider,
  providerUserId: string,
  accessToken: string,
  refreshToken: string | null,
  expiresAt: string | null,
) {
  await db
    .prepare(
      `UPDATE oauth_accounts SET access_token = ?, refresh_token = ?, expires_at = ?
       WHERE provider = ? AND provider_user_id = ?`,
    )
    .bind(accessToken, refreshToken, expiresAt, provider, providerUserId)
    .run();
}

export async function deleteOAuthAccount(db: D1Database, id: string) {
  await db.prepare("DELETE FROM oauth_accounts WHERE id = ?").bind(id).run();
}

export async function deleteOAuthAccountsByUserId(db: D1Database, userId: string) {
  await db.prepare("DELETE FROM oauth_accounts WHERE user_id = ?").bind(userId).run();
}
