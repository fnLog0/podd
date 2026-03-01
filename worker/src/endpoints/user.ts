import { Hono } from "hono";
import type { AppEnv } from "../types";
import { auth } from "../middleware";
import { getMe, updateMe, deleteMe, bootstrapMe } from "../handlers";

const user = new Hono<AppEnv>();

user.use("/*", auth);

user.get("/", getMe);
user.patch("/", updateMe);
user.delete("/", deleteMe);
user.post("/bootstrap", bootstrapMe);

export { user };
