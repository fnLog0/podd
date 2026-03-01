import { Hono } from "hono";
import type { AppEnv } from "../types";
import { devLogin } from "../handlers";

const dev = new Hono<AppEnv>();

dev.post("/login", devLogin);

export { dev };
