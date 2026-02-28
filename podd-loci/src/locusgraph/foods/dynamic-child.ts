// Dynamic child — the actual food item logged by the user.
// Extends the meal-type child context.
//
// context_id examples: "breakfast:oatmeal"
//                      "lunch:grilled_chicken"
//                      "dinner:pasta"
//                      "snack:almonds"
// extends:            ["foods:breakfast"]  (or lunch/dinner/snack)
//
// Full chain:
//   person:nasim_u123
//     └── nasim_u123:foods
//           ├── foods:breakfast
//           │     ├── breakfast:oatmeal       ← this level
//           │     └── breakfast:scrambled_eggs
//           ├── foods:lunch
//           │     └── lunch:grilled_chicken
//           ├── foods:dinner
//           │     └── dinner:pasta
//           └── foods:snack
//                 └── snack:almonds

import type { MealType } from "./child.js";

const breakfastContextId = `foods:breakfast`;
const lunchContextId = `foods:lunch`;
const dinnerContextId = `foods:dinner`;
const snackContextId = `foods:snack`;

export interface FoodItem {
  name: string;
  quantity: number;
  unit: "g" | "mg" | "ml" | "oz" | "cup" | "tbsp" | "tsp" | "piece" | "serving";
}

export interface Macros {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
  sugar_g: number;
}

export interface FoodPayload {
  meal_type: MealType;
  items: FoodItem[];
  macros: Macros;
  logged_at: string;
  notes: string;
}

interface DynamicChildEvent {
  name: string;
  meal_type: MealType;
  payload: FoodPayload;
}

function getChildContextId(type: MealType): string {
  switch (type) {
    case "breakfast":
      return breakfastContextId;
    case "lunch":
      return lunchContextId;
    case "dinner":
      return dinnerContextId;
    case "snack":
      return snackContextId;
    default:
      throw new Error(`Unknown meal type: ${type}`);
  }
}

export function dynamicChildEvent(event: DynamicChildEvent) {
  return {
    context_id: `${event.meal_type}:${event.name}`,
    event_kind: "fact" as const,
    source: "agent" as const,
    payload: event.payload,
    extends: [getChildContextId(event.meal_type)],
  };
}
