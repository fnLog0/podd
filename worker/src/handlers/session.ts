import type { AppContext } from "../types";
import { getSessionsByUserId, deleteSession, deleteUserSessions } from "../db/session";
import { success } from "../utils/responses";

export async function listSessions(c: AppContext) {
  const user = c.get("user");
  const sessions = await getSessionsByUserId(c.env.DB, user.id);

  const currentToken = c.get("session").token;
  const mapped = sessions.map((s) => ({
    id: s.id,
    expires_at: s.expires_at,
    created_at: s.created_at,
    current: s.token === currentToken,
  }));

  return success(c, mapped);
}

export async function logout(c: AppContext) {
  const session = c.get("session");
  await deleteSession(c.env.DB, session.token);
  return success(c, { logged_out: true });
}

export async function logoutAll(c: AppContext) {
  const user = c.get("user");
  await deleteUserSessions(c.env.DB, user.id);
  return success(c, { logged_out_all: true });
}
