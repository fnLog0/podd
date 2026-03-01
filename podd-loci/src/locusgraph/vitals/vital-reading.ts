// Vital reading — an individual vital sign measurement logged by the user.
// Extends the vital-type context.
//
// context_id examples: "blood_pressure:120_80_01032026"
//                      "heart_rate:72bpm_01032026"
//                      "weight:70kg_01032026"
//                      "blood_sugar:95_fasting_01032026"
// extends:            ["vitals:blood_pressure"]  (or heart_rate/weight/etc.)
//
// Full chain:
//   person:nasim_u123
//     └── nasim_u123:vitals
//           ├── vitals:blood_pressure
//           │     ├── blood_pressure:120_80_01032026       ← this level
//           │     └── blood_pressure:130_85_02032026
//           ├── vitals:heart_rate
//           │     └── heart_rate:72bpm_01032026
//           ├── vitals:weight
//           │     └── weight:70kg_01032026
//           ├── vitals:blood_sugar
//           │     └── blood_sugar:95_fasting_01032026
//           ├── vitals:temperature
//           │     └── temperature:36_5c_01032026
//           └── vitals:oxygen_saturation
//                 └── oxygen_saturation:98pct_01032026

import type { VitalType } from "./vital-type.js";
import { toToon } from "../../workflows/tools/toon-encoder.js";

export interface VitalReading {
  label: string;
  value: number;
  unit: string;
}

export interface VitalPayload {
  vital_type: VitalType;
  readings: VitalReading[];
  measured_at: string;
  context: string;
  notes: string;
}

interface VitalReadingEvent {
  name: string;
  vital_type: VitalType;
  payload: VitalPayload;
  related_to?: string[];
}

function getVitalTypeContextId(type: VitalType): string {
  return `vitals:${type}`;
}

export function vitalReadingEvent(event: VitalReadingEvent) {
  return {
    context_id: `${event.vital_type}:${event.name}`,
    event_kind: "fact" as const,
    source: "agent" as const,
    payload: { data_toon: toToon(event.payload) },
    extends: [getVitalTypeContextId(event.vital_type)],
    ...(event.related_to?.length ? { related_to: event.related_to } : {}),
  };
}
