import { describe, it, expect } from "vitest";
import {
  anchorSessionsContext,
  anchorSessionsEventPayload,
} from "../../../locusgraph/sessions/anchor.js";

describe("anchorSessionsContext", () => {
  it("returns correct context id", () => {
    expect(anchorSessionsContext("nasim", "u123")).toBe("nasim_u123:sessions");
  });

  it("handles different user inputs", () => {
    expect(anchorSessionsContext("alice", "u999")).toBe("alice_u999:sessions");
  });
});

describe("anchorSessionsEventPayload", () => {
  it("returns correct context_id", () => {
    const event = anchorSessionsEventPayload({
      name: "nasim",
      user_id: "u123",
    });
    expect(event.context_id).toBe("nasim_u123:sessions");
  });

  it("sets event_kind to 'fact'", () => {
    const event = anchorSessionsEventPayload({
      name: "nasim",
      user_id: "u123",
    });
    expect(event.event_kind).toBe("fact");
  });

  it("sets source to 'system'", () => {
    const event = anchorSessionsEventPayload({
      name: "nasim",
      user_id: "u123",
    });
    expect(event.source).toBe("system");
  });

  it("extends the user person context", () => {
    const event = anchorSessionsEventPayload({
      name: "nasim",
      user_id: "u123",
    });
    expect(event.extends).toEqual(["person:nasim_u123"]);
  });

  it("payload mentions the user name", () => {
    const event = anchorSessionsEventPayload({
      name: "nasim",
      user_id: "u123",
    });
    expect(event.payload).toContain("nasim");
  });
});
