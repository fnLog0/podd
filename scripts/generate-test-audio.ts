import * as fs from "node:fs";
import * as path from "node:path";

// Audio parameters
const SAMPLE_RATE = 16000;
const DURATION = 3; // seconds
const NUM_CHANNELS = 1;
const BITS_PER_SAMPLE = 16;
const FREQUENCY = 440; // A4 note

function generateTonePCM(): Buffer {
  const numSamples = SAMPLE_RATE * DURATION;
  const samples = new Int16Array(numSamples);

  for (let i = 0; i < numSamples; i++) {
    const t = i / SAMPLE_RATE;
    // Create a simple 440Hz sine wave with fading
    const amplitude = 0.5 * (1 - i / numSamples); // Fade out
    const sample = Math.floor(amplitude * 32767 * Math.sin(2 * Math.PI * FREQUENCY * t));
    samples[i] = sample;
  }

  return Buffer.from(samples.buffer);
}

function createWavFile(pcmData: Buffer): Buffer {
  const dataSize = pcmData.length;
  const byteRate = (SAMPLE_RATE * NUM_CHANNELS * BITS_PER_SAMPLE) / 8;
  const blockAlign = (NUM_CHANNELS * BITS_PER_SAMPLE) / 8;
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
  header.writeUInt16LE(NUM_CHANNELS, 22);
  header.writeUInt32LE(SAMPLE_RATE, 24);
  header.writeUInt32LE(byteRate, 28);
  header.writeUInt16LE(blockAlign, 32);
  header.writeUInt16LE(BITS_PER_SAMPLE, 34);

  // data chunk
  header.write("data", 36);
  header.writeUInt32LE(dataSize, 40);

  return Buffer.concat([header, pcmData]);
}

async function generateTestAudio(): Promise<void> {
  console.log("Generating test audio...");

  const pcmData = generateTonePCM();
  const wavData = createWavFile(pcmData);

  const outputPath = path.join(process.cwd(), "test-files", "test-audio.wav");
  fs.writeFileSync(outputPath, wavData);

  console.log(`Generated test-files/test-audio.wav`);
  console.log(`   Duration: ${DURATION}s, Sample Rate: ${SAMPLE_RATE}Hz`);
  console.log(`   Tone: ${FREQUENCY}Hz (A4 note)`);
  console.log(`   Samples: ${pcmData.length / 2}`);
}

generateTestAudio().catch(console.error);
