import { describe, it, expect } from "vitest";
import { categorizeContexts } from "../../../workflows/tools/context-formatter.js";

describe("categorizeContexts", () => {
  describe("user contexts", () => {
    it("categorizes person: contexts under user_contexts as TOON", () => {
      const result = categorizeContexts({
        contexts: [{ context_id: "person:nasim_u123" }],
      });
      expect(result.user_contexts).toContain("person:nasim_u123");
      expect(result.user_contexts).toContain("user");
    });

    it("returns fallback when no user contexts exist", () => {
      const result = categorizeContexts({ contexts: [] });
      expect(result.user_contexts).toBe("No user contexts available.");
    });

    it("lists multiple user contexts", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "person:nasim_u123" },
          { context_id: "person:alice_u999" },
        ],
      });
      expect(result.user_contexts).toContain("person:nasim_u123");
      expect(result.user_contexts).toContain("person:alice_u999");
    });
  });

  describe("food contexts", () => {
    it("categorizes anchor, meals, and items under food_contexts as TOON", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "nasim_u123:foods" },
          { context_id: "foods:breakfast" },
          { context_id: "foods:lunch" },
          { context_id: "breakfast:scrambled_eggs" },
          { context_id: "breakfast:toast" },
          { context_id: "lunch:salad" },
        ],
      });
      expect(result.food_contexts).toContain("nasim_u123:foods");
      expect(result.food_contexts).toContain("foods:breakfast");
      expect(result.food_contexts).toContain("foods:lunch");
      expect(result.food_contexts).toContain("breakfast:scrambled_eggs");
      expect(result.food_contexts).toContain("breakfast:toast");
      expect(result.food_contexts).toContain("lunch:salad");
    });

    it("structures food hierarchy with anchors, meals, and items", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "nasim_u123:foods" },
          { context_id: "foods:breakfast" },
          { context_id: "breakfast:eggs" },
        ],
      });
      expect(result.food_contexts).toContain("nasim_u123:foods");
      expect(result.food_contexts).toContain("foods:breakfast");
      expect(result.food_contexts).toContain("breakfast:eggs");
      expect(result.food_contexts).toContain("meal");
      expect(result.food_contexts).toContain("item");
    });

    it("returns fallback when no food contexts exist", () => {
      const result = categorizeContexts({ contexts: [] });
      expect(result.food_contexts).toBe("No food contexts available.");
    });

    it("handles all four meal types", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "nasim_u123:foods" },
          { context_id: "foods:breakfast" },
          { context_id: "foods:lunch" },
          { context_id: "foods:dinner" },
          { context_id: "foods:snack" },
          { context_id: "dinner:steak" },
          { context_id: "snack:yogurt" },
        ],
      });
      expect(result.food_contexts).toContain("foods:breakfast");
      expect(result.food_contexts).toContain("foods:lunch");
      expect(result.food_contexts).toContain("foods:dinner");
      expect(result.food_contexts).toContain("foods:snack");
      expect(result.food_contexts).toContain("dinner:steak");
      expect(result.food_contexts).toContain("snack:yogurt");
    });
  });

  describe("session contexts", () => {
    it("categorizes anchor, sessions, and turns under session_contexts as TOON", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "nasim_u123:sessions" },
          { context_id: "session:breakfast_eggs_01032026" },
          { context_id: "turn:breakfast_eggs_01032026_t1" },
          { context_id: "turn:breakfast_eggs_01032026_t2" },
        ],
      });
      expect(result.session_contexts).toContain("nasim_u123:sessions");
      expect(result.session_contexts).toContain(
        "session:breakfast_eggs_01032026",
      );
      expect(result.session_contexts).toContain(
        "turn:breakfast_eggs_01032026_t1",
      );
      expect(result.session_contexts).toContain(
        "turn:breakfast_eggs_01032026_t2",
      );
    });

    it("structures session hierarchy with sessions and turns", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "nasim_u123:sessions" },
          { context_id: "session:my_chat_01032026" },
          { context_id: "turn:my_chat_01032026_t1" },
        ],
      });
      expect(result.session_contexts).toContain("nasim_u123:sessions");
      expect(result.session_contexts).toContain("session:my_chat_01032026");
      expect(result.session_contexts).toContain("turn:my_chat_01032026_t1");
    });

    it("returns fallback when no session contexts exist", () => {
      const result = categorizeContexts({ contexts: [] });
      expect(result.session_contexts).toBe("No session contexts available.");
    });

    it("groups turns to the correct session when multiple sessions exist", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "nasim_u123:sessions" },
          { context_id: "session:chat_a_01032026" },
          { context_id: "session:chat_b_01032026" },
          { context_id: "turn:chat_a_01032026_t1" },
          { context_id: "turn:chat_b_01032026_t1" },
          { context_id: "turn:chat_b_01032026_t2" },
        ],
      });
      expect(result.session_contexts).toContain("session:chat_a_01032026");
      expect(result.session_contexts).toContain("session:chat_b_01032026");
      expect(result.session_contexts).toContain("turn:chat_a_01032026_t1");
      expect(result.session_contexts).toContain("turn:chat_b_01032026_t1");
      expect(result.session_contexts).toContain("turn:chat_b_01032026_t2");
    });
  });

  describe("vitals contexts", () => {
    it("categorizes anchor, vital types, and readings under vitals_contexts", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "nasim_u123:vitals" },
          { context_id: "vitals:blood_pressure" },
          { context_id: "vitals:heart_rate" },
          { context_id: "blood_pressure:120_80_01032026" },
          { context_id: "heart_rate:72bpm_01032026" },
        ],
      });
      expect(result.vitals_contexts).toContain("nasim_u123:vitals");
      expect(result.vitals_contexts).toContain("vitals:blood_pressure");
      expect(result.vitals_contexts).toContain("vitals:heart_rate");
      expect(result.vitals_contexts).toContain("blood_pressure:120_80_01032026");
      expect(result.vitals_contexts).toContain("heart_rate:72bpm_01032026");
    });

    it("structures vitals hierarchy with types and readings", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "nasim_u123:vitals" },
          { context_id: "vitals:weight" },
          { context_id: "weight:70kg_01032026" },
        ],
      });
      expect(result.vitals_contexts).toContain("nasim_u123:vitals");
      expect(result.vitals_contexts).toContain("vitals:weight");
      expect(result.vitals_contexts).toContain("weight:70kg_01032026");
      expect(result.vitals_contexts).toContain("vital_type");
      expect(result.vitals_contexts).toContain("reading");
    });

    it("returns fallback when no vitals contexts exist", () => {
      const result = categorizeContexts({ contexts: [] });
      expect(result.vitals_contexts).toBe("No vitals contexts available.");
    });

    it("handles all six vital types", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "nasim_u123:vitals" },
          { context_id: "vitals:blood_pressure" },
          { context_id: "vitals:heart_rate" },
          { context_id: "vitals:weight" },
          { context_id: "vitals:blood_sugar" },
          { context_id: "vitals:temperature" },
          { context_id: "vitals:oxygen_saturation" },
        ],
      });
      expect(result.vitals_contexts).toContain("vitals:blood_pressure");
      expect(result.vitals_contexts).toContain("vitals:heart_rate");
      expect(result.vitals_contexts).toContain("vitals:weight");
      expect(result.vitals_contexts).toContain("vitals:blood_sugar");
      expect(result.vitals_contexts).toContain("vitals:temperature");
      expect(result.vitals_contexts).toContain("vitals:oxygen_saturation");
    });
  });

  describe("mixed contexts", () => {
    it("separates all context types correctly", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "person:nasim_u123" },
          { context_id: "nasim_u123:foods" },
          { context_id: "foods:breakfast" },
          { context_id: "breakfast:eggs" },
          { context_id: "nasim_u123:vitals" },
          { context_id: "vitals:blood_pressure" },
          { context_id: "blood_pressure:120_80_01032026" },
          { context_id: "nasim_u123:sessions" },
          { context_id: "session:test_01032026" },
          { context_id: "turn:test_01032026_t1" },
        ],
      });

      expect(result.user_contexts).toContain("person:nasim_u123");
      expect(result.user_contexts).not.toContain("foods:breakfast");
      expect(result.user_contexts).not.toContain("vitals:blood_pressure");
      expect(result.user_contexts).not.toContain("session:test");

      expect(result.food_contexts).toContain("foods:breakfast");
      expect(result.food_contexts).not.toContain("person:");
      expect(result.food_contexts).not.toContain("vitals:");
      expect(result.food_contexts).not.toContain("session:");

      expect(result.vitals_contexts).toContain("vitals:blood_pressure");
      expect(result.vitals_contexts).not.toContain("person:");
      expect(result.vitals_contexts).not.toContain("foods:");
      expect(result.vitals_contexts).not.toContain("session:");

      expect(result.session_contexts).toContain("session:test_01032026");
      expect(result.session_contexts).not.toContain("person:");
      expect(result.session_contexts).not.toContain("foods:");
      expect(result.session_contexts).not.toContain("vitals:");
    });
  });

  describe("TOON output format", () => {
    it("produces non-JSON output for contexts", () => {
      const result = categorizeContexts({
        contexts: [
          { context_id: "person:nasim_u123" },
          { context_id: "foods:breakfast" },
        ],
      });
      expect(() => JSON.parse(result.user_contexts)).toThrow();
      expect(() => JSON.parse(result.food_contexts)).toThrow();
    });

    it("is more compact than JSON equivalent", () => {
      const contexts = {
        contexts: [
          { context_id: "nasim_u123:foods" },
          { context_id: "foods:breakfast" },
          { context_id: "foods:lunch" },
          { context_id: "breakfast:eggs" },
          { context_id: "lunch:salad" },
        ],
      };
      const toonResult = categorizeContexts(contexts);
      const jsonEquivalent = JSON.stringify(contexts, null, 2);
      expect(toonResult.food_contexts.length).toBeLessThan(jsonEquivalent.length);
    });
  });

  describe("raw input formats", () => {
    it("handles raw array input", () => {
      const result = categorizeContexts([
        { context_id: "person:nasim_u123" },
        { context_id: "foods:breakfast" },
      ]);
      expect(result.user_contexts).toContain("person:nasim_u123");
      expect(result.food_contexts).toContain("foods:breakfast");
    });

    it("handles null/undefined gracefully", () => {
      const result = categorizeContexts(null);
      expect(result.user_contexts).toBe("No user contexts available.");
      expect(result.food_contexts).toBe("No food contexts available.");
      expect(result.vitals_contexts).toBe("No vitals contexts available.");
      expect(result.session_contexts).toBe("No session contexts available.");
    });

    it("handles empty object", () => {
      const result = categorizeContexts({});
      expect(result.user_contexts).toBe("No user contexts available.");
      expect(result.food_contexts).toBe("No food contexts available.");
      expect(result.vitals_contexts).toBe("No vitals contexts available.");
      expect(result.session_contexts).toBe("No session contexts available.");
    });

    it("handles { items: [...] } format", () => {
      const result = categorizeContexts({
        items: [
          { context_id: "person:nasim_u123" },
          { context_id: "foods:breakfast" },
        ],
      });
      expect(result.user_contexts).toContain("person:nasim_u123");
      expect(result.food_contexts).toContain("foods:breakfast");
    });

    it("handles { results: [...] } format", () => {
      const result = categorizeContexts({
        results: [{ context_id: "session:test_01032026" }],
      });
      expect(result.session_contexts).toContain("session:test_01032026");
    });

    it("handles objects with id instead of context_id", () => {
      const result = categorizeContexts([
        { id: "person:nasim_u123" },
        { id: "foods:breakfast" },
      ]);
      expect(result.user_contexts).toContain("person:nasim_u123");
      expect(result.food_contexts).toContain("foods:breakfast");
    });
  });
});
