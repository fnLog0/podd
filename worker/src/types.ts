import { Context } from "hono";
import type { User, Session } from "./schema";

export type AppEnv = {
  Bindings: Env;
  Variables: { user: User; session: Session };
};

export type AppContext = Context<AppEnv>;
