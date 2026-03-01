// Context hierarchy for food tracking:
//
//   person:nasim_u123                    ← user (user.ts)
//     └── nasim_u123:foods               ← anchor (anchor.ts)
//           ├── foods:breakfast           ← meal (meal.ts)
//           │     ├── breakfast:oatmeal   ← food-item (food-item.ts)
//           │     └── breakfast:eggs
//           ├── foods:lunch
//           │     └── lunch:salad
//           ├── foods:dinner
//           │     └── dinner:steak
//           └── foods:snack
//                 └── snack:yogurt

export { anchorFoodContext, anchorFoodEventPayload } from "./anchor.js";
export { mealEventPayload, type MealType, type FoodEventInput } from "./meal.js";
export {
  foodItemEvent,
  type FoodItem,
  type Macros,
  type FoodPayload,
} from "./food-item.js";

import { anchorFoodEventPayload } from "./anchor.js";
import { mealEventPayload, type MealType } from "./meal.js";

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
    const mealEvent = mealEventPayload({ name, user_id, meal_type });
    const mealResult = await client.storeEvent({
      graph_id: GRAPH_ID,
      ...mealEvent,
      payload: { data: mealEvent.payload },
    });
    console.log(`[bootstrap] ${meal_type} context created:`, mealResult);
  }
}
