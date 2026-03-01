import { Hono } from "hono";
import type { AppEnv } from "../types";
import { auth } from "../middleware";
import { chat, streamChat, getContextMap } from "../handlers";

const chatEndpoint = new Hono<AppEnv>();

chatEndpoint.use("/*", auth);

chatEndpoint.post("/", chat);
chatEndpoint.post("/stream", streamChat);
chatEndpoint.get("/context", getContextMap);

export { chatEndpoint };
