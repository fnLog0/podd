import "dotenv/config";
import { HumanMessage } from "@langchain/core/messages";
import { graph } from "./workflows/graph.js";
import { bootstrapUser } from "./locusgraph/bootstrap.js";

async function main() {
  console.log("[main] Bootstrapping user...\n");
  await bootstrapUser({
    name: "nasim",
    user_id: "u123",
    email: "nasim@example.com",
    age: 30,
    gender: "male",
    height_cm: 175,
    weight_kg: 70,
    activity_level: "moderate",
    dietary_preferences: ["none"],
    allergies: [],
    medical_conditions: [],
    daily_calorie_goal: 2200,
  });

  const prompts = [
    "I had 2 scrambled eggs and a cup of green tea for breakfast",
    "What did I eat today?",
    "Am I getting enough protein?",
  ];

  for (const prompt of prompts) {
    console.log("\n" + "=".repeat(60));
    console.log(`[main] User: "${prompt}"`);
    console.log("=".repeat(60));

    const result = await graph.invoke({
      messages: [new HumanMessage(prompt)],
      user_id: "u123",
    });

    const lastMessage = result.messages.at(-1);
    console.log("\n[main] Agent response:", lastMessage?.content);
    console.log(`[main] Total messages in chain: ${result.messages.length}`);
    console.log(`[main] Context map loaded: ${result.context_map ? "yes" : "no"}`);
  }
}

main().catch(console.error);
