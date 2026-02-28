// Context hierarchy for food tracking:
//
//   person:nasim_u123                    ← user (user.ts)
//     └── nasim_u123:foods               ← anchor (anchor.ts)
//           ├── foods:breakfast           ← child (child.ts)
//           │     ├── breakfast:oatmeal   ← dynamic-child (dynamic-child.ts)
//           │     └── breakfast:eggs
//           ├── foods:lunch
//           │     └── lunch:salad
//           ├── foods:dinner
//           │     └── dinner:steak
//           └── foods:snack
//                 └── snack:yogurt

export { anchorFoodContext, anchorFoodEventPayload } from "./anchor.js";
export { childEventPayload, type MealType, type FoodEventInput } from "./child.js";
export {
  dynamicChildEvent,
  type FoodItem,
  type Macros,
  type FoodPayload,
} from "./dynamic-child.js";

import { anchorFoodEventPayload } from "./anchor.js";
import { childEventPayload, type MealType } from "./child.js";

const MEAL_TYPES: MealType[] = ["breakfast", "lunch", "dinner", "snack"];

export async function bootstrapFoodContexts(name: string, user_id: string) {
  const { getClient, getGraphId } = await import("../client.js");
  const client = getClient();
  const GRAPH_ID = getGraphId();

  const anchorEvent = anchorFoodEventPayload({ name, user_id });
  const anchorResult = await client.storeEvent({
    graph_id: GRAPH_ID,
    ...anchorEvent,
    payload: { data: anchorEvent.payload },
  });
  console.log(`[bootstrap] food anchor created:`, anchorResult);

  for (const meal_type of MEAL_TYPES) {
    const childEvent = childEventPayload({ name, user_id, meal_type });
    const childResult = await client.storeEvent({
      graph_id: GRAPH_ID,
      ...childEvent,
      payload: { data: childEvent.payload },
    });
    console.log(`[bootstrap] ${meal_type} context created:`, childResult);
  }
}
