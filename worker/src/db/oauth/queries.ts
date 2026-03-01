import type { OAuthAccount, OAuthProvider } from "../../schema";

export async function getOAuthAccount(
  db: D1Database,
  provider: OAuthProvider,
  providerUserId: string,
): Promise<OAuthAccount | null> {
  const row = await db
    .prepare("SELECT * FROM oauth_accounts WHERE provider = ? AND provider_user_id = ?")
    .bind(provider, providerUserId)
    .first();
  return row as OAuthAccount | null;
}

export async function getOAuthAccountsByUserId(
  db: D1Database,
  userId: string,
): Promise<OAuthAccount[]> {
  const { results } = await db
    .prepare("SELECT * FROM oauth_accounts WHERE user_id = ? ORDER BY created_at DESC")
    .bind(userId)
    .all();
  return results as OAuthAccount[];
}
