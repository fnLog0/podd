# Voice Pipeline Implementation - Sarvam AI

This implementation provides voice capabilities using the Sarvam AI SDK, including Speech-to-Text (STT), Text-to-Speech (TTS), and real-time WebSocket streaming.

## Features

### 1. Speech-to-Text (STT) - Saaras v2.5
- Auto language detection (11 Indian languages)
- Code-mixing support
- Real-time transcription
- Optional translation to English

### 2. Text-to-Speech (TTS) - Bulbul v3
- 30+ Indian voices
- 11 languages supported
- Adjustable pitch, pace, and loudness
- Multiple sample rates (8kHz, 16kHz, 22.05kHz, 24kHz)

### 3. Voice Endpoints

#### `POST /api/voice/stream`
Receives audio blob, runs Saaras STT, returns transcript as JSON.

**Request:**
- Method: POST
- Body: Multipart form data with audio file
- Query params:
  - `language_code`: Language code (default: "unknown" for auto-detect)
  - `model`: STT model (default: "saarika:v2")
  - `with_translation`: Set to true to translate to English

**Response:**
```json
{
  "transcript": "नमस्ते, मैं ठीक हूं",
  "language_code": "hi-IN",
  "confidence": 0.95
}
```

#### `POST /api/voice/synthesize`
Receives text, runs Bulbul TTS, returns audio file (WAV).

**Request:**
- Method: POST
- Body: JSON
```json
{
  "text": "Hello, this is a test message",
  "language_code": "hi-IN",
  "speaker": "Meera",
  "pitch": 0.0,
  "pace": 1.0,
  "loudness": 1.0,
  "sample_rate": 22050
}
```

**Response:**
- Content-Type: audio/wav
- Body: Audio bytes (WAV format)
- Headers:
  - `X-Language-Code`: Language used
  - `X-Speaker`: Speaker name

#### `POST /api/voice/conversation`
Full round-trip: audio → Saaras STT → LangGraph workflow → Bulbul TTS → return audio response.

**Request:**
- Method: POST
- Body: Multipart form data with audio file
- Query params:
  - `locale`: Target language for response (default: "hi-IN")
  - `stt_language`: Source language for STT (default: "unknown")
  - `tts_speaker`: Speaker for TTS response (default: "Meera")

**Response:**
- Content-Type: audio/wav
- Body: Audio bytes (WAV format)
- Headers:
  - `X-Transcript`: Transcribed text
  - `X-Response-Text`: Assistant's response text
  - `X-Intent`: Detected intent
  - `X-Language-Code`: Response language

#### `WS /api/voice/ws`
Real-time bidirectional audio streaming WebSocket.

**Connection:** `ws://localhost:8000/api/voice/ws`

**Message Types:**

1. **Audio from client** (binary):
   - Send audio chunks as binary data
   - Server will transcribe and respond

2. **Auth message** (JSON):
```json
{
  "type": "auth",
  "user_id": "user123"
}
```

3. **Interrupt message** (JSON):
```json
{
  "type": "interrupt"
}
```

4. **Text input** (JSON):
```json
{
  "type": "text_input",
  "text": "Hello, how are you?"
}
```

**Server responses:**

1. **Transcript** (JSON):
```json
{
  "type": "transcript",
  "transcript": "नमस्ते",
  "language_code": "hi-IN"
}
```

2. **Audio** (binary):
   - TTS audio as WAV binary data

3. **Audio complete** (JSON):
```json
{
  "type": "audio_complete",
  "text": "Hello! How can I help you today?"
}
```

4. **Error** (JSON):
```json
{
  "type": "error",
  "message": "Error description"
}
```

## Supported Languages

### STT (Speech-to-Text)
- Hindi (hi-IN)
- English (en-IN)
- Bengali (bn-IN)
- Gujarati (gu-IN)
- Kannada (kn-IN)
- Malayalam (ml-IN)
- Marathi (mr-IN)
- Odia (od-IN)
- Punjabi (pa-IN)
- Tamil (ta-IN)
- Telugu (te-IN)
- Use "unknown" for auto-detection

### TTS (Text-to-Speech)
Same 11 languages as STT, plus additional Assamese, Bodo, Dogri, Konkani, Kashmiri, Maithili, Manipuri, Nepali, Sanskrit, Santali, Sindhi, and Urdu.

### Speaker Voices

**Bulbul v1:**
- Female: Diya, Maya, Meera, Pavithra, Maitreyi, Misha
- Male: Amol, Arjun, Amartya, Arvind, Neel, Vian

**Bulbul v2:**
- Female: Anushka, Manisha, Vidya, Arya
- Male: Abhilash, Karun, Hitesh

