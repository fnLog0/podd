// Meal-type contexts. One per meal category.
// Extends the user's anchor food context.
//
// context_id examples: "foods:breakfast"
//                      "foods:lunch"
//                      "foods:dinner"
//                      "foods:snack"
// extends:            ["nasim_u123:foods"]
//
// Graph:  nasim_u123:foods  <──  foods:breakfast  ──>  breakfast:oatmeal
//                           <──  foods:lunch      ──>  lunch:grilled_chicken
//                           <──  foods:dinner     ──>  dinner:pasta
//                           <──  foods:snack      ──>  snack:almonds

import { anchorFoodContext } from "./anchor.js";

export type MealType = "breakfast" | "lunch" | "dinner" | "snack";

export interface FoodEventInput {
  name: string;
  user_id: string;
  meal_type: MealType;
}

export function mealEventPayload(event: FoodEventInput) {
  return {
    context_id: `foods:${event.meal_type}`,
    event_kind: "fact" as const,
    source: "system" as const,
    payload: `this memories refer for ${event.meal_type}:{llm_generated_name} contexts for future events`,
    extends: [anchorFoodContext(event.name, event.user_id)],
  };
}
