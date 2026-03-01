import { describe, it, expect } from "vitest";
import {
  mealEventPayload,
  type MealType,
  type FoodEventInput,
} from "../../../locusgraph/foods/meal.js";

const mealTypes: MealType[] = ["breakfast", "lunch", "dinner", "snack"];

describe("mealEventPayload", () => {
  it.each(mealTypes)("generates correct context_id for %s", (mealType) => {
    const input: FoodEventInput = {
      name: "nasim",
      user_id: "u123",
      meal_type: mealType,
    };
    const event = mealEventPayload(input);
    expect(event.context_id).toBe(`foods:${mealType}`);
  });

  it("sets event_kind to 'fact'", () => {
    const event = mealEventPayload({
      name: "nasim",
      user_id: "u123",
      meal_type: "breakfast",
    });
    expect(event.event_kind).toBe("fact");
  });

  it("sets source to 'system'", () => {
    const event = mealEventPayload({
      name: "nasim",
      user_id: "u123",
      meal_type: "lunch",
    });
    expect(event.source).toBe("system");
  });

  it("extends the anchor food context", () => {
    const event = mealEventPayload({
      name: "nasim",
      user_id: "u123",
      meal_type: "dinner",
    });
    expect(event.extends).toEqual(["nasim_u123:foods"]);
  });

  it("extends correct anchor for different users", () => {
    const event = mealEventPayload({
      name: "alice",
      user_id: "u999",
      meal_type: "snack",
    });
    expect(event.extends).toEqual(["alice_u999:foods"]);
  });

  it("payload contains the meal type name", () => {
    const event = mealEventPayload({
      name: "nasim",
      user_id: "u123",
      meal_type: "breakfast",
    });
    expect(event.payload).toContain("breakfast");
  });
});
