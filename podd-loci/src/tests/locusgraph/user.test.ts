import { describe, it, expect } from "vitest";
import {
  userPersonContext,
  userEventPayload,
  type UserEventPayload,
} from "../../locusgraph/user.js";

const sampleUser: UserEventPayload = {
  name: "nasim",
  user_id: "u123",
  email: "nasim@example.com",
  age: 30,
  gender: "male",
  height_cm: 175,
  weight_kg: 70,
  activity_level: "moderate",
  dietary_preferences: ["none"],
  allergies: [],
  medical_conditions: [],
  daily_calorie_goal: 2200,
};

describe("userPersonContext", () => {
  it("returns correct context id format", () => {
    expect(userPersonContext("nasim", "u123")).toBe("person:nasim_u123");
  });

  it("handles different name/id combinations", () => {
    expect(userPersonContext("alice", "u999")).toBe("person:alice_u999");
    expect(userPersonContext("bob", "abc")).toBe("person:bob_abc");
  });

  it("handles empty strings", () => {
    expect(userPersonContext("", "")).toBe("person:_");
  });
});

describe("userEventPayload", () => {
  it("returns correct structure with context_id", () => {
    const event = userEventPayload(sampleUser);
    expect(event.context_id).toBe("person:nasim_u123");
  });

  it("sets event_kind to 'fact'", () => {
    const event = userEventPayload(sampleUser);
    expect(event.event_kind).toBe("fact");
  });

  it("sets source to 'system'", () => {
    const event = userEventPayload(sampleUser);
    expect(event.source).toBe("system");
  });

  it("spreads all user fields into payload", () => {
    const event = userEventPayload(sampleUser);
    expect(event.payload).toMatchObject({
      name: "nasim",
      user_id: "u123",
      email: "nasim@example.com",
      age: 30,
      gender: "male",
      height_cm: 175,
      weight_kg: 70,
      activity_level: "moderate",
      dietary_preferences: ["none"],
      allergies: [],
      medical_conditions: [],
      daily_calorie_goal: 2200,
    });
  });

  it("creates a separate copy of payload (not same reference)", () => {
    const event = userEventPayload(sampleUser);
    expect(event.payload).not.toBe(sampleUser);
    expect(event.payload).toEqual(sampleUser);
  });
});
