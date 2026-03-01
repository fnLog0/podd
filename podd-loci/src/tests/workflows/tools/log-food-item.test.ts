import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../../../locusgraph/client.js", () => ({
  getClient: () => ({
    storeEvent: vi.fn().mockResolvedValue({ event_id: "evt_mock_123" }),
  }),
  getGraphId: () => "mock-graph-id",
}));

vi.mock("../../../locusgraph/sessions/tracker.js", () => ({
  getCurrentSessionContextId: () => "session:test_session",
  getCurrentTurnContextId: () => "turn:test_session_t1",
}));

vi.mock("@langchain/openai", () => ({
  ChatOpenAI: class {
    bindTools() {
      return this;
    }
  },
}));

const mockLLMResponse = {
  content: JSON.stringify({
    meal_type: "breakfast",
    items: [
      { name: "scrambled_eggs", quantity: 2, unit: "piece" },
      { name: "green_tea", quantity: 1, unit: "cup" },
    ],
    macros: {
      calories: 200,
      protein_g: 14,
      carbs_g: 2,
      fat_g: 15,
      fiber_g: 0,
      sugar_g: 0,
    },
    logged_at: "2026-03-01T08:00:00Z",
    notes: "",
  }),
};

vi.mock("../../../prompts/index.js", () => ({
  foodParserPrompt: {
    pipe: () => ({
      invoke: vi.fn().mockResolvedValue(mockLLMResponse),
    }),
  },
}));

describe("logFoodItemTool", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("is defined with correct name and description", async () => {
    const { logFoodItemTool } = await import(
      "../../../workflows/tools/log-food-item.js"
    );
    expect(logFoodItemTool.name).toBe("log_food_item");
    expect(logFoodItemTool.description).toBeTruthy();
    expect(logFoodItemTool.description).toContain("Log");
  });

  it("returns success message with food details on valid input", async () => {
    const { logFoodItemTool } = await import(
      "../../../workflows/tools/log-food-item.js"
    );
    const result = await logFoodItemTool.invoke(
      "I had 2 scrambled eggs and green tea for breakfast",
    );
    expect(result).toContain("Logged breakfast");
    expect(result).toContain("scrambled_eggs");
    expect(result).toContain("200 cal");
    expect(result).toContain("evt_mock_123");
  });
});
