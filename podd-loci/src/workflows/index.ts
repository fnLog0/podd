import { HumanMessage } from "@langchain/core/messages";
import { graph } from "./graph.js";

export { graph } from "./graph.js";
export { tools } from "./tools/index.js";

export async function runWorkflow(
  userMessage: string,
  threadId = "default",
) {
  const result = await graph.invoke(
    { messages: [new HumanMessage(userMessage)] },
    { configurable: { thread_id: threadId } },
  );

  return result.messages.at(-1)?.content ?? "";
}
