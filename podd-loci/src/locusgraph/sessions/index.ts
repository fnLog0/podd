// Context hierarchy for session/turn tracking:
//
//   person:nasim_u123
//     └── nasim_u123:sessions                                        ← anchor (anchor.ts)
//           ├── session:breakfast_eggs_green_tea_01032026             ← session (session.ts) — created dynamically
//           │     ├── turn:breakfast_eggs_green_tea_01032026_t1       ← turn (turn.ts)
//           │     └── turn:breakfast_eggs_green_tea_01032026_t2
//           └── session:protein_intake_check_01032026
//                 └── turn:protein_intake_check_01032026_t1

export { anchorSessionsContext, anchorSessionsEventPayload } from "./anchor.js";
export { setCurrentSession, getCurrentSessionContextId, getCurrentTurnContextId } from "./tracker.js";
export { sessionContext, sessionEventPayload, type SessionEventInput } from "./session.js";
export {
  turnContext,
  dynamicTurnEvent,
  type ToolCallRecord,
  type TurnPayload,
  type DynamicTurnEvent,
} from "./turn.js";

import { anchorSessionsEventPayload } from "./anchor.js";
import { sessionEventPayload, type SessionEventInput } from "./session.js";
import { dynamicTurnEvent, type TurnPayload } from "./turn.js";

export async function bootstrapSessionsContexts(name: string, user_id: string) {
  const { getClient, getGraphId } = await import("../client.js");
  const client = getClient();
  const GRAPH_ID = getGraphId();

  const anchorEvent = anchorSessionsEventPayload({ name, user_id });
  const anchorResult = await client.storeEvent({
    graph_id: GRAPH_ID,
    ...anchorEvent,
    payload: { data: anchorEvent.payload },
  });
  console.log(`[bootstrap] sessions anchor created:`, anchorResult);
}

export function generateSessionTitle(firstMessage: string): string {
  const now = new Date();
  const dd = String(now.getDate()).padStart(2, "0");
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const yyyy = now.getFullYear();
  const date = `${dd}${mm}${yyyy}`;

  const slug = firstMessage
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, "")
    .trim()
    .split(/\s+/)
    .slice(0, 5)
    .join("_");

  return `${slug}_${date}`;
}

export async function storeSession(input: SessionEventInput) {
  const { getClient, getGraphId } = await import("../client.js");
  const client = getClient();
  const GRAPH_ID = getGraphId();

  const event = sessionEventPayload(input);
  const result = await client.storeEvent({
    graph_id: GRAPH_ID,
    ...event,
    payload: { data: event.payload },
  });
  console.log(`[session] session context stored:`, result);
  return result;
}

const MAX_FIELD_LENGTH = 1000;

function truncate(text: string, max = MAX_FIELD_LENGTH): string {
  if (text.length <= max) return text;
  return text.slice(0, max) + `... [truncated ${text.length - max} chars]`;
}

function trimTurnPayload(payload: TurnPayload): TurnPayload {
  return {
    ...payload,
    user_message: truncate(payload.user_message),
    ai_response: truncate(payload.ai_response, 2000),
    tool_calls: payload.tool_calls.map((tc) => ({
      ...tc,
      tool_output: truncate(tc.tool_output),
    })),
  };
}

export async function storeTurn(
  sessionTitle: string,
  turnPayload: TurnPayload,
) {
  const { getClient, getGraphId } = await import("../client.js");
  const client = getClient();
  const GRAPH_ID = getGraphId();

  const trimmed = trimTurnPayload(turnPayload);

  const event = dynamicTurnEvent({
    session_title: sessionTitle,
    turn_number: trimmed.turn_number,
    payload: trimmed,
  });

  try {
    const result = await client.storeEvent({
      graph_id: GRAPH_ID,
      ...event,
      payload: event.payload as unknown as Record<string, unknown>,
    });
    console.log(`[session] turn ${trimmed.turn_number} stored:`, result);
    return result;
  } catch (err) {
    console.error(
      `[session] turn ${trimmed.turn_number} store failed:`,
      err instanceof Error ? err.message : String(err),
    );
    return null;
  }
}
