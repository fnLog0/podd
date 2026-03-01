// Tracks the current session and turn so tools (e.g. log_food)
// can link their events back to the active session/turn via related_to.

import { sessionContext } from "./session.js";
import { turnContext } from "./turn.js";

let _sessionTitle = "";
let _turnNumber = 0;

export function setCurrentSession(title: string, turn: number) {
  _sessionTitle = title;
  _turnNumber = turn;
}

export function getCurrentSessionContextId(): string {
  return _sessionTitle ? sessionContext(_sessionTitle) : "";
}

export function getCurrentTurnContextId(): string {
  return _sessionTitle && _turnNumber
    ? turnContext(_sessionTitle, _turnNumber)
    : "";
}
