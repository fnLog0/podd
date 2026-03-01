import { describe, it, expect } from "vitest";
import {
  foodItemEvent,
  type FoodPayload,
} from "../../../locusgraph/foods/food-item.js";
import type { MealType } from "../../../locusgraph/foods/meal.js";

function makeFoodPayload(overrides?: Partial<FoodPayload>): FoodPayload {
  return {
    meal_type: "breakfast",
    items: [{ name: "oatmeal", quantity: 1, unit: "serving" }],
    macros: {
      calories: 150,
      protein_g: 5,
      carbs_g: 27,
      fat_g: 3,
      fiber_g: 4,
      sugar_g: 1,
    },
    logged_at: "2026-03-01T08:00:00Z",
    notes: "",
    ...overrides,
  };
}

describe("foodItemEvent", () => {
  it("generates correct context_id from meal_type and name", () => {
    const event = foodItemEvent({
      name: "oatmeal",
      meal_type: "breakfast",
      payload: makeFoodPayload(),
    });
    expect(event.context_id).toBe("breakfast:oatmeal");
  });

  it.each<MealType>(["breakfast", "lunch", "dinner", "snack"])(
    "maps %s to the correct meal context in extends",
    (mealType) => {
      const event = foodItemEvent({
        name: "test_food",
        meal_type: mealType,
        payload: makeFoodPayload({ meal_type: mealType }),
      });
      expect(event.extends).toEqual([`foods:${mealType}`]);
    },
  );

  it("sets event_kind to 'fact'", () => {
    const event = foodItemEvent({
      name: "eggs",
      meal_type: "breakfast",
      payload: makeFoodPayload(),
    });
    expect(event.event_kind).toBe("fact");
  });

  it("sets source to 'agent'", () => {
    const event = foodItemEvent({
      name: "eggs",
      meal_type: "breakfast",
      payload: makeFoodPayload(),
    });
    expect(event.source).toBe("agent");
  });

  it("wraps payload as TOON-encoded data_toon string", () => {
    const payload = makeFoodPayload();
    const event = foodItemEvent({
      name: "oatmeal",
      meal_type: "breakfast",
      payload,
    });
    expect(event.payload).toHaveProperty("data_toon");
    expect(typeof event.payload.data_toon).toBe("string");
    expect(event.payload.data_toon).toContain("oatmeal");
    expect(event.payload.data_toon).toContain("150");
  });

  it("includes related_to when provided", () => {
    const event = foodItemEvent({
      name: "eggs",
      meal_type: "breakfast",
      payload: makeFoodPayload(),
      related_to: ["session:my_session", "turn:my_session_t1"],
    });
    expect(event.related_to).toEqual([
      "session:my_session",
      "turn:my_session_t1",
    ]);
  });

  it("omits related_to when not provided", () => {
    const event = foodItemEvent({
      name: "eggs",
      meal_type: "breakfast",
      payload: makeFoodPayload(),
    });
    expect(event).not.toHaveProperty("related_to");
  });

  it("omits related_to when array is empty", () => {
    const event = foodItemEvent({
      name: "eggs",
      meal_type: "breakfast",
      payload: makeFoodPayload(),
      related_to: [],
    });
    expect(event).not.toHaveProperty("related_to");
  });
});
