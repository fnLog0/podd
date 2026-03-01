import type { AppContext } from "../types";
import { success, error } from "../utils/responses";
import { HumanMessage } from "@langchain/core/messages";
import {
  configure,
  graph,
  prefetchContextMap,
  getConfig,
} from "podd-loci";

function ensureConfigured(c: AppContext) {
  const config = getConfig();
  if (!config.locusGraphAgentSecret) {
    configure({
      locusGraphServerUrl: c.env.LOCUSGRAPH_SERVER_URL,
      locusGraphAgentSecret: c.env.LOCUSGRAPH_AGENT_SECRET || c.env.LOCUSGRAPH_JWT_PRIVATE_KEY,
      locusGraphGraphId: c.env.LOCUSGRAPH_GRAPH_ID,
      openaiApiKey: c.env.OPENAI_API_KEY,
      openaiModel: c.env.OPENAI_MODEL,
    });
  }
}

export async function chat(c: AppContext) {
  try {
    ensureConfigured(c);

    const user = c.get("user");
    const body = await c.req.json();
    const { message, thread_id } = body;

    if (!message || typeof message !== "string") {
      return error(c, "message is required", 400);
    }

    const threadId = thread_id || `thread_${user.id}_${Date.now()}`;
    const threadConfig = { configurable: { thread_id: threadId } };

    const result = await graph.invoke(
      {
        messages: [new HumanMessage(message)],
        user_id: user.id,
        user_name: user.name,
      },
      threadConfig,
    );

    const lastMessage = result.messages.at(-1);

    return success(c, {
      response: lastMessage?.content,
      thread_id: threadId,
      session_title: result.session_title,
      message_count: result.messages.length,
    });
  } catch (err) {
    console.error("Chat error:", err);
    return error(c, err instanceof Error ? err.message : "Internal server error", 500);
  }
}

export async function streamChat(c: AppContext) {
  ensureConfigured(c);

  const user = c.get("user");
  const body = await c.req.json();
  const { message, thread_id } = body;

  if (!message || typeof message !== "string") {
    return error(c, "message is required", 400);
  }

  const threadId = thread_id || `thread_${user.id}_${Date.now()}`;
  const threadConfig = { configurable: { thread_id: threadId } };

  const stream = await graph.stream(
    {
      messages: [new HumanMessage(message)],
      user_id: user.id,
      user_name: user.name,
    },
    { ...threadConfig, streamMode: "values" },
  );

  const encoder = new TextEncoder();
  const readable = new ReadableStream({
    async start(controller) {
      try {
        for await (const event of stream) {
          const data = JSON.stringify(event);
          controller.enqueue(encoder.encode(`data: ${data}\n\n`));
        }
        controller.close();
      } catch (err) {
        controller.error(err);
      }
    },
  });

  return new Response(readable, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}

export async function getContextMap(c: AppContext) {
  ensureConfigured(c);

  const contextMap = await prefetchContextMap();
  return success(c, contextMap);
}
