import type { AppContext } from "../types";
import { UserUpdate } from "../schema";
import { getUserById, updateUser, markLocusgraphBootstrapped } from "../db/user";
import { deleteUserSessions } from "../db/session";
import { deleteOAuthAccountsByUserId } from "../db/oauth";
import { success, error } from "../utils/responses";

export async function getMe(c: AppContext) {
  return success(c, c.get("user"));
}

export async function updateMe(c: AppContext) {
  const body = await c.req.json();
  const parsed = UserUpdate.safeParse(body);
  if (!parsed.success) {
    return error(c, parsed.error.issues.map((i) => i.message).join(", "), 400);
  }

  const user = c.get("user");
  const db = c.env.DB;

  await updateUser(db, user.id, parsed.data);

  const updated = await getUserById(db, user.id);
  return success(c, updated);
}

export async function deleteMe(c: AppContext) {
  const user = c.get("user");
  const db = c.env.DB;

  await deleteOAuthAccountsByUserId(db, user.id);
  await deleteUserSessions(db, user.id);
  await db.prepare("DELETE FROM users WHERE id = ?").bind(user.id).run();

  return success(c, { deleted: true });
}

export async function bootstrapMe(c: AppContext) {
  const user = c.get("user");
  const db = c.env.DB;

  if (user.locusgraph_bootstrapped) {
    return success(c, { bootstrapped: true, skipped: true });
  }

  const { bootstrapUser } = await import("podd-loci");

  await bootstrapUser(
    {
      name: user.name,
      user_id: user.id,
      email: user.email,
      age: user.age ?? undefined,
      gender: user.gender ?? undefined,
      height_cm: user.height_cm ?? undefined,
      weight_kg: user.weight_kg ?? undefined,
      activity_level: user.activity_level ?? undefined,
      dietary_preferences: user.dietary_preferences,
      allergies: user.allergies,
      medical_conditions: user.medical_conditions,
      daily_calorie_goal: user.daily_calorie_goal ?? undefined,
    },
    { skipIfExists: true },
  );

  await markLocusgraphBootstrapped(db, user.id);

  return success(c, { bootstrapped: true, skipped: false });
}
