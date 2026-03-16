import { createServer } from 'node:http';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

import { logRequest } from './lib/logger.mjs';
import { wavTone } from './lib/audio-gen.mjs';
import { isSafePath, validateUploadSize, MAX_UPLOAD_BYTES } from './lib/validation.mjs';

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

async function ensureDirs() {
  await fs.mkdir(uploadsDir, { recursive: true });
  await fs.mkdir(outputDir, { recursive: true });
}

async function handleUpload(req, res) {
  const chunks = [];
  let totalBytes = 0;

  for await (const chunk of req) {
    totalBytes += chunk.length;
    if (totalBytes > MAX_UPLOAD_BYTES) {
      json(res, 413, { success: false, error: `Upload too large (max ${MAX_UPLOAD_BYTES} bytes)` });
      return;
    }
    chunks.push(chunk);
  }

  const audioBuffer = Buffer.concat(chunks);
  const sizeCheck = validateUploadSize(audioBuffer.length);
  if (!sizeCheck.ok) {
    json(res, 400, { success: false, error: sizeCheck.error });
    return;
  }

  const stamp = Date.now();
  const uploadName = `recording-${stamp}.pcm`;
  const wavName = `tts-${stamp}.wav`;

  await fs.writeFile(path.join(uploadsDir, uploadName), audioBuffer);
  await fs.writeFile(path.join(outputDir, wavName), wavTone());

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
  const startTime = Date.now();
  let statusCode = 200;

  try {
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
      json(res, 200, { success: true, status: 'ok', uptime: process.uptime() });
      return;
    }

    if (req.method === 'POST' && url.pathname === '/upload') {
      await handleUpload(req, res);
      return;
    }

    if (req.method === 'GET' && url.pathname.startsWith('/audio/')) {
      const relativePath = url.pathname.replace(/^\/audio\//, '');
      if (!isSafePath(relativePath)) {
        statusCode = 400;
        json(res, 400, { success: false, error: 'Invalid path' });
        return;
      }
      const filePath = path.join(audioDir, path.normalize(relativePath));
      if (!filePath.startsWith(audioDir)) {
        statusCode = 403;
        json(res, 403, { success: false, error: 'Forbidden' });
        return;
      }
      await serveFile(res, filePath, 'audio/wav');
      return;
    }

    if (req.method === 'GET' && url.pathname.startsWith('/uploads/')) {
      const relativePath = url.pathname.replace(/^\/uploads\//, '');
      if (!isSafePath(relativePath)) {
        statusCode = 400;
        json(res, 400, { success: false, error: 'Invalid path' });
        return;
      }
      const filePath = path.join(uploadsDir, path.normalize(relativePath));
      if (!filePath.startsWith(uploadsDir)) {
        statusCode = 403;
        json(res, 403, { success: false, error: 'Forbidden' });
        return;
      }
      await serveFile(res, filePath, 'application/octet-stream');
      return;
    }

    statusCode = 404;
    json(res, 404, { success: false, error: 'Route not found' });
  } catch (err) {
    statusCode = 500;
    console.error('Unhandled error:', err);
    json(res, 500, { success: false, error: 'Internal server error' });
  } finally {
    logRequest(req, res.statusCode || statusCode, startTime);
  }
});

await ensureDirs();
server.listen(PORT, HOST, () => {
  console.log(`Test server listening on http://${HOST}:${PORT}`);
  for (const ip of getLocalIps()) {
    console.log(`LAN URL: http://${ip}:${PORT}`);
  }
  console.log('POST /upload and GET /audio/output/<file>.wav are ready');
});
