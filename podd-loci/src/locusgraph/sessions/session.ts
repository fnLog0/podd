// Session context — one per conversation.
// Extends the user's anchor sessions context.
// context_id is human-readable so the LLM understands what happened in each session.
//
// context_id examples: "session:breakfast_eggs_green_tea_01032026"
//                      "session:protein_intake_check_01032026"
// extends:            ["nasim_u123:sessions"]
//
// Graph:  nasim_u123:sessions  <──  session:breakfast_eggs_green_tea_01032026
//                              <──  session:protein_intake_check_01032026

import { anchorSessionsContext } from "./anchor.js";

export interface SessionEventInput {
  name: string;
  user_id: string;
  session_title: string;
}

export function sessionContext(session_title: string) {
  return `session:${session_title}`;
}

export function sessionEventPayload(event: SessionEventInput) {
  return {
    context_id: sessionContext(event.session_title),
    event_kind: "fact" as const,
    source: "system" as const,
    payload: `conversation session about "${event.session_title.replace(/_/g, " ")}" — each turn is stored as turn:${event.session_title}_t{N}`,
    extends: [anchorSessionsContext(event.name, event.user_id)],
  };
}
