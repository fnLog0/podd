import type { UserCreate, UserUpdate } from "../../schema";

export async function createUser(db: D1Database, id: string, data: UserCreate) {
  const now = new Date().toISOString();
  await db
    .prepare(
      `INSERT INTO users (id, email, name, avatar_url, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?)`,
    )
    .bind(id, data.email, data.name, data.avatar_url ?? null, now, now)
    .run();
}

export async function updateUser(db: D1Database, id: string, data: UserUpdate) {
  const fields: string[] = [];
  const values: unknown[] = [];

  if (data.name !== undefined) { fields.push("name = ?"); values.push(data.name); }
  if (data.avatar_url !== undefined) { fields.push("avatar_url = ?"); values.push(data.avatar_url); }
  if (data.age !== undefined) { fields.push("age = ?"); values.push(data.age); }
  if (data.gender !== undefined) { fields.push("gender = ?"); values.push(data.gender); }
  if (data.height_cm !== undefined) { fields.push("height_cm = ?"); values.push(data.height_cm); }
  if (data.weight_kg !== undefined) { fields.push("weight_kg = ?"); values.push(data.weight_kg); }
  if (data.activity_level !== undefined) { fields.push("activity_level = ?"); values.push(data.activity_level); }
  if (data.dietary_preferences !== undefined) { fields.push("dietary_preferences = ?"); values.push(JSON.stringify(data.dietary_preferences)); }
  if (data.allergies !== undefined) { fields.push("allergies = ?"); values.push(JSON.stringify(data.allergies)); }
  if (data.medical_conditions !== undefined) { fields.push("medical_conditions = ?"); values.push(JSON.stringify(data.medical_conditions)); }
  if (data.daily_calorie_goal !== undefined) { fields.push("daily_calorie_goal = ?"); values.push(data.daily_calorie_goal); }

  if (fields.length === 0) return;

  fields.push("updated_at = ?");
  values.push(new Date().toISOString());
  values.push(id);

  await db
    .prepare(`UPDATE users SET ${fields.join(", ")} WHERE id = ?`)
    .bind(...values)
    .run();
}

export async function markLocusgraphBootstrapped(db: D1Database, id: string) {
  await db
    .prepare("UPDATE users SET locusgraph_bootstrapped = 1, updated_at = ? WHERE id = ?")
    .bind(new Date().toISOString(), id)
    .run();
}
