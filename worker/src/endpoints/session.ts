import { Hono } from "hono";
import type { AppEnv } from "../types";
import { auth } from "../middleware";
import { listSessions, logout, logoutAll } from "../handlers";

const session = new Hono<AppEnv>();

session.use("/*", auth);

session.get("/", listSessions);
session.post("/logout", logout);
session.post("/logout/all", logoutAll);

export { session };