## Configuration

Add to `.env` file:
```env
SARVAM_API_KEY=your_api_key_here
```

Get your API key from: https://dashboard.sarvam.ai

## Testing

Run the test suite:
```bash
python test_sarvam_voice.py
```

This will test:
1. Service initialization
2. Language identification
3. Text translation
4. Text-to-Speech generation
5. Speech-to-Text (requires audio file)

## ESP32 Integration

### Audio Capture from ESP32 Mic
```cpp
// Example: POST audio to /api/voice/stream
HTTPClient http;
http.begin("http://your-server/api/voice/stream");
http.addHeader("Authorization", "Bearer " + accessToken);
http.addHeader("Content-Type", "multipart/form-data");

// Send audio chunks
int httpResponseCode = http.sendRequest("POST", (uint8_t*)audioData, audioLength);
```

### TTS Playback on ESP32
```cpp
// Example: Get TTS audio from /api/voice/synthesize
HTTPClient http;
http.begin("http://your-server/api/voice/synthesize");
http.addHeader("Authorization", "Bearer " + accessToken);
http.addHeader("Content-Type", "application/json");

String json = "{\"text\":\"Hello\",\"language_code\":\"hi-IN\"}";
int httpResponseCode = http.POST(json);

// Play the received audio data
String audioData = http.getString();
playAudio(audioData);
```

### Full Conversation Loop via WebSocket
```cpp
// Example: WebSocket connection
WebSocketsClient webSocket;
webSocket.begin("ws://your-server/api/voice/ws");

// Send audio chunk
webSocket.sendBIN(audioData, audioLength);

// Handle incoming audio
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_BIN) {
    playAudio(payload, length);
  }
}
```

### Audio Optimization for ESP32
- **Sample Rate**: Use 8000 Hz or 16000 Hz for reduced bandwidth
- **Format**: WAV (PCM) is supported directly
- **Compression**: Consider ADPCM or similar for audio data transmission
- **Buffer Size**: Keep chunks under 4KB for reliable transmission

## API Models

### Speech-to-Text Models
- **saarika:v1**: Mandatory language_code parameter
- **saarika:v2**: Optional language_code (supports auto-detection)

### Text-to-Speech Models
- **bulbul:v1**: 12 speakers, 6 male + 6 female
- **bulbul:v2**: 7 speakers, 3 male + 4 female

### Translation Models
- **mayura:v1**: 12 languages, all translation modes
- **sarvam-translate:v1**: All 22 scheduled Indian languages, formal mode only

## Cost Information

As per Sarvam AI documentation (as of Feb 2026):
- **STT (Saaras)**: ₹30/hour
- **TTS (Bulbul)**: ₹30/10K characters
- **Translation**: Varies by model and text length

Refer to https://dashboard.sarvam.ai for current pricing.

## Error Handling

All endpoints return appropriate error responses:

**STT Errors:**
- Invalid audio format
- Unsupported language
- API rate limits

**TTS Errors:**
- Empty or invalid text
- Unsupported speaker for language
- Text too long (>10K characters recommended)

**WebSocket Errors:**
- Connection timeout
- Invalid message format
- Audio processing failures

## Troubleshooting

### Common Issues

1. **"SARVAM_API_KEY not set"**
   - Add your API key to `.env` file
   - Restart the server

2. **STT returns empty transcript**
   - Check audio file format (WAV, MP3 supported)
   - Ensure audio has sufficient volume
   - Try with "unknown" language code for auto-detection

3. **TTS fails with "No audio data in response"**
   - Verify text is not empty
   - Check language code is valid
   - Ensure speaker is compatible with model

4. **WebSocket connection drops**
   - Check network connectivity
   - Ensure server is running
   - Verify WebSocket endpoint URL

## Files Structure

```
backend/
├── src/
│   ├── routes/
│   │   └── voice/
│   │       ├── __init__.py
│   │       └── voice.py          # Voice API endpoints
│   ├── schemas/
│   │   └── voice/
│   │       ├── __init__.py
│   │       └── voice.py          # Voice request/response schemas
│   ├── services/
│   │   └── sarvam_service.py    # Sarvam AI SDK wrapper
│   └── workflows/
│       └── health_workflow.py    # LangGraph integration
├── requirements.txt               # Includes sarvamai==0.1.25
├── .env.example                  # SARVAM_API_KEY configuration
└── test_sarvam_voice.py          # Test suite
```

## References

- [Sarvam AI Documentation](https://docs.sarvam.ai)
- [Sarvam AI Python SDK](https://pypi.org/project/sarvamai/)
- [Sarvam AI Dashboard](https://dashboard.sarvam.ai)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
