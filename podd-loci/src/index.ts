// ── Config ──
export { configure, getConfig, type PoddConfig } from "./config.js";

// ── Graph ──
export { graph, GraphState, type GraphStateType } from "./workflows/graph.js";

// ── Tools ──
export {
  tools,
  logFoodItemTool,
  logVitalTool,
  retrieveMemoriesTool,
  listContextsTool,
  prefetchContextMap,
  type CategorizedContexts,
} from "./workflows/tools/index.js";

// ── Prompts ──
export {
  systemPrompt,
  foodParserPrompt,
  vitalsParserPrompt,
} from "./prompts/index.js";

// ── LocusGraph Client ──
export { getClient, getGraphId } from "./locusgraph/client.js";

// ── Bootstrap ──
export { bootstrapUser, type BootstrapOptions } from "./locusgraph/bootstrap.js";

// ── User ──
export {
  userPersonContext,
  userEventPayload,
  bootstrapUserContext,
  type UserEventPayload,
  type Gender,
  type ActivityLevel,
  type DietaryPreference,
} from "./locusgraph/user.js";

// ── Foods ──
export {
  anchorFoodContext,
  anchorFoodEventPayload,
  mealEventPayload,
  foodItemEvent,
  bootstrapFoodContexts,
  type FoodEventInput,
  type FoodPayload,
  type FoodItem,
  type Macros,
  type MealType,
} from "./locusgraph/foods/index.js";

// ── Vitals ──
export {
  anchorVitalsContext,
  anchorVitalsEventPayload,
  vitalTypeEventPayload,
  vitalReadingEvent,
  bootstrapVitalsContexts,
  type VitalType,
  type VitalTypeEventInput,
  type VitalReading,
  type VitalPayload,
} from "./locusgraph/vitals/index.js";

// ── Sessions ──
export {
  anchorSessionsContext,
  anchorSessionsEventPayload,
  sessionContext,
  sessionEventPayload,
  turnContext,
  dynamicTurnEvent,
  generateSessionTitle,
  storeSession,
  storeTurn,
  bootstrapSessionsContexts,
  type SessionEventInput,
  type ToolCallRecord,
  type TurnPayload,
  type DynamicTurnEvent,
} from "./locusgraph/sessions/index.js";

// ── Session Tracker ──
export {
  setCurrentSession,
  getCurrentSessionContextId,
  getCurrentTurnContextId,
} from "./locusgraph/sessions/tracker.js";

// ── TOON Encoder ──
export { toToon } from "./workflows/tools/toon-encoder.js";
