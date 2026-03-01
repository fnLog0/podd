import { describe, it, expect } from "vitest";
import {
  sessionContext,
  sessionEventPayload,
} from "../../../locusgraph/sessions/session.js";

describe("sessionContext", () => {
  it("returns correct session context id", () => {
    expect(sessionContext("breakfast_eggs_01032026")).toBe(
      "session:breakfast_eggs_01032026",
    );
  });

  it("handles various title formats", () => {
    expect(sessionContext("protein_check_01032026")).toBe(
      "session:protein_check_01032026",
    );
    expect(sessionContext("a")).toBe("session:a");
  });
});

describe("sessionEventPayload", () => {
  const input = {
    name: "nasim",
    user_id: "u123",
    session_title: "breakfast_eggs_green_tea_01032026",
  };

  it("returns correct context_id", () => {
    const event = sessionEventPayload(input);
    expect(event.context_id).toBe(
      "session:breakfast_eggs_green_tea_01032026",
    );
  });

  it("sets event_kind to 'fact'", () => {
    const event = sessionEventPayload(input);
    expect(event.event_kind).toBe("fact");
  });

  it("sets source to 'system'", () => {
    const event = sessionEventPayload(input);
    expect(event.source).toBe("system");
  });

  it("extends the user's sessions anchor", () => {
    const event = sessionEventPayload(input);
    expect(event.extends).toEqual(["nasim_u123:sessions"]);
  });

  it("payload contains human-readable session title", () => {
    const event = sessionEventPayload(input);
    expect(event.payload).toContain("breakfast eggs green tea 01032026");
  });

  it("payload references turn naming convention", () => {
    const event = sessionEventPayload(input);
    expect(event.payload).toContain(
      "turn:breakfast_eggs_green_tea_01032026_t{N}",
    );
  });
});
