// Dynamic child — the actual vital reading logged by the user.
// Extends the vital-type child context.
//
// context_id examples: "blood_pressure:120_80"
//                      "heart_rate:72bpm"
//                      "blood_sugar:95mgdl"
//                      "weight:70kg"
//                      "temperature:36.6c"
//                      "oxygen_saturation:98pct"
// extends:            ["vitals:blood_pressure"]  (or heart_rate/blood_sugar/etc.)
//
// Full chain:
//   person:nasim_u123
//     └── nasim_u123:vitals
//           ├── vitals:blood_pressure
//           │     └── blood_pressure:120_80       ← this level
//           ├── vitals:heart_rate
//           │     └── heart_rate:72bpm
//           ├── vitals:blood_sugar
//           │     └── blood_sugar:95mgdl
//           ├── vitals:weight
//           │     └── weight:70kg
//           ├── vitals:temperature
//           │     └── temperature:36.6c
//           └── vitals:oxygen_saturation
//                 └── oxygen_saturation:98pct

import type { VitalType } from "./child.js";

export interface BloodPressureReading {
  systolic: number;
  diastolic: number;
  unit: "mmHg";
}

export interface HeartRateReading {
  bpm: number;
}

export interface BloodSugarReading {
  value: number;
  unit: "mg/dL" | "mmol/L";
  timing: "fasting" | "before_meal" | "after_meal" | "random";
}

export interface WeightReading {
  value: number;
  unit: "kg" | "lbs";
}

export interface TemperatureReading {
  value: number;
  unit: "C" | "F";
}

export interface OxygenSaturationReading {
  spo2_percent: number;
}

export type VitalReading =
  | BloodPressureReading
  | HeartRateReading
  | BloodSugarReading
  | WeightReading
  | TemperatureReading
  | OxygenSaturationReading;

export interface VitalPayload {
  vital_type: VitalType;
  reading: VitalReading;
  recorded_at: string;
  notes: string;
}

interface DynamicVitalEvent {
  label: string;
  vital_type: VitalType;
  payload: VitalPayload;
}

export function dynamicVitalEvent(event: DynamicVitalEvent) {
  return {
    context_id: `${event.vital_type}:${event.label}`,
    event_kind: "fact" as const,
    source: "agent" as const,
    payload: event.payload,
    extends: [`vitals:${event.vital_type}`],
  };
}
