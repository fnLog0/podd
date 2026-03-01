import { describe, it, expect } from "vitest";
import {
  vitalReadingEvent,
  type VitalPayload,
} from "../../../locusgraph/vitals/vital-reading.js";
import type { VitalType } from "../../../locusgraph/vitals/vital-type.js";

function makeVitalPayload(overrides?: Partial<VitalPayload>): VitalPayload {
  return {
    vital_type: "blood_pressure",
    readings: [
      { label: "systolic", value: 120, unit: "mmHg" },
      { label: "diastolic", value: 80, unit: "mmHg" },
    ],
    measured_at: "2026-03-01T08:00:00Z",
    context: "resting",
    notes: "",
    ...overrides,
  };
}

describe("vitalReadingEvent", () => {
  it("generates correct context_id from vital_type and name", () => {
    const event = vitalReadingEvent({
      name: "120_80_01032026",
      vital_type: "blood_pressure",
      payload: makeVitalPayload(),
    });
    expect(event.context_id).toBe("blood_pressure:120_80_01032026");
  });

  it.each<VitalType>([
    "blood_pressure",
    "heart_rate",
    "weight",
    "blood_sugar",
    "temperature",
    "oxygen_saturation",
  ])("maps %s to the correct vital type context in extends", (vitalType) => {
    const event = vitalReadingEvent({
      name: "test_reading",
      vital_type: vitalType,
      payload: makeVitalPayload({ vital_type: vitalType }),
    });
    expect(event.extends).toEqual([`vitals:${vitalType}`]);
  });

  it("sets event_kind to fact", () => {
    const event = vitalReadingEvent({
      name: "120_80_01032026",
      vital_type: "blood_pressure",
      payload: makeVitalPayload(),
    });
    expect(event.event_kind).toBe("fact");
  });

  it("sets source to agent", () => {
    const event = vitalReadingEvent({
      name: "120_80_01032026",
      vital_type: "blood_pressure",
      payload: makeVitalPayload(),
    });
    expect(event.source).toBe("agent");
  });

  it("wraps payload as TOON-encoded data_toon string", () => {
    const payload = makeVitalPayload();
    const event = vitalReadingEvent({
      name: "120_80_01032026",
      vital_type: "blood_pressure",
      payload,
    });
    expect(event.payload).toHaveProperty("data_toon");
    expect(typeof event.payload.data_toon).toBe("string");
    expect(event.payload.data_toon).toContain("systolic");
    expect(event.payload.data_toon).toContain("120");
    expect(event.payload.data_toon).toContain("diastolic");
    expect(event.payload.data_toon).toContain("80");
  });

  it("includes related_to when provided", () => {
    const event = vitalReadingEvent({
      name: "120_80_01032026",
      vital_type: "blood_pressure",
      payload: makeVitalPayload(),
      related_to: ["session:my_session", "turn:my_session_t1"],
    });
    expect(event.related_to).toEqual([
      "session:my_session",
      "turn:my_session_t1",
    ]);
  });

  it("omits related_to when not provided", () => {
    const event = vitalReadingEvent({
      name: "120_80_01032026",
      vital_type: "blood_pressure",
      payload: makeVitalPayload(),
    });
    expect(event).not.toHaveProperty("related_to");
  });

  it("omits related_to when array is empty", () => {
    const event = vitalReadingEvent({
      name: "120_80_01032026",
      vital_type: "blood_pressure",
      payload: makeVitalPayload(),
      related_to: [],
    });
    expect(event).not.toHaveProperty("related_to");
  });

  it("handles weight vital type", () => {
    const event = vitalReadingEvent({
      name: "70kg_01032026",
      vital_type: "weight",
      payload: makeVitalPayload({
        vital_type: "weight",
        readings: [{ label: "weight", value: 70, unit: "kg" }],
      }),
    });
    expect(event.context_id).toBe("weight:70kg_01032026");
    expect(event.extends).toEqual(["vitals:weight"]);
    expect(event.payload.data_toon).toContain("70");
  });

  it("handles heart_rate vital type", () => {
    const event = vitalReadingEvent({
      name: "72bpm_01032026",
      vital_type: "heart_rate",
      payload: makeVitalPayload({
        vital_type: "heart_rate",
        readings: [{ label: "bpm", value: 72, unit: "bpm" }],
      }),
    });
    expect(event.context_id).toBe("heart_rate:72bpm_01032026");
    expect(event.extends).toEqual(["vitals:heart_rate"]);
  });
});
