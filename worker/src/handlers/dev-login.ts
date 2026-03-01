import type { AppContext } from "../types";
import { getUserByEmail, createUser } from "../db/user";
import { createSession } from "../db/session";
import { generateId } from "../utils/helpers";
import { success, error } from "../utils/responses";

const SESSION_TTL_MS = 30 * 24 * 60 * 60 * 1000;

export async function devLogin(c: AppContext) {
  const body = await c.req.json().catch(() => ({}));
  const email = (body as Record<string, unknown>).email as string | undefined;
  const name = (body as Record<string, unknown>).name as string | undefined;

  if (!email) return error(c, "email is required", 400);

  const db = c.env.DB;

  let user = await getUserByEmail(db, email);
  if (!user) {
    if (!name) return error(c, "name is required for new users", 400);
    const userId = generateId();
    await createUser(db, userId, { email, name });
    user = { id: userId, email, name } as any;
  }

  const token = Array.from(crypto.getRandomValues(new Uint8Array(32)), (b) =>
    b.toString(16).padStart(2, "0"),
  ).join("");
  const expiresAt = new Date(Date.now() + SESSION_TTL_MS).toISOString();

  await createSession(db, generateId(), user!.id, token, expiresAt);

  return success(c, {
    token,
    expires_at: expiresAt,
    user_id: user!.id,
    email: user!.email,
    name: user!.name,
  });
}
