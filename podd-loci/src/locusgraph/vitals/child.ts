// Child vital-type contexts. One per vital category.
// Extends the user's anchor vitals context.
//
// context_id examples: "vitals:blood_pressure"
//                      "vitals:heart_rate"
//                      "vitals:blood_sugar"
//                      "vitals:weight"
//                      "vitals:temperature"
//                      "vitals:oxygen_saturation"
// extends:            ["nasim_u123:vitals"]
//
// Graph:  nasim_u123:vitals  <──  vitals:blood_pressure    ──>  blood_pressure:120_80
//                            <──  vitals:heart_rate         ──>  heart_rate:72bpm
//                            <──  vitals:blood_sugar        ──>  blood_sugar:95mgdl
//                            <──  vitals:weight             ──>  weight:70kg
//                            <──  vitals:temperature        ──>  temperature:36.6c
//                            <──  vitals:oxygen_saturation  ──>  oxygen_saturation:98pct

import { anchorVitalsContext } from "./anchor.js";

export type VitalType =
  | "blood_pressure"
  | "heart_rate"
  | "blood_sugar"
  | "weight"
  | "temperature"
  | "oxygen_saturation";

export interface VitalEventInput {
  name: string;
  user_id: string;
  vital_type: VitalType;
}

export function childVitalEventPayload(event: VitalEventInput) {
  return {
    context_id: `vitals:${event.vital_type}`,
    event_kind: "fact" as const,
    source: "system" as const,
    payload: `this memories refer for ${event.vital_type}:{reading} contexts for future events`,
    extends: [anchorVitalsContext(event.name, event.user_id)],
  };
}
