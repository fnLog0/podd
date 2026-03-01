import { config } from "dotenv";
import { resolve } from "path";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load .env from examples directory
config({ path: resolve(__dirname, ".env") });

const BASE_URL = process.env.BASE_URL || "http://localhost:8788";
const TOKEN = process.env.TOKEN || "";

if (!TOKEN) {
  console.error("ERROR: TOKEN environment variable is required");
  console.error("Run dev-login first to get a token, then:");
  console.error("  TOKEN=your_token npx tsx examples/test-voice.ts");
  process.exit(1);
}

async function request(path: string, body: unknown) {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  return response;
}

async function testTextToSpeech() {
  console.log("\n=== Test 1: Text to Speech ===");
  
  const response = await request("/tts", {
    text: "नमस्ते! यह एक टेस्ट है।",
    target_language_code: "hi-IN",
    speaker: "shubh",
    model: "bulbul:v3",
    pace: 1.0,
    output_audio_codec: "mp3",
  });

  if (!response.ok) {
    console.error("Failed:", await response.text());
    return;
  }

  const buffer = await response.arrayBuffer();
  console.log(`Received ${buffer.byteLength} bytes of audio`);
  
  // Save to file
  const fs = await import("fs");
  fs.writeFileSync("examples/output-tts.mp3", Buffer.from(buffer));
  console.log("Saved to examples/output-tts.mp3");
}

async function testChatWithVoice() {
  console.log("\n=== Test 2: Chat with Voice ===");
  
  const response = await request("/tts/chat", {
    message: "What did I eat today?",
    tts_options: {
      target_language_code: "hi-IN",
      speaker: "shubh",
      pace: 1.0,
    },
  });

  if (!response.ok) {
    console.error("Failed:", await response.text());
    return;
  }

  const threadId = response.headers.get("X-Thread-Id");
  const responseText = decodeURIComponent(response.headers.get("X-Response-Text") || "");
  
  console.log("Thread ID:", threadId);
  console.log("Response text:", responseText);

  const buffer = await response.arrayBuffer();
  console.log(`Received ${buffer.byteLength} bytes of audio`);
  
  const fs = await import("fs");
  fs.writeFileSync("examples/output-chat.mp3", Buffer.from(buffer));
  console.log("Saved to examples/output-chat.mp3");
}

async function testStreamChatWithVoice() {
  console.log("\n=== Test 3: Stream Chat with Voice ===");
  
  const response = await request("/tts/chat/stream", {
    message: "Tell me a short story about a brave cat",
    tts_options: {
      target_language_code: "hi-IN",
      speaker: "shubh",
      pace: 1.0,
      output_audio_codec: "mp3",
    },
  });

  if (!response.ok) {
    console.error("Failed:", await response.text());
    return;
  }

  const chunks: Uint8Array[] = [];
  const reader = response.body?.getReader();
  
  if (!reader) {
    console.error("No response body");
    return;
  }

  console.log("Streaming audio...");
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    console.log(`Received ${value.length} bytes (total: ${chunks.reduce((a, c) => a + c.length, 0)})`);
  }

  const totalBytes = chunks.reduce((a, c) => a + c.length, 0);
  console.log(`\nTotal received: ${totalBytes} bytes`);

  const fs = await import("fs");
  const buffer = Buffer.concat(chunks);
  const filepath = "examples/output-stream.mp3";
  fs.writeFileSync(filepath, buffer);
  console.log(`Saved to ${filepath}`);
  
  return filepath;
}

async function playAudioFile(filepath: string) {
  const fs = await import("fs");
  const fullPath = resolve(__dirname, "..", filepath);
  
  if (!fs.existsSync(fullPath)) {
    console.error(`File not found: ${fullPath}`);
    return;
  }

  console.log(`\n🔊 Playing: ${fullPath}`);
  
  const { execSync } = await import("child_process");
  const platform = process.platform;
  
  try {
    if (platform === "darwin") {
      execSync(`afplay "${fullPath}"`, { stdio: "inherit" });
    } else if (platform === "linux") {
      execSync(`mpg123 "${fullPath}"`, { stdio: "inherit" });
    } else if (platform === "win32") {
      execSync(`powershell -c (New-Object Media.SoundPlayer "${fullPath}").PlaySync()`, { stdio: "inherit" });
    } else {
      console.log("Auto-play not supported. Open the file manually:");
      console.log(`  ${fullPath}`);
    }
  } catch (err) {
    console.log("Could not auto-play audio. Open the file manually:");
    console.log(`  ${fullPath}`);
    console.log("\nOn macOS: open " + fullPath);
  }
}

async function main() {
  const test = process.argv[2] || "all";
  
  console.log("Base URL:", BASE_URL);
  console.log("Token:", TOKEN.slice(0, 8) + "...");
  
  try {
    if (test === "tts" || test === "all") {
      await testTextToSpeech();
    }
    
    if (test === "chat" || test === "all") {
      await testChatWithVoice();
    }
    
    if (test === "stream" || test === "all") {
      const filepath = await testStreamChatWithVoice();
      if (filepath) {
        console.log("\n🔊 Playing audio...");
        await playAudioFile(filepath);
      }
    }
    
    if (test === "play") {
      await playAudioFile("examples/output-stream.mp3");
    }
    
    console.log("\n✅ Tests completed!");
    
  } catch (err) {
    console.error("Error:", err);
    process.exit(1);
  }
}

main();
