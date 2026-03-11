import { SarvamAIClient } from "sarvamai";
import * as fs from "fs";
import * as path from "path";
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

// TTS output directory - use output subfolder
const TTS_OUTPUT_DIR = process.env.TTS_OUTPUT_DIR
  ? path.join(process.cwd(), process.env.TTS_OUTPUT_DIR)
  : path.join(process.cwd(), "tts-output", "output");

// Ensure TTS output directory exists
function ensureOutputDir() {
  if (!fs.existsSync(TTS_OUTPUT_DIR)) {
    fs.mkdirSync(TTS_OUTPUT_DIR, { recursive: true });
  }
  console.log(`📁 TTS output directory: ${TTS_OUTPUT_DIR}`);
}

/**
 * Convert text to speech using Sarvam AI TTS
 */
async function textToSpeech(text: string): Promise<string> {
  if (!text || text.trim().length === 0) {
    throw new Error("Text is required for text-to-speech conversion");
  }

  console.log("🔊 Starting text-to-speech conversion...");
  console.log(`📝 Input text: ${text}`);

  ensureOutputDir();

  try {
    // Generate output filename with timestamp
    const timestamp = Date.now();
    const outputFilename = `response_${timestamp}.wav`;
    const outputPath = path.join(TTS_OUTPUT_DIR, outputFilename);

    console.log("📡 Sending text to Sarvam AI TTS service...");
    console.log(`💾 Output will be saved to: ${outputPath}`);

    // Use Sarvam AI TTS API
    const response = await getClient().textToSpeech.convert({
      text: text.trim(), // Trim whitespace
      target_language_code: "en-IN",
      model: "bulbul:v3",
      speaker: "shubh",
      speech_sample_rate: 16000,
    });

    // Extract base64 audio from response
    if (response.audios && response.audios.length > 0) {
      const audioBase64 = response.audios[0];
      if (!audioBase64 || audioBase64.length === 0) {
        throw new Error("Empty audio data received from TTS API");
      }
      // Decode base64 to buffer
      const audioBuffer = Buffer.from(audioBase64, "base64");
      if (audioBuffer.length === 0) {
        throw new Error("Failed to decode audio data from base64");
      }
      // Save to file
      fs.writeFileSync(outputPath, audioBuffer);
      console.log("✅ Text-to-speech conversion completed");
      console.log(`🎵 Audio file created: ${outputPath}`);
      console.log(`📊 Audio size: ${audioBuffer.length} bytes`);
      return outputPath;
    } else {
      throw new Error("No audio received from TTS API");
    }
  } catch (error) {
    console.error("❌ Text-to-speech error:", error);
    throw new Error(
      `Failed to convert text to speech: ${error instanceof Error ? error.message : "Unknown error"}`
    );
  }
}

/**
 * Agent node for text-to-speech
 */
export async function textToSpeechAgent(state: WorkflowState): Promise<Partial<WorkflowState>> {
  const { aiResponse } = state;

  if (!aiResponse) {
    throw new Error("aiResponse is required in state for TTS conversion");
  }

  const audioFilePath = await textToSpeech(aiResponse);

  return {
    ttsAudioPath: audioFilePath,
    messages: [...state.messages, `TTS: Audio generated for response`],
  };
}
