import { z } from "zod";

export const Gender = z.enum(["male", "female", "other"]);

export const ActivityLevel = z.enum([
  "sedentary",
  "light",
  "moderate",
  "active",
  "very_active",
]);

export const DietaryPreference = z.enum([
  "none",
  "vegetarian",
  "vegan",
  "keto",
  "paleo",
  "gluten_free",
  "dairy_free",
]);

export const User = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string(),
  avatar_url: z.string().url().nullable(),
  age: z.number().int().min(1).max(150).nullable(),
  gender: Gender.nullable(),
  height_cm: z.number().positive().nullable(),
  weight_kg: z.number().positive().nullable(),
  activity_level: ActivityLevel.nullable(),
  dietary_preferences: z.array(DietaryPreference).default([]),
  allergies: z.array(z.string()).default([]),
  medical_conditions: z.array(z.string()).default([]),
  daily_calorie_goal: z.number().int().positive().nullable(),
  locusgraph_bootstrapped: z.boolean().default(false),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const UserCreate = User.pick({
  email: true,
  name: true,
}).extend({
  avatar_url: z.string().url().nullable().optional(),
});

export const UserUpdate = z.object({
  name: z.string().optional(),
  avatar_url: z.string().url().nullable().optional(),
  age: z.number().int().min(1).max(150).nullable().optional(),
  gender: Gender.nullable().optional(),
  height_cm: z.number().positive().nullable().optional(),
  weight_kg: z.number().positive().nullable().optional(),
  activity_level: ActivityLevel.nullable().optional(),
  dietary_preferences: z.array(DietaryPreference).optional(),
  allergies: z.array(z.string()).optional(),
  medical_conditions: z.array(z.string()).optional(),
  daily_calorie_goal: z.number().int().positive().nullable().optional(),
});

export const Session = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  token: z.string(),
  expires_at: z.string().datetime(),
  created_at: z.string().datetime(),
});
