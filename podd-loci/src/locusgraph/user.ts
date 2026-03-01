export type Gender = "male" | "female" | "other";
export type ActivityLevel = "sedentary" | "light" | "moderate" | "active" | "very_active";
export type DietaryPreference = "none" | "vegetarian" | "vegan" | "keto" | "paleo" | "gluten_free" | "dairy_free";

export interface UserEventPayload {
  name: string;
  user_id: string;
  email: string;
  age: number;
  gender: Gender;
  height_cm: number;
  weight_kg: number;
  activity_level: ActivityLevel;
  dietary_preferences: DietaryPreference[];
  allergies: string[];
  medical_conditions: string[];
  daily_calorie_goal: number;
}

export function userPersonContext(name: string, user_id: string) {
  const normalizedName = name.toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_-]/g, "");
  const normalizedUserId = user_id.replace(/[^a-z0-9_-]/g, "");
  return `person:${normalizedName}_${normalizedUserId}`;
}

export function userEventPayload(user: UserEventPayload) {
  return {
    context_id: userPersonContext(user.name, user.user_id),
    event_kind: "fact" as const,
    source: "system" as const,
    payload: { ...user },
  };
}

export async function bootstrapUserContext(user: UserEventPayload) {
  const { getClient, getGraphId } = await import("./client.js");
  const client = getClient();
  const GRAPH_ID = getGraphId();

  const event = userEventPayload(user);
  const result = await client.storeEvent({
    graph_id: GRAPH_ID,
    ...event,
    payload: event.payload as unknown as Record<string, unknown>,
  });
  console.log(`[bootstrap] person context created:`, result);
  return result;
}
