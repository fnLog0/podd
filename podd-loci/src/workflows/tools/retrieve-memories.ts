import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import { getClient, getGraphId } from "../../locusgraph/client.js";

export const retrieveMemoriesTool = new DynamicStructuredTool({
  name: "retrieve_memories",
  description:
    "Retrieve relevant memories from LocusGraph by semantic search. Use contextIds to narrow results to specific contexts like foods:breakfast or nasim_u123:foods.",
  schema: z.object({
    query: z.string().describe("The search query to find relevant memories"),
    contextIds: z
      .array(z.string())
      .describe("Optional context IDs to filter results")
      .default([]),
    limit: z.number().describe("Max number of results to return").default(5),
  }),
  func: async ({ query, contextIds, limit }) => {
    console.log("\n[retrieve_memories] Query:", query);
    if (contextIds.length > 0) console.log("[retrieve_memories] Context filter:", contextIds);
    console.log("[retrieve_memories] Limit:", limit);

    try {
      const req: Record<string, unknown> = {
        graphId: getGraphId(),
        query,
        limit,
      };
      if (contextIds.length > 0) req.contextIds = contextIds;

      const result = await getClient().retrieveMemories(
        req as { graphId: string; query: string; limit: number; contextIds?: string[] }
      );

      console.log("[retrieve_memories] Items found:", result.items_found);
      console.log("[retrieve_memories] Raw result:", JSON.stringify(result, null, 2));

      if (!result.memories || (Array.isArray(result.memories) && result.memories.length === 0)) {
        return "No memories found.";
      }
      return typeof result.memories === "string"
        ? result.memories
        : JSON.stringify(result.memories, null, 2);
    } catch (err) {
      console.error("[retrieve_memories] Error:", err);
      return `Failed to retrieve memories: ${err instanceof Error ? err.message : String(err)}`;
    }
  },
});
