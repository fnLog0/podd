import { Hono } from "hono";
import type { AppEnv } from "../types";
import { auth } from "../middleware";
import { textToSpeech, chatWithVoice, streamChatWithVoice } from "../handlers";

const tts = new Hono<AppEnv>();

tts.use("/*", auth);

tts.post("/", textToSpeech);
tts.post("/chat", chatWithVoice);
tts.post("/chat/stream", streamChatWithVoice);

export { tts };
