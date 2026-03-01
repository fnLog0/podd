import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import { getClient, getGraphId } from "../../locusgraph/client.js";
import {
  categorizeContexts,
  type CategorizedContexts,
} from "./context-formatter.js";
import { toToon } from "./toon-encoder.js";

export const listContextsTool = new DynamicStructuredTool({
  name: "list_contexts",
  description:
    "List available contexts from LocusGraph. Can filter by context_type or search by context_name. Call with no filters to list all context types.",
  schema: z.object({
    context_type: z
      .string()
      .describe("Optional filter by context type")
      .default(""),
    context_name: z
      .string()
      .describe("Optional search by context name")
      .default(""),
    limit: z.number().describe("Max number of results").default(50),
  }),
  func: async ({ context_type, context_name, limit }) => {
    console.log(
      "\n[list_contexts] type:",
      context_type || "all",
      "| name:",
      context_name || "all"
    );

    try {
      const opts: Record<string, unknown> = { graphId: getGraphId(), limit };
      if (context_type) opts.context_type = context_type;
      if (context_name) opts.context_name = context_name;

      const result = await getClient().listContexts(
        opts as { graphId: string; limit: number; context_type?: string; context_name?: string }
      );

      console.log("[list_contexts] Result:", JSON.stringify(result, null, 2));

      return toToon(result);
    } catch (err) {
      console.error("[list_contexts] Error:", err);
      return `Failed to list contexts: ${err instanceof Error ? err.message : String(err)}`;
    }
  },
});

const NO_CONTEXTS: CategorizedContexts = {
  user_contexts: "No user contexts available.",
  food_contexts: "No food contexts available.",
  session_contexts: "No session contexts available.",
};

interface ContextTypeEntry {
  context_type: string;
  count: number;
}

interface RawContext {
  context_id: string;
  [key: string]: unknown;
}

function extractArray(obj: unknown, key: string): unknown[] {
  if (obj && typeof obj === "object" && key in obj) {
    const val = (obj as Record<string, unknown>)[key];
    if (Array.isArray(val)) return val;
  }
  return [];
}

export async function prefetchContextMap(): Promise<CategorizedContexts> {
  try {
    const client = getClient();
    const graphId = getGraphId();

    const typesResult = await client.listContexts({ graphId, limit: 100 });

    console.log("[prefetch] Raw API response:", JSON.stringify(typesResult, null, 2));

    const contextTypes = extractArray(typesResult, "context_types") as ContextTypeEntry[];

    if (contextTypes.length === 0) {
      // Fallback: the response itself may already contain contexts directly
      const directContexts = extractArray(typesResult, "contexts") as RawContext[];
      if (directContexts.length > 0) {
        console.log("[prefetch] Found contexts directly:", directContexts.length);
        return categorizeContexts(directContexts);
      }

      console.log("[prefetch] No context types or contexts found");
      return NO_CONTEXTS;
    }

    console.log(
      "[prefetch] Found context types:",
      contextTypes.map((ct) => `${ct.context_type}(${ct.count})`).join(", "),
    );

    const allContexts: RawContext[] = [];

    for (const ct of contextTypes) {
      const result = await client.listContexts({
        graphId,
        context_type: ct.context_type,
        limit: 100,
      });

      const contexts = extractArray(result, "contexts") as RawContext[];
      allContexts.push(...contexts);
    }

    console.log(
      "[prefetch] Total contexts loaded:",
      allContexts.length,
      "| IDs:",
      allContexts.map((c) => c.context_id).join(", "),
    );

    return categorizeContexts(allContexts);
  } catch (err) {
    console.error("[prefetch] Error:", err);
    return NO_CONTEXTS;
  }
}
