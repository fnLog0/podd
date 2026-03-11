import { SarvamAIClient } from "sarvamai";
import * as fs from "fs";
import type { WorkflowState } from "../types";

let client: SarvamAIClient | null = null;

function getClient(): SarvamAIClient {
  if (!client) {
    if (!process.env.SARVAM_API_KEY) {
      throw new Error("SARVAM_API_KEY environment variable is not set");
    }
    client = new SarvamAIClient({
      apiSubscriptionKey: process.env.SARVAM_API_KEY,
    });
  }
  return client;
}

/**
 * Convert speech/audio to text using Sarvam AI
 */
async function speechToText(filePath: string): Promise<string> {
  if (!filePath) {
    throw new Error("Audio file path is required");
  }

  console.log("🎙️  Starting speech-to-text conversion...");
  console.log(`📁 Audio file: ${filePath}`);

  try {
    console.log("📡 Sending audio to Sarvam AI...");

    const response = await getClient().speechToText.transcribe({
      file: fs.createReadStream(filePath),
    });

    console.log("✅ Transcription completed");
    console.log(`📝 Transcribed text: ${response.transcript}`);

    return response.transcript as string;
  } catch (error) {
    console.error("❌ Speech-to-text error:", error);
    throw new Error(
      `Failed to transcribe audio: ${error instanceof Error ? error.message : "Unknown error"}`
    );
  }
}

/**
 * Agent node for speech-to-text
 */
export async function transcribeAgent(state: WorkflowState): Promise<Partial<WorkflowState>> {
  const { audioFilePath } = state;

  if (!audioFilePath) {
    throw new Error("audioFilePath is required in state");
  }

  const text = await speechToText(audioFilePath);

  // Handle empty transcription
  if (!text || text.trim() === "") {
    console.log("⚠️ No speech detected in audio - using fallback text");
    return {
      transcribedText: "Hello, can you hear me?",
      messages: ["User (Speech): [No speech detected - fallback text]"],
    };
  }

  return {
    transcribedText: text,
    messages: [`User (Speech): ${text}`],
  };
}
