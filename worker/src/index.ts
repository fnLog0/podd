import { Hono } from "hono";
import type { AppEnv } from "./types";
import { cors } from "./middleware";
import { auth, user, session, health, dev, chatEndpoint, tts } from "./endpoints";

const app = new Hono<AppEnv>();

app.use("*", cors());

app.route("/health", health);
app.route("/auth", auth);
app.route("/dev", dev);
app.route("/me", user);
app.route("/sessions", session);
app.route("/chat", chatEndpoint);
app.route("/tts", tts);

export default app;
