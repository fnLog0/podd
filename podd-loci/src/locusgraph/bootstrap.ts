import { bootstrapUserContext, type UserEventPayload } from "./user.js";
import { bootstrapFoodContexts } from "./foods/index.js";
import { bootstrapVitalsContexts } from "./vitals/index.js";

export async function bootstrapUser(user: UserEventPayload) {
  await bootstrapUserContext(user);
  await bootstrapFoodContexts(user.name, user.user_id);
  await bootstrapVitalsContexts(user.name, user.user_id);
  console.log(`[bootstrap] done for ${user.name} (${user.user_id})`);
}
