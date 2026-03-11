import { createServer } from 'node:http';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = Number(process.env.PORT || 3000);
const HOST = process.env.HOST || '0.0.0.0';
const uploadsDir = path.join(__dirname, 'uploads');
const audioDir = path.join(__dirname, 'audio');
const outputDir = path.join(audioDir, 'output');

function getLocalIps() {
  const interfaces = os.networkInterfaces();
  const ips = [];

  for (const entries of Object.values(interfaces)) {
    for (const entry of entries || []) {
      if (entry.family === 'IPv4' && !entry.internal) {
        ips.push(entry.address);
      }
    }
  }

  return ips;
}

function json(res, statusCode, payload) {
  const body = JSON.stringify(payload, null, 2);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

function wavTone({ seconds = 1.5, sampleRate = 16000, frequency = 440, amplitude = 0.3 }) {
  const totalSamples = Math.floor(seconds * sampleRate);
  const channels = 1;
  const bitsPerSample = 16;
  const bytesPerSample = bitsPerSample / 8;
  const dataSize = totalSamples * channels * bytesPerSample;
  const buffer = Buffer.alloc(44 + dataSize);

  buffer.write('RIFF', 0);
  buffer.writeUInt32LE(36 + dataSize, 4);
  buffer.write('WAVE', 8);
  buffer.write('fmt ', 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(channels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * channels * bytesPerSample, 28);
  buffer.writeUInt16LE(channels * bytesPerSample, 32);
  buffer.writeUInt16LE(bitsPerSample, 34);
  buffer.write('data', 36);
  buffer.writeUInt32LE(dataSize, 40);

  for (let i = 0; i < totalSamples; i++) {
    const sample = Math.sin((2 * Math.PI * frequency * i) / sampleRate);
    const value = Math.max(-1, Math.min(1, sample * amplitude));
    buffer.writeInt16LE(Math.round(value * 32767), 44 + (i * bytesPerSample));
  }

  return buffer;
}

async function ensureDirs() {
  await fs.mkdir(uploadsDir, { recursive: true });
  await fs.mkdir(outputDir, { recursive: true });
}

async function handleUpload(req, res) {
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(chunk);
  }

  const audioBuffer = Buffer.concat(chunks);
  if (audioBuffer.length === 0) {
    json(res, 400, { success: false, error: 'Empty upload body' });
    return;
  }

  const stamp = Date.now();
  const uploadName = `recording-${stamp}.pcm`;
  const wavName = `tts-${stamp}.wav`;

  await fs.writeFile(path.join(uploadsDir, uploadName), audioBuffer);
  await fs.writeFile(path.join(outputDir, wavName), wavTone({}));

  json(res, 200, {
    success: true,
    transcript: `Received ${audioBuffer.length} bytes of PCM audio`,
    aiResponse: 'Test server response from local mock backend',
    ttsAudioPath: `/audio/output/${wavName}`,
    debug: {
      uploadedFile: `/uploads/${uploadName}`,
      bytes: audioBuffer.length,
    },
  });
}

async function serveFile(res, filePath, contentType) {
  try {
    const data = await fs.readFile(filePath);
    res.writeHead(200, {
      'Content-Type': contentType,
      'Content-Length': data.length,
      'Cache-Control': 'no-store',
    });
    res.end(data);
  } catch {
    json(res, 404, { success: false, error: 'File not found' });
  }
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`);

  if (req.method === 'GET' && url.pathname === '/') {
    json(res, 200, {
      success: true,
      service: 'podd-esp32-test-server',
      endpoints: {
        health: 'GET /health',
        upload: 'POST /upload',
        audio: 'GET /audio/output/<file>.wav',
      },
    });
    return;
  }

  if (req.method === 'GET' && url.pathname === '/health') {
    json(res, 200, { success: true, status: 'ok' });
    return;
  }

  if (req.method === 'POST' && url.pathname === '/upload') {
    await handleUpload(req, res);
    return;
  }

  if (req.method === 'GET' && url.pathname.startsWith('/audio/')) {
    const relativePath = path.normalize(url.pathname.replace(/^\/audio\//, ''));
    const filePath = path.join(audioDir, relativePath);
    await serveFile(res, filePath, 'audio/wav');
    return;
  }

  if (req.method === 'GET' && url.pathname.startsWith('/uploads/')) {
    const relativePath = path.normalize(url.pathname.replace(/^\/uploads\//, ''));
    const filePath = path.join(uploadsDir, relativePath);
    await serveFile(res, filePath, 'application/octet-stream');
    return;
  }

  json(res, 404, { success: false, error: 'Route not found' });
});

await ensureDirs();
server.listen(PORT, HOST, () => {
  console.log(`Test server listening on http://${HOST}:${PORT}`);
  for (const ip of getLocalIps()) {
    console.log(`LAN URL: http://${ip}:${PORT}`);
  }
  console.log('POST /upload and GET /audio/output/<file>.wav are ready');
});
