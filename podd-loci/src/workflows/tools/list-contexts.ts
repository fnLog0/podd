import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import { getClient, getGraphId } from "../../locusgraph/client.js";

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

      return JSON.stringify(result, null, 2);
    } catch (err) {
      console.error("[list_contexts] Error:", err);
      return `Failed to list contexts: ${err instanceof Error ? err.message : String(err)}`;
    }
  },
});

export async function prefetchContextMap(): Promise<string> {
  try {
    const result = await getClient().listContexts({
      graphId: getGraphId(),
      limit: 100,
    });

    return JSON.stringify(result, null, 2);
  } catch {
    return "No context map available.";
  }
}
