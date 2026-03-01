import { createMiddleware } from "hono/factory";
import type { AppEnv } from "../types";
import { getSessionByToken } from "../db/session";
import { getUserById } from "../db/user";

export const auth = createMiddleware<AppEnv>(async (c, next) => {
  const header = c.req.header("Authorization");
  if (!header?.startsWith("Bearer ")) {
    return c.json({ success: false, error: "Missing or invalid Authorization header" }, 401);
  }

  const token = header.slice(7);
  const db = c.env.DB;

  const session = await getSessionByToken(db, token);
  if (!session) {
    return c.json({ success: false, error: "Invalid or expired session" }, 401);
  }

  const user = await getUserById(db, session.user_id);
  if (!user) {
    return c.json({ success: false, error: "User not found" }, 401);
  }

  c.set("user", user);
  c.set("session", session);

  await next();
});
