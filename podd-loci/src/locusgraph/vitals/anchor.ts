// Anchor (root) vitals context for a user.
// Extends the user's person context and links down to vital-type children.
//
// context_id example: "nasim_u123:vitals"
// extends:           ["person:nasim_u123"]
//
// Graph:  person:nasim_u123  <──  nasim_u123:vitals  ──>  vitals:blood_pressure
//                                                     ──>  vitals:heart_rate
//                                                     ──>  vitals:weight
//                                                     ──>  vitals:blood_sugar
//                                                     ──>  vitals:temperature
//                                                     ──>  vitals:oxygen_saturation

import { userPersonContext } from "../user.js";

function normalizeId(str: string): string {
  return str.toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_-]/g, "");
}

export function anchorVitalsContext(name: string, user_id: string) {
  return `${normalizeId(name)}_${normalizeId(user_id)}:vitals`;
}

export function anchorVitalsEventPayload({
  name,
  user_id,
}: {
  name: string;
  user_id: string;
}) {
  return {
    context_id: anchorVitalsContext(name, user_id),
    event_kind: "fact" as const,
    source: "system" as const,
    payload: `this memories link to these context vitals:blood_pressure, vitals:heart_rate, vitals:weight, vitals:blood_sugar, vitals:temperature, vitals:oxygen_saturation`,
    extends: [userPersonContext(name, user_id)],
  };
}
