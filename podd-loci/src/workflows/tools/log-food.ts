import { DynamicTool } from "@langchain/core/tools";
import { ChatOpenAI } from "@langchain/openai";
import { getClient, getGraphId } from "../../locusgraph/client.js";
import { dynamicChildEvent } from "../../locusgraph/foods/dynamic-child.js";
import type { FoodPayload } from "../../locusgraph/foods/dynamic-child.js";

const foodParserLLM = new ChatOpenAI({
  model: "gpt-4o-mini",
  temperature: 0,
});

const FOOD_PARSE_PROMPT = `You are a nutrition assistant. Parse the user's food description into structured JSON.
Return ONLY valid JSON matching this exact schema — no markdown, no explanation:

{
  "meal_type": "breakfast" | "lunch" | "dinner" | "snack",
  "items": [
    {
      "name": "food name (lowercase, underscores for spaces)",
      "quantity": number,
      "unit": "g" | "mg" | "ml" | "oz" | "cup" | "tbsp" | "tsp" | "piece" | "serving"
    }
  ],
  "macros": {
    "calories": number,
    "protein_g": number,
    "carbs_g": number,
    "fat_g": number,
    "fiber_g": number,
    "sugar_g": number
  },
  "logged_at": "ISO 8601 timestamp (use current time if not specified)",
  "notes": "any extra context from user, empty string if none"
}

Estimate macros as accurately as possible based on the food items and quantities.
If meal_type is not mentioned, infer from the time or default to "snack".`;

export const logFoodTool = new DynamicTool({
  name: "log_food",
  description:
    "Log what the user ate. Input is a natural language description of food, e.g. 'I had 2 eggs and toast for breakfast'. Parses it with an LLM, estimates nutrition, and stores it in LocusGraph.",
  func: async (input: string) => {
    console.log("\n[log_food] Input:", input);

    const response = await foodParserLLM.invoke([
      { role: "system", content: FOOD_PARSE_PROMPT },
      { role: "user", content: input },
    ]);

    const content =
      typeof response.content === "string"
        ? response.content
        : JSON.stringify(response.content);

    console.log("\n[log_food] LLM raw response:", content);

    let parsed: FoodPayload;
    try {
      parsed = JSON.parse(content) as FoodPayload;
    } catch {
      return `Failed to parse food data from LLM response: ${content}`;
    }

    console.log("\n[log_food] Parsed payload:", JSON.stringify(parsed, null, 2));

    const primaryItem = parsed.items[0]?.name ?? "unknown";
    const event = dynamicChildEvent({
      name: primaryItem,
      meal_type: parsed.meal_type,
      payload: parsed,
    });

    console.log("\n[log_food] Event to store:", JSON.stringify(event, null, 2));

    try {
      const result = await getClient().storeEvent({
        graph_id: getGraphId(),
        ...event,
        payload: event.payload as unknown as Record<string, unknown>,
      });

      console.log("\n[log_food] LocusGraph response:", JSON.stringify(result, null, 2));

      const itemNames = parsed.items.map((i) => i.name).join(", ");
      return `Logged ${parsed.meal_type}: ${itemNames} (${parsed.macros.calories} cal). Event ID: ${result.event_id}`;
    } catch (err) {
      console.error("\n[log_food] Store error:", err);
      return `Failed to store food event: ${err instanceof Error ? err.message : String(err)}`;
    }
  },
});
