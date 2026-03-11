import * as dotenv from "dotenv";
import { runWorkflow } from "./graph/workflow";

dotenv.config();

async function main() {
  console.log("🎤 Audio Processing System Started!");

  const audioFilePath = process.env.AUDIO_FILE_PATH;

  if (!audioFilePath) {
    console.error("❌ AUDIO_FILE_PATH environment variable is not set");
    console.log("💡 Set it in your .env file: AUDIO_FILE_PATH=./audio-sample.wav");
    process.exit(1);
  }

  console.log(`📁 Processing audio file: ${audioFilePath}`);

  try {
    const result = await runWorkflow(audioFilePath);

    console.log("\n✅ Processing Complete!");
    console.log(`📝 Transcript: ${result.transcribedText}`);
    console.log(`🤖 AI Response: ${result.aiResponse}`);
    console.log(`🎵 TTS Audio: ${result.ttsAudioPath}`);
    console.log(`\n💬 Conversation:`);
    result.messages.forEach((msg) => console.log(`  ${msg}`));
  } catch (error) {
    console.error("❌ Error:", error);
    process.exit(1);
  }
}

main().catch(console.error);
