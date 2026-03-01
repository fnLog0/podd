// Context hierarchy for vitals tracking:
//
//   person:nasim_u123                              ← user (user.ts)
//     └── nasim_u123:vitals                        ← anchor (anchor.ts)
//           ├── vitals:blood_pressure               ← vital-type (vital-type.ts)
//           │     ├── blood_pressure:120_80_am       ← vital-reading (vital-reading.ts)
//           │     └── blood_pressure:130_85_pm
//           ├── vitals:heart_rate
//           │     └── heart_rate:72bpm_rest
//           ├── vitals:weight
//           │     └── weight:70kg_morning
//           ├── vitals:blood_sugar
//           │     └── blood_sugar:95_fasting
//           ├── vitals:temperature
//           │     └── temperature:36_5c
//           └── vitals:oxygen_saturation
//                 └── oxygen_saturation:98pct

export { anchorVitalsContext, anchorVitalsEventPayload } from "./anchor.js";
export { vitalTypeEventPayload, type VitalType, type VitalTypeEventInput } from "./vital-type.js";
export {
  vitalReadingEvent,
  type VitalReading,
  type VitalPayload,
} from "./vital-reading.js";

import { anchorVitalsEventPayload } from "./anchor.js";
import { vitalTypeEventPayload, type VitalType } from "./vital-type.js";

const VITAL_TYPES: VitalType[] = [
  "blood_pressure",
  "heart_rate",
  "weight",
  "blood_sugar",
  "temperature",
  "oxygen_saturation",
];

export async function bootstrapVitalsContexts(name: string, user_id: string) {
  const { getClient, getGraphId } = await import("../client.js");
  const client = getClient();
  const GRAPH_ID = getGraphId();

  const anchorEvent = anchorVitalsEventPayload({ name, user_id });
  const anchorResult = await client.storeEvent({
    graph_id: GRAPH_ID,
    ...anchorEvent,
    payload: { data: anchorEvent.payload },
  });
  console.log(`[bootstrap] vitals anchor created:`, anchorResult);

  for (const vital_type of VITAL_TYPES) {
    const vitalEvent = vitalTypeEventPayload({ name, user_id, vital_type });
    const vitalResult = await client.storeEvent({
      graph_id: GRAPH_ID,
      ...vitalEvent,
      payload: { data: vitalEvent.payload },
    });
    console.log(`[bootstrap] ${vital_type} context created:`, vitalResult);
  }
}
