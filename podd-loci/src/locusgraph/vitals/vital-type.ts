// Vital-type contexts. One per vital category.
// Extends the user's anchor vitals context.
//
// context_id examples: "vitals:blood_pressure"
//                      "vitals:heart_rate"
//                      "vitals:weight"
//                      "vitals:blood_sugar"
//                      "vitals:temperature"
//                      "vitals:oxygen_saturation"
// extends:            ["nasim_u123:vitals"]
//
// Graph:  nasim_u123:vitals  <──  vitals:blood_pressure  ──>  blood_pressure:120_80_01032026
//                             <──  vitals:heart_rate       ──>  heart_rate:72_01032026
//                             <──  vitals:weight           ──>  weight:70kg_01032026

import { anchorVitalsContext } from "./anchor.js";

export type VitalType =
  | "blood_pressure"
  | "heart_rate"
  | "weight"
  | "blood_sugar"
  | "temperature"
  | "oxygen_saturation";

export interface VitalTypeEventInput {
  name: string;
  user_id: string;
  vital_type: VitalType;
}

export function vitalTypeEventPayload(event: VitalTypeEventInput) {
  return {
    context_id: `vitals:${event.vital_type}`,
    event_kind: "fact" as const,
    source: "system" as const,
    payload: `this memories refer for ${event.vital_type}:{llm_generated_name} contexts for future events`,
    extends: [anchorVitalsContext(event.name, event.user_id)],
  };
}
