import { toToon } from "./toon-encoder.js";

interface RawContext {
  context_id: string;
  [key: string]: unknown;
}

export interface CategorizedContexts {
  user_contexts: string;
  food_contexts: string;
  session_contexts: string;
}

const FOOD_ITEM_PREFIXES = ["breakfast:", "lunch:", "dinner:", "snack:"];
const MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"];

function isUserContext(id: string): boolean {
  return id.startsWith("person:");
}

function isFoodAnchor(id: string): boolean {
  return id.endsWith(":foods");
}

function isMealContext(id: string): boolean {
  return id.startsWith("foods:");
}

function isFoodItemContext(id: string): boolean {
  return FOOD_ITEM_PREFIXES.some((p) => id.startsWith(p));
}

function isSessionAnchor(id: string): boolean {
  return id.endsWith(":sessions");
}

function isSessionContext(id: string): boolean {
  return id.startsWith("session:");
}

function isTurnContext(id: string): boolean {
  return id.startsWith("turn:");
}

function getMealTypeFromFoodItem(id: string): string | null {
  for (const meal of MEAL_TYPES) {
    if (id.startsWith(`${meal}:`)) return meal;
  }
  return null;
}

function getSessionTitleFromTurn(turnId: string): string | null {
  const match = turnId.match(/^turn:(.+)_t\d+$/);
  return match?.[1] ?? null;
}

function classifyContext(id: string): string {
  if (isFoodAnchor(id)) return "anchor";
  if (isMealContext(id)) return "meal";
  if (isFoodItemContext(id)) return "item";
  if (isSessionAnchor(id)) return "anchor";
  if (isSessionContext(id)) return "session";
  if (isTurnContext(id)) return "turn";
  if (isUserContext(id)) return "user";
  return "other";
}

function buildFoodHierarchy(contexts: RawContext[]): Record<string, unknown> {
  const anchors = contexts.filter((c) => isFoodAnchor(c.context_id));
  const meals = contexts.filter((c) => isMealContext(c.context_id));
  const items = contexts.filter((c) => isFoodItemContext(c.context_id));

  const mealNodes = meals.map((meal) => {
    const mealType = meal.context_id.replace("foods:", "");
    const mealItems = items
      .filter((i) => getMealTypeFromFoodItem(i.context_id) === mealType)
      .map((i) => ({ id: i.context_id, role: "item" }));
    return { id: meal.context_id, role: "meal", items: mealItems };
  });

  return {
    anchors: anchors.map((a) => a.context_id),
    meals: mealNodes,
  };
}

function buildSessionHierarchy(contexts: RawContext[]): Record<string, unknown> {
  const anchors = contexts.filter((c) => isSessionAnchor(c.context_id));
  const sessions = contexts.filter((c) => isSessionContext(c.context_id));
  const turns = contexts.filter((c) => isTurnContext(c.context_id));

  const sessionNodes = sessions.map((session) => {
    const title = session.context_id.replace("session:", "");
    const sessionTurns = turns
      .filter((t) => getSessionTitleFromTurn(t.context_id) === title)
      .map((t) => t.context_id);
    return { id: session.context_id, turns: sessionTurns };
  });

  return {
    anchors: anchors.map((a) => a.context_id),
    sessions: sessionNodes,
  };
}

function formatUserContexts(contexts: RawContext[]): string {
  if (contexts.length === 0) return "No user contexts available.";
  return toToon(contexts.map((c) => ({
    id: c.context_id,
    role: classifyContext(c.context_id),
  })));
}

function formatFoodContexts(contexts: RawContext[]): string {
  if (contexts.length === 0) return "No food contexts available.";
  return toToon(buildFoodHierarchy(contexts));
}

function formatSessionContexts(contexts: RawContext[]): string {
  if (contexts.length === 0) return "No session contexts available.";
  return toToon(buildSessionHierarchy(contexts));
}

function extractContexts(raw: unknown): RawContext[] {
  if (Array.isArray(raw)) {
    return raw
      .filter((item): item is RawContext =>
        item && typeof item === "object" && typeof (item.context_id ?? item.id) === "string",
      )
      .map((item) => ({
        ...item,
        context_id: (item.context_id ?? item.id) as string,
      }));
  }

  if (raw && typeof raw === "object") {
    const obj = raw as Record<string, unknown>;
    if (Array.isArray(obj.contexts)) return extractContexts(obj.contexts);
    if (Array.isArray(obj.items)) return extractContexts(obj.items);
    if (Array.isArray(obj.results)) return extractContexts(obj.results);
  }

  return [];
}

export function categorizeContexts(
  raw: unknown,
): CategorizedContexts {
  const contexts = extractContexts(raw);

  const user = contexts.filter((c) => isUserContext(c.context_id));
  const food = contexts.filter(
    (c) =>
      isFoodAnchor(c.context_id) ||
      isMealContext(c.context_id) ||
      isFoodItemContext(c.context_id),
  );
  const session = contexts.filter(
    (c) =>
      isSessionAnchor(c.context_id) ||
      isSessionContext(c.context_id) ||
      isTurnContext(c.context_id),
  );

  return {
    user_contexts: formatUserContexts(user),
    food_contexts: formatFoodContexts(food),
    session_contexts: formatSessionContexts(session),
  };
}
