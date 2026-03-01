import { z } from "zod";
import {
  User as UserSchema,
  UserCreate as UserCreateSchema,
  UserUpdate as UserUpdateSchema,
  Session as SessionSchema,
  Gender as GenderSchema,
  ActivityLevel as ActivityLevelSchema,
  DietaryPreference as DietaryPreferenceSchema,
} from "./user";
import {
  OAuthAccount as OAuthAccountSchema,
  OAuthProvider as OAuthProviderSchema,
} from "./oauth";

export const User = UserSchema;
export type User = z.infer<typeof UserSchema>;

export const UserCreate = UserCreateSchema;
export type UserCreate = z.infer<typeof UserCreateSchema>;

export const UserUpdate = UserUpdateSchema;
export type UserUpdate = z.infer<typeof UserUpdateSchema>;

export const Gender = GenderSchema;
export type Gender = z.infer<typeof GenderSchema>;

export const ActivityLevel = ActivityLevelSchema;
export type ActivityLevel = z.infer<typeof ActivityLevelSchema>;

export const DietaryPreference = DietaryPreferenceSchema;
export type DietaryPreference = z.infer<typeof DietaryPreferenceSchema>;

export const Session = SessionSchema;
export type Session = z.infer<typeof SessionSchema>;

export const OAuthAccount = OAuthAccountSchema;
export type OAuthAccount = z.infer<typeof OAuthAccountSchema>;

export const OAuthProvider = OAuthProviderSchema;
export type OAuthProvider = z.infer<typeof OAuthProviderSchema>;
