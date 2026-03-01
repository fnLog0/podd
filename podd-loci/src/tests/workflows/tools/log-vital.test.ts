import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../../../locusgraph/client.js", () => ({
  getClient: () => ({
    storeEvent: vi.fn().mockResolvedValue({ event_id: "evt_vital_123" }),
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
    vital_type: "blood_pressure",
    readings: [
      { label: "systolic", value: 120, unit: "mmHg" },
      { label: "diastolic", value: 80, unit: "mmHg" },
    ],
    measured_at: "2026-03-01T08:00:00Z",
    context: "resting",
    notes: "",
  }),
};

vi.mock("../../../prompts/index.js", () => ({
  vitalsParserPrompt: {
    pipe: () => ({
      invoke: vi.fn().mockResolvedValue(mockLLMResponse),
    }),
  },
}));

describe("logVitalTool", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("is defined with correct name and description", async () => {
    const { logVitalTool } = await import(
      "../../../workflows/tools/log-vital.js"
    );
    expect(logVitalTool.name).toBe("log_vital");
    expect(logVitalTool.description).toBeTruthy();
    expect(logVitalTool.description).toContain("vital");
  });

  it("returns success message with vital details on valid input", async () => {
    const { logVitalTool } = await import(
      "../../../workflows/tools/log-vital.js"
    );
    const result = await logVitalTool.invoke(
      "My blood pressure is 120/80",
    );
    expect(result).toContain("Logged blood_pressure");
    expect(result).toContain("systolic: 120 mmHg");
    expect(result).toContain("diastolic: 80 mmHg");
    expect(result).toContain("evt_vital_123");
  });
});
