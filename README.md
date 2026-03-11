# Z PODD - Multi-Agent Audio Processing System

A voice-enabled multi-agent system combining ESP32 audio capture, Sarvam AI speech-to-text, and Google Gemini AI for intelligent responses.

## 🎯 Features

- **Voice Input**: Capture live audio via ESP32 + INMP441 microphone
- **Speech-to-Text**: Convert audio to text using Sarvam AI
- **AI Processing**: Generate intelligent responses with Google Gemini AI
- **Dual Modes**: File-based or live ESP32 audio capture
- **REST API**: Server endpoint for audio upload and processing

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- pnpm
- Sarvam AI API key
- Google AI API key

### Installation

```bash
# Install dependencies
pnpm install

# Configure environment variables
cp .env.example .env

# Edit .env and add your API keys
# SARVAM_API_KEY=your_sarvam_api_key
# GOOGLE_API_KEY=your_google_api_key
```

### Usage

#### File-Based Workflow

```bash
# Set your audio file path in .env
AUDIO_FILE_PATH=./test-audio.wav

# Run the workflow
pnpm start
```

#### Server Workflow (ESP32)

```bash
# Start the server
pnpm server

# The server will be available at http://localhost:3000
# Upload audio to: http://localhost:3000/upload
```

## 📁 Project Structure

```
z_podd/
├── src/
│   ├── agents/
│   │   ├── speech-to-text.ts    # Sarvam AI STT agent
│   │   └── ai-processor.ts      # Gemini AI agent
│   ├── graph/
│   │   └── workflow.ts          # Multi-agent workflow
│   ├── types.ts                 # Type definitions
│   ├── index.ts                 # File-based CLI entry
│   └── server.ts                # Express server
├── esp32/
│   └── esp32.ino                # ESP32 firmware
├── docs/
│   ├── hardware/                # Hardware documentation
│   ├── backend_doc/             # Backend documentation
│   └── README.md                # Documentation index
└── package.json
```

## 🔌 Hardware Setup (ESP32 + INMP441)

### Wiring

| INMP441 | ESP32   |
| ------- | ------- |
| VDD     | 3.3V    |
| GND     | GND     |
| SCK     | GPIO 14 |
| WS      | GPIO 15 |
| SD      | GPIO 16 |
| L/R     | GND     |

### ESP32 Setup

1. Install Arduino IDE
2. Add ESP32 board support
3. Upload code to ESP32 (WiFi and server already configured)
4. Connect hardware as shown above

For detailed instructions, see [Hardware Setup Guide](docs/hardware/README.md)

## 📡 API Endpoints

### POST /upload

Upload audio data for processing.

**Content-Type**: `application/octet-stream`

**Response**:

```json
{
  "success": true,
  "transcript": "transcribed text",
  "aiResponse": "AI generated response",
  "conversation": ["User: ...", "AI: ..."]
}
```

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md) - Get started in 10 minutes
- [Hardware Setup](docs/hardware/README.md) - ESP32 + INMP441 hardware setup
- [Backend Setup](docs/backend_doc/README.md) - Node.js backend with Sarvam + Gemini
- [Documentation Index](docs/README.md) - All documentation

## 🔧 Configuration

### Environment Variables

- `SARVAM_API_KEY` - Sarvam AI subscription key (required)
- `GOOGLE_API_KEY` - Google AI API key (required)
- `AUDIO_FILE_PATH` - Path to audio file for file-based mode (optional)
- `PORT` - Server port (default: 3000)

## 🛠️ Development

```bash
# Start development server
pnpm dev:server

# Run file-based workflow
pnpm dev

# Format code
pnpm format

# Build TypeScript
pnpm build
```

## 🐛 Troubleshooting

- ESP32 issues → [Hardware Setup Guide](docs/hardware/README.md#troubleshooting)
- Backend issues → [Backend Setup Guide](docs/backend_doc/README.md#troubleshooting)

## 📝 Workflow Overview

### File-Based Workflow

```
Audio File → Sarvam STT → Text → Gemini AI → Response
```

### ESP32-Based Workflow

```
ESP32 + INMP441 → WiFi Upload → Server → Sarvam STT → Gemini AI → Response
```

## 🤝 Contributing

Contributions are welcome! Please read the documentation first.

## 📄 License

ISC

## 🔗 Links

- [Sarvam AI](https://www.sarvam.ai/)
- [Google Gemini](https://ai.google.dev/)
- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
