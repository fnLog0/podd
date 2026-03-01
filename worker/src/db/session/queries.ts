import type { Session } from "../../schema";

export async function getSessionByToken(db: D1Database, token: string): Promise<Session | null> {
  const row = await db
    .prepare("SELECT * FROM sessions WHERE token = ? AND expires_at > ?")
    .bind(token, new Date().toISOString())
    .first();
  return row as Session | null;
}

export async function getSessionsByUserId(db: D1Database, userId: string): Promise<Session[]> {
  const { results } = await db
    .prepare("SELECT * FROM sessions WHERE user_id = ? AND expires_at > ? ORDER BY created_at DESC")
    .bind(userId, new Date().toISOString())
    .all();
  return results as Session[];
}
