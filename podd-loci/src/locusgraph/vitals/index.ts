// Context hierarchy for vitals tracking:
//
//   person:nasim_u123                             ← user (user.ts)
//     └── nasim_u123:vitals                       ← anchor (anchor.ts)
//           ├── vitals:blood_pressure             ← child (child.ts)
//           │     └── blood_pressure:120_80       ← dynamic-child (dynamic-child.ts)
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

export { anchorVitalsContext, anchorVitalsEventPayload } from "./anchor.js";
export { childVitalEventPayload, type VitalType, type VitalEventInput } from "./child.js";
export {
  dynamicVitalEvent,
  type VitalPayload,
  type VitalReading,
  type BloodPressureReading,
  type HeartRateReading,
  type BloodSugarReading,
  type WeightReading,
  type TemperatureReading,
  type OxygenSaturationReading,
} from "./dynamic-child.js";

import { anchorVitalsEventPayload } from "./anchor.js";
import { childVitalEventPayload, type VitalType } from "./child.js";

const VITAL_TYPES: VitalType[] = [
  "blood_pressure",
  "heart_rate",
  "blood_sugar",
  "weight",
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
    const childEvent = childVitalEventPayload({ name, user_id, vital_type });
    const childResult = await client.storeEvent({
      graph_id: GRAPH_ID,
      ...childEvent,
      payload: { data: childEvent.payload },
    });
    console.log(`[bootstrap] ${vital_type} context created:`, childResult);
  }
}
