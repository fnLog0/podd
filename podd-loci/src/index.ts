import "dotenv/config";
import { HumanMessage } from "@langchain/core/messages";
import { graph } from "./workflows/graph.js";
import { bootstrapUser } from "./locusgraph/bootstrap.js";
import { prefetchContextMap } from "./workflows/tools/index.js";

const USER = {
  name: "nasim",
  user_id: "u123",
  email: "nasim@example.com",
  age: 30,
  gender: "male" as const,
  height_cm: 175,
  weight_kg: 70,
  activity_level: "moderate" as const,
  dietary_preferences: ["none" as const],
  allergies: [],
  medical_conditions: [],
  daily_calorie_goal: 2200,
};

function divider(label: string) {
  console.log("\n" + "=".repeat(60));
  console.log(`  ${label}`);
  console.log("=".repeat(60));
}

async function printContextMap() {
  const { user_contexts, food_contexts, session_contexts } =
    await prefetchContextMap();
  console.log("\n--- User Contexts ---");
  console.log(user_contexts);
  console.log("\n--- Food Contexts ---");
  console.log(food_contexts);
  console.log("\n--- Session Contexts ---");
  console.log(session_contexts);
}

async function runTurn(
  prompt: string,
  threadConfig: { configurable: { thread_id: string } },
) {
  console.log(`\n[user] "${prompt}"`);

  const result = await graph.invoke(
    {
      messages: [new HumanMessage(prompt)],
      user_id: USER.user_id,
      user_name: USER.name,
    },
    threadConfig,
  );

  const lastMessage = result.messages.at(-1);
  console.log(`[agent] ${lastMessage?.content}`);
  console.log(`[info] messages: ${result.messages.length} | session: ${result.session_title}`);

  return result;
}

async function main() {
  // ── Bootstrap ──
  divider("BOOTSTRAP");
  await bootstrapUser(USER);

  // ── Session 1: Food logging ──
  divider("SESSION 1 — Log food items");
  const session1 = { configurable: { thread_id: "session_food_log" } };

  await runTurn(
    "I had 2 scrambled eggs and a cup of green tea for breakfast",
    session1,
  );

  await runTurn(
    "For lunch I ate a grilled chicken salad with olive oil dressing",
    session1,
  );

  await runTurn(
    "I just had a banana and some almonds as a snack",
    session1,
  );

  // ── Session 2: Query food history ──
  divider("SESSION 2 — Query food & nutrition");
  const session2 = { configurable: { thread_id: "session_food_query" } };

  await runTurn("What did I eat today?", session2);

  await runTurn("How much protein have I had so far?", session2);

  await runTurn(
    "Am I on track with my 2200 calorie goal?",
    session2,
  );

  // ── Final context map ──
  divider("FINAL CONTEXT MAP");
  await printContextMap();
}

main().catch(console.error);
