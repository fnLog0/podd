import { transcribeAgent } from "../agents/speech-to-text";
import { aiProcessorAgent } from "../agents/ai-processor";
import { textToSpeechAgent } from "../agents/text-to-speech";
import type { WorkflowState } from "../types";

/**
 * Run the complete multi-agent workflow
 * - Agent 1: Sarvam Speech-to-Text
 * - Agent 2: Gemini AI Processor
 * - Agent 3: Text-to-Speech (TTS)
 */
export async function runWorkflow(audioFilePath: string): Promise<WorkflowState> {
  console.log("🚀 Starting multi-agent workflow...\n");

  const state: WorkflowState = {
    audioFilePath,
    transcribedText: "",
    messages: [],
    aiResponse: "",
    ttsAudioPath: "",
  };

  console.log("📞 Agent 1: Transcribing audio...");
  const transcribeResult = await transcribeAgent(state);
  const state1 = { ...state, ...transcribeResult } as WorkflowState;

  console.log("🤖 Agent 2: Processing with AI...");
  const processResult = await aiProcessorAgent(state1);
  const state2 = { ...state1, ...processResult } as WorkflowState;

  console.log("🔊 Agent 3: Converting response to speech...");
  const ttsResult = await textToSpeechAgent(state2);
  const state3 = { ...state2, ...ttsResult } as WorkflowState;

  return state3;
}
