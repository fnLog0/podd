// Anchor (root) sessions context for a user.
// Extends the user's person context and links down to individual sessions.
//
// context_id example: "nasim_u123:sessions"
// extends:           ["person:nasim_u123"]
//
// Graph:  person:nasim_u123  <──  nasim_u123:sessions  ──>  session:breakfast_eggs_green_tea_01032026
//                                                      ──>  session:protein_intake_check_01032026

import { userPersonContext } from "../user.js";

function normalizeId(str: string): string {
  return str.toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_-]/g, "");
}

export function anchorSessionsContext(name: string, user_id: string) {
  return `${normalizeId(name)}_${normalizeId(user_id)}:sessions`;
}

export function anchorSessionsEventPayload({
  name,
  user_id,
}: {
  name: string;
  user_id: string;
}) {
  return {
    context_id: anchorSessionsContext(name, user_id),
    event_kind: "fact" as const,
    source: "system" as const,
    payload: `all conversation sessions for user ${name} — each session is stored as session:{chat_title}`,
    extends: [userPersonContext(name, user_id)],
  };
}
