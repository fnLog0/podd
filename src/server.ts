import express, { Request, Response } from "express";
import cors from "cors";
import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";
import { runWorkflow } from "./graph/workflow";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const TEMP_DIR = process.env.TEMP_DIR
  ? path.join(process.cwd(), process.env.TEMP_DIR)
  : path.join(__dirname, "../temp");
const TTS_OUTPUT_DIR = process.env.TTS_OUTPUT_DIR
  ? path.join(process.cwd(), process.env.TTS_OUTPUT_DIR)
  : path.join(__dirname, "../tts-output");

// Ensure temp directory exists
if (!fs.existsSync(TEMP_DIR)) {
  fs.mkdirSync(TEMP_DIR, { recursive: true });
}

// Ensure TTS output directory exists (including output subdirectory)
if (!fs.existsSync(TTS_OUTPUT_DIR)) {
  fs.mkdirSync(TTS_OUTPUT_DIR, { recursive: true });
}
// Ensure output subdirectory exists for TTS files
const TTS_OUTPUT_SUBDIR = path.join(TTS_OUTPUT_DIR, "output");
if (!fs.existsSync(TTS_OUTPUT_SUBDIR)) {
  fs.mkdirSync(TTS_OUTPUT_SUBDIR, { recursive: true });
}

app.use(cors());
app.use(express.raw({ type: "application/octet-stream", limit: "10mb" }));

// Upload endpoint - receives audio from ESP32
app.post("/upload", async (req: Request, res: Response) => {
  let audioPath: string | null = null;
  let ttsPath: string | null = null;

  try {
    // Validate request body
    if (!req.body || req.body.length === 0) {
      return res.status(400).json({
        success: false,
        error: "No audio data received",
      });
    }

    console.log("📥 Received audio from ESP32");
    console.log(`📊 Size: ${req.body.length} bytes`);

    // Save audio to temporary WAV file
    audioPath = path.join(TEMP_DIR, "uploaded-audio.wav");
    const wavData = createWavFile(req.body);
    fs.writeFileSync(audioPath, wavData);

    console.log(`💾 Saved to: ${audioPath}`);

    // Run workflow
    const result = await runWorkflow(audioPath);

    // Clean up uploaded audio
    if (audioPath && fs.existsSync(audioPath)) {
      fs.unlinkSync(audioPath);
    }

    // Store TTS path for cleanup later
    ttsPath = result.ttsAudioPath;

    // Validate result
    if (!result.transcribedText || !result.aiResponse) {
      throw new Error("Invalid result from workflow");
    }

    // Return results
    res.json({
      success: true,
      transcript: result.transcribedText,
      aiResponse: result.aiResponse,
      conversation: result.messages,
      ttsAudioPath: result.ttsAudioPath,
    });
  } catch (error) {
    console.error("❌ Error:", error);

    // Clean up files on error
    if (audioPath && fs.existsSync(audioPath)) {
      fs.unlinkSync(audioPath);
    }

    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

// Download TTS audio endpoint - for ESP32 to play response
app.get("/audio/:filename", (req: Request, res: Response) => {
  try {
    const filename = req.params.filename;

    // Sanitize filename to prevent directory traversal
    if (filename.includes("..") || filename.includes("\\")) {
      console.log(`❌ Invalid filename detected: ${filename}`);
      return res.status(400).json({
        success: false,
        error: "Invalid filename",
      });
    }

    const audioPath = path.join(TTS_OUTPUT_DIR, filename);

    if (!fs.existsSync(audioPath)) {
      console.log(`❌ Audio file not found: ${audioPath}`);
      console.log(`🔍 Looking in directory: ${TTS_OUTPUT_DIR}`);
      try {
        const files = fs.readdirSync(TTS_OUTPUT_DIR);
        console.log(`📂 Available files: ${files.join(", ")}`);
      } catch (e) {
        console.log(`❌ Could not list directory: ${e}`);
      }
      return res.status(404).json({
        success: false,
        error: "Audio file not found",
      });
    }

    console.log(`📤 Serving audio file: ${filename}`);
    console.log(`📍 Full path: ${audioPath}`);
    res.sendFile(audioPath);
  } catch (error) {
    console.error("❌ Error serving audio:", error);
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

// Health check
app.get("/", (req: Request, res: Response) => {
  res.json({
    status: "running",
    message: "Audio capture server ready",
    endpoints: {
      upload: "POST /upload - Upload audio for processing",
      audio: "GET /audio/:filename - Download TTS audio file",
      health: "GET / - Health check",
    },
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📡 Upload endpoint: http://localhost:${PORT}/upload`);
});

// Convert raw I2S audio data to WAV format
function createWavFile(pcmData: Buffer): Buffer {
  if (!pcmData || pcmData.length === 0) {
    throw new Error("Invalid PCM data: empty or null");
  }

  const sampleRate = 16000;
  const numChannels = 1;
  const bitsPerSample = 16;
  const dataSize = pcmData.length;
  const byteRate = (sampleRate * numChannels * bitsPerSample) / 8;
  const blockAlign = (numChannels * bitsPerSample) / 8;
  const fileSize = 36 + dataSize;

  const header = Buffer.alloc(44);

  // RIFF header
  header.write("RIFF", 0);
  header.writeUInt32LE(fileSize, 4);
  header.write("WAVE", 8);

  // fmt chunk
  header.write("fmt ", 12);
  header.writeUInt32LE(16, 16); // Subchunk1Size
  header.writeUInt16LE(1, 20); // AudioFormat (PCM)
  header.writeUInt16LE(numChannels, 22);
  header.writeUInt32LE(sampleRate, 24);
  header.writeUInt32LE(byteRate, 28);
  header.writeUInt16LE(blockAlign, 32);
  header.writeUInt16LE(bitsPerSample, 34);

  // data chunk
  header.write("data", 36);
  header.writeUInt32LE(dataSize, 40);

  return Buffer.concat([header, pcmData]);
}
