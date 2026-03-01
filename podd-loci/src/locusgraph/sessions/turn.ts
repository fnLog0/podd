// Turn — each user message → agent response in a session.
// Extends the session context.
//
// context_id examples: "turn:breakfast_eggs_green_tea_01032026_t1"
//                      "turn:breakfast_eggs_green_tea_01032026_t2"
// extends:            ["session:breakfast_eggs_green_tea_01032026"]
//
// Chain:
//   person:nasim_u123
//     └── nasim_u123:sessions
//           └── session:breakfast_eggs_green_tea_01032026
//                 ├── turn:breakfast_eggs_green_tea_01032026_t1   ← this level
//                 └── turn:breakfast_eggs_green_tea_01032026_t2

import { sessionContext } from "./session.js";
import { toToon } from "../../workflows/tools/toon-encoder.js";

export interface ToolCallRecord {
  tool_name: string;
  tool_input: Record<string, unknown>;
  tool_output: string;
}

export interface TurnPayload {
  turn_number: number;
  session_title: string;
  user_id: string;
  user_message: string;
  ai_response: string;
  tool_calls: ToolCallRecord[];
  message_count: number;
  logged_at: string;
}

export interface DynamicTurnEvent {
  session_title: string;
  turn_number: number;
  payload: TurnPayload;
}

export function turnContext(session_title: string, turn_number: number) {
  return `turn:${session_title}_t${turn_number}`;
}

export function dynamicTurnEvent(event: DynamicTurnEvent) {
  return {
    context_id: turnContext(event.session_title, event.turn_number),
    event_kind: "action" as const,
    source: "agent" as const,
    payload: { data_toon: toToon(event.payload) },
    extends: [sessionContext(event.session_title)],
  };
}
