import { DynamicTool } from "@langchain/core/tools";
import { ChatOpenAI } from "@langchain/openai";
import { getClient, getGraphId } from "../../locusgraph/client.js";
import { foodItemEvent } from "../../locusgraph/foods/food-item.js";
import type { FoodPayload } from "../../locusgraph/foods/food-item.js";
import {
  getCurrentSessionContextId,
  getCurrentTurnContextId,
} from "../../locusgraph/sessions/tracker.js";
import { foodParserPrompt } from "../../prompts/index.js";

export const logFoodItemTool = new DynamicTool({
  name: "log_food_item",
  description:
    "Log what the user ate. Input is a natural language description of food, e.g. 'I had 2 eggs and toast for breakfast'. Parses it with an LLM, estimates nutrition, and stores it in LocusGraph.",
  func: async (input: string) => {
    console.log("\n[log_food_item] Input:", input);

    const llm = new ChatOpenAI({ model: "gpt-4o-mini", temperature: 0 });
    const chain = foodParserPrompt.pipe(llm);
    const response = await chain.invoke({ input });

    const content =
      typeof response.content === "string"
        ? response.content
        : JSON.stringify(response.content);

    console.log("\n[log_food_item] LLM raw response:", content);

    let parsed: FoodPayload;
    try {
      parsed = JSON.parse(content) as FoodPayload;
    } catch {
      return `Failed to parse food data from LLM response: ${content}`;
    }

    console.log("\n[log_food_item] Parsed payload:", JSON.stringify(parsed, null, 2));

    const primaryItem = parsed.items[0]?.name ?? "unknown";
    const related_to = [
      getCurrentSessionContextId(),
      getCurrentTurnContextId(),
    ].filter(Boolean);

    const event = foodItemEvent({
      name: primaryItem,
      meal_type: parsed.meal_type,
      payload: parsed,
      ...(related_to.length ? { related_to } : {}),
    });

    console.log("\n[log_food_item] Event to store:", JSON.stringify(event, null, 2));

    try {
      const result = await getClient().storeEvent({
        graph_id: getGraphId(),
        ...event,
        payload: event.payload as unknown as Record<string, unknown>,
      });

      console.log("\n[log_food_item] LocusGraph response:", JSON.stringify(result, null, 2));

      const itemNames = parsed.items.map((i) => i.name).join(", ");
      return `Logged ${parsed.meal_type}: ${itemNames} (${parsed.macros.calories} cal). Event ID: ${result.event_id}`;
    } catch (err) {
      console.error("\n[log_food_item] Store error:", err);
      return `Failed to store food event: ${err instanceof Error ? err.message : String(err)}`;
    }
  },
});
