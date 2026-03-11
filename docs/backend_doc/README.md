# Backend Setup

Node.js backend with Sarvam STT and Google Gemini AI.

## Prerequisites

- Node.js 18+
- pnpm package manager
- Sarvam AI API key
- Google AI API key

## Installation

```bash
# Install dependencies
pnpm install
```

## Environment Setup

Create `.env` file in project root:

```env
SARVAM_API_KEY=your_sarvam_api_key
GOOGLE_API_KEY=your_google_api_key
AUDIO_FILE_PATH=./audio-sample.wav
PORT=3000
```

### Get API Keys

**Sarvam AI:**

1. Go to https://www.sarvam.ai/
2. Sign up and get your API key

**Google AI:**

1. Go to https://aistudio.google.com/
2. Create a project and get API key

## Running the Backend

### File-Based Mode (Test with audio file)

```bash
# Place your audio file as ./audio-sample.wav
pnpm start
```

### Server Mode (For ESP32)

```bash
pnpm server
```

Server runs on: http://localhost:3000

## Project Structure

```
src/
├── agents/
│   ├── speech-to-text.ts    # Sarvam AI STT
│   ├── ai-processor.ts      # Gemini AI processor
│   └── text-to-speech.ts    # Text-to-Speech agent
├── graph/
│   └── workflow.ts          # Multi-agent workflow
├── types.ts                 # TypeScript types
├── index.ts                 # File-based entry point
└── server.ts                # Express server for ESP32
```

## API Endpoints

### POST /upload

Upload audio from ESP32 for processing.

**Request:**

- Content-Type: `application/octet-stream`
- Body: Raw audio data

**Response:**

```json
{
  "success": true,
  "transcript": "transcribed text",
  "aiResponse": "AI response",
  "conversation": ["User: ...", "AI: ..."]
}
```

### GET /

Health check endpoint.

**Response:**

```json
{
  "status": "running",
  "message": "Audio capture server ready"
}
```

## Workflow

The backend runs a multi-agent system:

```
Audio File → Sarvam STT → Text → Gemini AI → Response
```

**Agent 1: Sarvam Speech-to-Text**

- Transcribes audio to text
- Uses Sarvam AI API

**Agent 2: Gemini AI Processor**

- Processes transcribed text
- Generates intelligent responses
- Uses Google Gemini AI

## Troubleshooting

### API Key Not Found

```
Error: SARVAM_API_KEY environment variable is not set
```

**Solution:** Add your API keys to `.env` file

### Audio File Not Found

```
Error: audioFilePath is required in state
```

**Solution:** Set `AUDIO_FILE_PATH` in `.env` or ensure audio file exists

### Server Not Starting

**Solution:**

- Check port 3000 is not in use
- Verify dependencies are installed (`pnpm install`)
- Check Node.js version (18+)

### No Transcript from Audio

**Solution:**

- Ensure audio is in WAV format
- Check audio quality (not too quiet)
- Verify Sarvam API key is valid

## Testing

### Test File-Based Workflow

```bash
# Place test audio file
echo "test" > audio-sample.wav

# Run
pnpm start
```

### Test Server with cURL

```bash
# Start server first
pnpm server

# In another terminal
curl -X POST http://localhost:3000/upload \
  -H "Content-Type: application/octet-stream" \
  --data-binary @your-audio-file.wav
```

## Development

```bash
# Format code
pnpm format

# Build TypeScript
pnpm build
```

## Audio Format Requirements

- **Format:** WAV
- **Sample Rate:** 16000 Hz
- **Channels:** Mono
- **Bit Depth:** 16-bit
