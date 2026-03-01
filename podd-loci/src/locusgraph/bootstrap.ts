import { bootstrapUserContext, userPersonContext, type UserEventPayload } from "./user.js";
import { getClient, getGraphId } from "./client.js";
import { bootstrapFoodContexts } from "./foods/index.js";
import { bootstrapVitalsContexts } from "./vitals/index.js";
import { bootstrapSessionsContexts } from "./sessions/index.js";

async function userExists(name: string, user_id: string): Promise<boolean> {
  try {
    const contextId = userPersonContext(name, user_id);
    const result = await getClient().listContexts({
      graphId: getGraphId(),
      context_name: contextId,
      limit: 1,
    });
    const obj = result as unknown as Record<string, unknown>;
    const contexts = obj.contexts ?? obj.items ?? [];
    return Array.isArray(contexts) && contexts.length > 0;
  } catch {
    return false;
  }
}

export interface BootstrapOptions {
  skipIfExists?: boolean;
}

export async function bootstrapUser(
  user: UserEventPayload,
  options: BootstrapOptions = {},
) {
  if (options.skipIfExists) {
    const exists = await userExists(user.name, user.user_id);
    if (exists) {
      console.log(`[bootstrap] skipped — user ${user.name} (${user.user_id}) already exists`);
      return;
    }
  }

  await bootstrapUserContext(user);
  await bootstrapFoodContexts(user.name, user.user_id);
  await bootstrapVitalsContexts(user.name, user.user_id);
  await bootstrapSessionsContexts(user.name, user.user_id);
  console.log(`[bootstrap] done for ${user.name} (${user.user_id})`);
}
