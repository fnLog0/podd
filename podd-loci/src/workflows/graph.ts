import "dotenv/config";
import {
  Annotation,
  StateGraph,
  MessagesAnnotation,
  END,
  START,
  messagesStateReducer,
} from "@langchain/langgraph";
import type { BaseMessage } from "@langchain/core/messages";
import { SystemMessage } from "@langchain/core/messages";
import { ToolNode, toolsCondition } from "@langchain/langgraph/prebuilt";
import { ChatOpenAI } from "@langchain/openai";
import { tools, prefetchContextMap } from "./tools/index.js";
import type { UserEventPayload } from "../locusgraph/user.js";

const overwrite = <T>() => ({
  reducer: (_prev: T, next: T) => next,
});

export const GraphState = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: messagesStateReducer,
    default: () => [],
  }),

  user_id: Annotation<string>(overwrite<string>()),

  user: Annotation<UserEventPayload | null>({
    ...overwrite<UserEventPayload | null>(),
    default: () => null,
  }),

  intent: Annotation<string>({
    ...overwrite<string>(),
    default: () => "",
  }),

  context_map: Annotation<string>({
    ...overwrite<string>(),
    default: () => "",
  }),
});

export type GraphStateType = typeof GraphState.State;

const llm = new ChatOpenAI({
  model: "gpt-4o-mini",
  temperature: 0,
});

const modelWithTools = llm.bindTools(tools);

const SYSTEM_PROMPT = `You are a health assistant that tracks food intake and provides nutritional guidance.

You have access to a memory system (LocusGraph) with the following tools:
- log_food: Use when the user reports what they ate. Parses food into structured nutrition data and stores it.
- retrieve_memories: Use when you need past context (food history, patterns) to answer the user. Pass a query and optional contextIds to filter.
- list_contexts: Use to refresh the context map and discover available contexts.
- get_current_time: Use when you need the current date/time.

Only retrieve memories when you actually need them to answer the user's question.

Available context map for this user:
`;

async function contextNode(state: GraphStateType) {
  const contextMap = await prefetchContextMap();
  return { context_map: contextMap };
}

async function agentNode(state: GraphStateType) {
  const systemMessage = new SystemMessage(
    SYSTEM_PROMPT + (state.context_map || "No contexts available yet.")
  );

  const response = await modelWithTools.invoke([
    systemMessage,
    ...state.messages,
  ]);

  return { messages: [response] };
}

const toolNode = new ToolNode(tools);

const workflow = new StateGraph(GraphState)
  .addNode("context", contextNode)
  .addNode("agent", agentNode)
  .addNode("tools", toolNode)
  .addEdge(START, "context")
  .addEdge("context", "agent")
  .addConditionalEdges("agent", toolsCondition, ["tools", END])
  .addEdge("tools", "agent");

export const graph = workflow.compile();
