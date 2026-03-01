import { describe, it, expect } from "vitest";
import {
  anchorVitalsContext,
  anchorVitalsEventPayload,
} from "../../../locusgraph/vitals/anchor.js";

describe("anchorVitalsContext", () => {
  it("returns correct context id", () => {
    expect(anchorVitalsContext("nasim", "u123")).toBe("nasim_u123:vitals");
  });

  it("works with different user names", () => {
    expect(anchorVitalsContext("alice", "u999")).toBe("alice_u999:vitals");
  });
});

describe("anchorVitalsEventPayload", () => {
  it("returns correct context_id", () => {
    const event = anchorVitalsEventPayload({ name: "nasim", user_id: "u123" });
    expect(event.context_id).toBe("nasim_u123:vitals");
  });

  it("sets event_kind to fact", () => {
    const event = anchorVitalsEventPayload({ name: "nasim", user_id: "u123" });
    expect(event.event_kind).toBe("fact");
  });

  it("sets source to system", () => {
    const event = anchorVitalsEventPayload({ name: "nasim", user_id: "u123" });
    expect(event.source).toBe("system");
  });

  it("extends person context", () => {
    const event = anchorVitalsEventPayload({ name: "nasim", user_id: "u123" });
    expect(event.extends).toEqual(["person:nasim_u123"]);
  });

  it("includes all vital types in payload description", () => {
    const event = anchorVitalsEventPayload({ name: "nasim", user_id: "u123" });
    expect(event.payload).toContain("blood_pressure");
    expect(event.payload).toContain("heart_rate");
    expect(event.payload).toContain("weight");
    expect(event.payload).toContain("blood_sugar");
    expect(event.payload).toContain("temperature");
    expect(event.payload).toContain("oxygen_saturation");
  });
});
