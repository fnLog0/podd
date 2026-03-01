import { describe, it, expect } from "vitest";
import {
  vitalTypeEventPayload,
  type VitalType,
} from "../../../locusgraph/vitals/vital-type.js";

describe("vitalTypeEventPayload", () => {
  it("generates correct context_id for blood_pressure", () => {
    const event = vitalTypeEventPayload({
      name: "nasim",
      user_id: "u123",
      vital_type: "blood_pressure",
    });
    expect(event.context_id).toBe("vitals:blood_pressure");
  });

  it.each<VitalType>([
    "blood_pressure",
    "heart_rate",
    "weight",
    "blood_sugar",
    "temperature",
    "oxygen_saturation",
  ])("maps %s to correct context_id", (vitalType) => {
    const event = vitalTypeEventPayload({
      name: "nasim",
      user_id: "u123",
      vital_type: vitalType,
    });
    expect(event.context_id).toBe(`vitals:${vitalType}`);
  });

  it("sets event_kind to fact", () => {
    const event = vitalTypeEventPayload({
      name: "nasim",
      user_id: "u123",
      vital_type: "heart_rate",
    });
    expect(event.event_kind).toBe("fact");
  });

  it("sets source to system", () => {
    const event = vitalTypeEventPayload({
      name: "nasim",
      user_id: "u123",
      vital_type: "weight",
    });
    expect(event.source).toBe("system");
  });

  it("extends anchor vitals context", () => {
    const event = vitalTypeEventPayload({
      name: "nasim",
      user_id: "u123",
      vital_type: "blood_pressure",
    });
    expect(event.extends).toEqual(["nasim_u123:vitals"]);
  });

  it("includes vital_type in payload description", () => {
    const event = vitalTypeEventPayload({
      name: "nasim",
      user_id: "u123",
      vital_type: "temperature",
    });
    expect(event.payload).toContain("temperature");
  });
});
