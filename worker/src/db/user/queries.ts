import type { User } from "../../schema";

export async function getUserById(db: D1Database, id: string): Promise<User | null> {
  const row = await db.prepare("SELECT * FROM users WHERE id = ?").bind(id).first();
  return row ? parseUserRow(row) : null;
}

export async function getUserByEmail(db: D1Database, email: string): Promise<User | null> {
  const row = await db.prepare("SELECT * FROM users WHERE email = ?").bind(email).first();
  return row ? parseUserRow(row) : null;
}

function parseUserRow(row: Record<string, unknown>): User {
  return {
    ...row,
    dietary_preferences: JSON.parse((row.dietary_preferences as string) || "[]"),
    allergies: JSON.parse((row.allergies as string) || "[]"),
    medical_conditions: JSON.parse((row.medical_conditions as string) || "[]"),
    locusgraph_bootstrapped: Boolean(row.locusgraph_bootstrapped),
  } as User;
}
