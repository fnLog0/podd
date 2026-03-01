import "dotenv/config";
import {
  Annotation,
  StateGraph,
  END,
  START,
  messagesStateReducer,
  MemorySaver,
} from "@langchain/langgraph";
import type { BaseMessage } from "@langchain/core/messages";
import { AIMessage } from "@langchain/core/messages";
import { ToolNode, toolsCondition } from "@langchain/langgraph/prebuilt";
import { ChatOpenAI } from "@langchain/openai";
import { tools, prefetchContextMap } from "./tools/index.js";
import type { UserEventPayload } from "../locusgraph/user.js";
import { systemPrompt } from "../prompts/index.js";
import {
  storeSession,
  storeTurn,
  generateSessionTitle,
} from "../locusgraph/sessions/index.js";
import type { ToolCallRecord } from "../locusgraph/sessions/index.js";
import { setCurrentSession } from "../locusgraph/sessions/tracker.js";

const overwrite = <T>() => ({
  reducer: (_prev: T, next: T) => next,
});

export const GraphState = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: messagesStateReducer,
    default: () => [],
  }),

  user_id: Annotation<string>(overwrite<string>()),

  user_name: Annotation<string>({
    ...overwrite<string>(),
    default: () => "",
  }),

  user: Annotation<UserEventPayload | null>({
    ...overwrite<UserEventPayload | null>(),
    default: () => null,
  }),

  intent: Annotation<string>({
    ...overwrite<string>(),
    default: () => "",
  }),

  user_contexts: Annotation<string>({
    ...overwrite<string>(),
    default: () => "",
  }),

  food_contexts: Annotation<string>({
    ...overwrite<string>(),
    default: () => "",
  }),

  session_contexts: Annotation<string>({
    ...overwrite<string>(),
    default: () => "",
  }),

  session_title: Annotation<string>({
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

async function contextNode(state: GraphStateType) {
  const { user_contexts, food_contexts, session_contexts } =
    await prefetchContextMap();

  let sessionTitle = state.session_title;
  if (!sessionTitle) {
    const firstHuman = state.messages.find((m) => m._getType() === "human");
    if (firstHuman) {
      sessionTitle = generateSessionTitle(String(firstHuman.content));
    }
  }

  let turnNumber = 0;
  for (const m of state.messages) {
    if (m._getType() === "human") turnNumber++;
  }

  if (sessionTitle) {
    setCurrentSession(sessionTitle, turnNumber);
  }

  return {
    user_contexts,
    food_contexts,
    session_contexts,
    session_title: sessionTitle,
  };
}

async function agentNode(state: GraphStateType) {
  const formattedPrompt = await systemPrompt.formatMessages({
    user_contexts: state.user_contexts || "No user contexts available.",
    food_contexts: state.food_contexts || "No food contexts available.",
    session_contexts: state.session_contexts || "No session contexts available.",
  });

  const response = await modelWithTools.invoke([
    ...formattedPrompt,
    ...state.messages,
  ]);

  return { messages: [response] };
}

const toolNode = new ToolNode(tools);

async function logTurnNode(state: GraphStateType) {
  const messages = state.messages;

  // Find where the current turn starts (last HumanMessage)
  let turnStartIdx = 0;
  for (let i = messages.length - 1; i >= 0; i--) {
    if (messages[i]!._getType() === "human") {
      turnStartIdx = i;
      break;
    }
  }

  // Count total HumanMessages = turn number
  let turnNumber = 0;
  for (const m of messages) {
    if (m._getType() === "human") turnNumber++;
  }

  const turnMessages = messages.slice(turnStartIdx);
  const userMessage = String(turnMessages[0]!.content);
  const sessionTitle = state.session_title;

  // Extract AI messages and tool messages from this turn
  const aiMessages = turnMessages.filter((m) => m instanceof AIMessage);
  const toolMessages = turnMessages.filter((m) => m._getType() === "tool");

  const finalAi = aiMessages[aiMessages.length - 1];
  const aiResponse = finalAi ? String(finalAi.content) : "";

  // Extract tool calls with their results
  const toolCalls: ToolCallRecord[] = [];
  for (const aiMsg of aiMessages) {
    if (aiMsg.tool_calls && aiMsg.tool_calls.length > 0) {
      for (const tc of aiMsg.tool_calls) {
        const result = toolMessages.find(
          (tm: BaseMessage) => (tm as any).tool_call_id === tc.id,
        );
        toolCalls.push({
          tool_name: tc.name,
          tool_input: tc.args as Record<string, unknown>,
          tool_output: result ? String(result.content) : "",
        });
      }
    }
  }

  // Store session context on the first turn
  if (turnNumber === 1 && state.user_name) {
    await storeSession({
      name: state.user_name,
      user_id: state.user_id,
      session_title: sessionTitle,
    });
  }

  // Store the turn
  await storeTurn(sessionTitle, {
    turn_number: turnNumber,
    session_title: sessionTitle,
    user_id: state.user_id,
    user_message: userMessage,
    ai_response: aiResponse,
    tool_calls: toolCalls,
    message_count: messages.length,
    logged_at: new Date().toISOString(),
  });

  return { session_title: sessionTitle };
}

const workflow = new StateGraph(GraphState)
  .addNode("context", contextNode)
  .addNode("agent", agentNode)
  .addNode("tools", toolNode)
  .addNode("logTurn", logTurnNode)
  .addEdge(START, "context")
  .addEdge("context", "agent")
  .addConditionalEdges("agent", (state) => {
    const result = toolsCondition(state);
    return result === END ? "logTurn" : "tools";
  }, ["tools", "logTurn"])
  .addEdge("tools", "agent")
  .addEdge("logTurn", END);

const checkpointer = new MemorySaver();
export const graph = workflow.compile({ checkpointer });
