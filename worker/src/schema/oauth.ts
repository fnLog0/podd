import { z } from "zod";

export const OAuthProvider = z.enum(["google", "github"]);

export const OAuthAccount = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  provider: OAuthProvider,
  provider_user_id: z.string(),
  access_token: z.string(),
  refresh_token: z.string().nullable(),
  expires_at: z.string().datetime().nullable(),
  created_at: z.string().datetime(),
});
