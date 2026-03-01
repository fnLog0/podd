import { Hono } from "hono";
import type { AppEnv } from "../types";
import { googleRedirect, githubRedirect, oauthCallback } from "../handlers";

const auth = new Hono<AppEnv>();

auth.get("/google", googleRedirect);
auth.get("/github", githubRedirect);
auth.get("/callback", oauthCallback);

export { auth };
