import { describe, it, expect } from "vitest";
import {
  anchorFoodContext,
  anchorFoodEventPayload,
} from "../../../locusgraph/foods/anchor.js";

describe("anchorFoodContext", () => {
  it("returns correct anchor context id", () => {
    expect(anchorFoodContext("nasim", "u123")).toBe("nasim_u123:foods");
  });

  it("handles different name/id combinations", () => {
    expect(anchorFoodContext("alice", "u999")).toBe("alice_u999:foods");
  });
});

describe("anchorFoodEventPayload", () => {
  it("returns correct context_id", () => {
    const event = anchorFoodEventPayload({ name: "nasim", user_id: "u123" });
    expect(event.context_id).toBe("nasim_u123:foods");
  });

  it("sets event_kind to 'fact'", () => {
    const event = anchorFoodEventPayload({ name: "nasim", user_id: "u123" });
    expect(event.event_kind).toBe("fact");
  });

  it("sets source to 'system'", () => {
    const event = anchorFoodEventPayload({ name: "nasim", user_id: "u123" });
    expect(event.source).toBe("system");
  });

  it("extends the user person context", () => {
    const event = anchorFoodEventPayload({ name: "nasim", user_id: "u123" });
    expect(event.extends).toEqual(["person:nasim_u123"]);
  });

  it("payload references all meal-type contexts", () => {
    const event = anchorFoodEventPayload({ name: "nasim", user_id: "u123" });
    expect(event.payload).toContain("foods:breakfast");
    expect(event.payload).toContain("foods:lunch");
    expect(event.payload).toContain("foods:dinner");
    expect(event.payload).toContain("foods:snack");
  });
});
