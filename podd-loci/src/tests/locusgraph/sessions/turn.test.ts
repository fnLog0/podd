import { describe, it, expect } from "vitest";
import {
  turnContext,
  dynamicTurnEvent,
  type TurnPayload,
} from "../../../locusgraph/sessions/turn.js";

function makeTurnPayload(overrides?: Partial<TurnPayload>): TurnPayload {
  return {
    turn_number: 1,
    session_title: "breakfast_eggs_01032026",
    user_id: "u123",
    user_message: "I had eggs for breakfast",
    ai_response: "Logged your breakfast!",
    tool_calls: [],
    message_count: 2,
    logged_at: "2026-03-01T08:00:00Z",
    ...overrides,
  };
}

describe("turnContext", () => {
  it("returns correct turn context id", () => {
    expect(turnContext("breakfast_eggs_01032026", 1)).toBe(
      "turn:breakfast_eggs_01032026_t1",
    );
  });

  it("handles different turn numbers", () => {
    expect(turnContext("my_session", 3)).toBe("turn:my_session_t3");
    expect(turnContext("my_session", 10)).toBe("turn:my_session_t10");
  });
});

describe("dynamicTurnEvent", () => {
  it("returns correct context_id", () => {
    const event = dynamicTurnEvent({
      session_title: "breakfast_eggs_01032026",
      turn_number: 1,
      payload: makeTurnPayload(),
    });
    expect(event.context_id).toBe("turn:breakfast_eggs_01032026_t1");
  });

  it("sets event_kind to 'action'", () => {
    const event = dynamicTurnEvent({
      session_title: "breakfast_eggs_01032026",
      turn_number: 1,
      payload: makeTurnPayload(),
    });
    expect(event.event_kind).toBe("action");
  });

  it("sets source to 'agent'", () => {
    const event = dynamicTurnEvent({
      session_title: "breakfast_eggs_01032026",
      turn_number: 1,
      payload: makeTurnPayload(),
    });
    expect(event.source).toBe("agent");
  });

  it("extends the parent session context", () => {
    const event = dynamicTurnEvent({
      session_title: "breakfast_eggs_01032026",
      turn_number: 2,
      payload: makeTurnPayload({ turn_number: 2 }),
    });
    expect(event.extends).toEqual(["session:breakfast_eggs_01032026"]);
  });

  it("wraps turn payload as TOON-encoded data_toon string", () => {
    const payload = makeTurnPayload({
      tool_calls: [
        {
          tool_name: "log_food",
          tool_input: { food: "eggs" },
          tool_output: "Logged!",
        },
      ],
    });
    const event = dynamicTurnEvent({
      session_title: "breakfast_eggs_01032026",
      turn_number: 1,
      payload,
    });
    expect(event.payload).toHaveProperty("data_toon");
    expect(typeof event.payload.data_toon).toBe("string");
    expect(event.payload.data_toon).toContain("log_food");
    expect(event.payload.data_toon).toContain("eggs");
    expect(event.payload.data_toon).toContain("breakfast_eggs_01032026");
  });
});
