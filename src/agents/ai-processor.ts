import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import type { WorkflowState } from "../types";

let model: ChatGoogleGenerativeAI | null = null;

function getModel(): ChatGoogleGenerativeAI {
  if (!model) {
    if (!process.env.GOOGLE_API_KEY) {
      throw new Error("GOOGLE_API_KEY environment variable is not set");
    }
    model = new ChatGoogleGenerativeAI({
      model: "gemini-2.5-flash",
      temperature: 0.7,
      apiKey: process.env.GOOGLE_API_KEY,
    });
  }
  return model;
}

/**
 * Process text and generate AI response using Google Gemini
 */
export async function processWithAI(input: string): Promise<string> {
  console.log("🤖 Processing text with Gemini AI...");
  console.log(`📝 Input: ${input}`);

  try {
    const response = await getModel().invoke(input);

    console.log("✅ AI response generated");
    console.log(`🤖 Response: ${response.content}`);

    return response.content as string;
  } catch (error) {
    console.error("❌ AI processing error:", error);
    throw new Error(
      `Failed to process with AI: ${error instanceof Error ? error.message : "Unknown error"}`
    );
  }
}

/**
 * Agent node for AI processing
 */
export async function aiProcessorAgent(state: WorkflowState): Promise<Partial<WorkflowState>> {
  const { transcribedText, messages } = state;

  if (!transcribedText) {
    throw new Error("transcribedText is required in state");
  }

  const response = await processWithAI(transcribedText);

  return {
    aiResponse: response,
    messages: [...messages, `AI: ${response}`],
  };
}
