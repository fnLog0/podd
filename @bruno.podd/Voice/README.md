# Voice API - Bruno Test Collection

This collection contains tests for the Voice API endpoints using Sarvam AI SDK.

## Available Tests

### 1. Voice Stream
**Endpoint:** `POST /api/voice/stream`

Transcribes audio to text using Sarvam AI STT (Saaras v2).

**Parameters:**
- `language_code`: Language code (default: "unknown" for auto-detect)
  - Options: hi-IN, en-IN, bn-IN, gu-IN, kn-IN, ml-IN, mr-IN, od-IN, pa-IN, ta-IN, te-IN
- `model`: STT model (default: "saarika:v2")
  - Options: saarika:v1, saarika:v2
- `with_translation`: Translate to English (default: false)
  - Options: true, false

**Request:**
- Content-Type: multipart/form-data
- File: Audio file (WAV, MP3, etc.)

**Response (JSON):**
```json
{
  "transcript": "नमस्ते, मैं ठीक हूं",
  "language_code": "hi-IN",
  "confidence": 0.95
}
```

**Usage:**
1. Create an audio file (test_audio.wav)
2. Set Bruno variable `audio_file` to point to the file
3. Run the "Voice Stream" test
4. View transcript in response

### 2. Voice Synthesize
**Endpoint:** `POST /api/voice/synthesize`

Converts text to speech using Sarvam AI TTS (Bulbul v1).

**Parameters:**
- `text`: Text to convert (required)
- `language_code`: Target language (default: "hi-IN")
- `speaker`: Speaker voice (default: "Meera")
  - Bulbul v1: Diya, Maya, Meera, Pavithra, Maitreyi, Misha (female)
  - Bulbul v1: Amol, Arjun, Amartya, Arvind, Neel, Vian (male)
- `pitch`: Voice pitch, range -0.75 to 0.75 (default: 0.0)
- `pace`: Speech speed, range 0.5 to 2.0 (default: 1.0)
- `loudness`: Audio loudness, range 0.3 to 3.0 (default: 1.0)
- `sample_rate`: Sample rate in Hz (default: 22050)
  - Options: 8000, 16000, 22050, 24000

**Request (JSON):**
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
- Body: Audio bytes
- Headers:
  - `X-Language-Code`: Language used
  - `X-Speaker`: Speaker name

**Usage:**
1. Modify the JSON body with your text and parameters
2. Run the "Voice Synthesize" test
3. Save the response as a .wav file to play

### 3. Voice Conversation
**Endpoint:** `POST /api/voice/conversation`

Full round-trip: Audio → STT → LangGraph → TTS → Audio response.

**Parameters:**
- `locale`: Target language for response (default: "hi-IN")
- `stt_language`: Source language for STT (default: "unknown")
- `tts_speaker`: Speaker for TTS response (default: "Meera")

**Request:**
- Content-Type: multipart/form-data
- File: Audio file

**Response:**
- Content-Type: audio/wav
- Body: Audio bytes
- Headers:
  - `X-Transcript`: Transcribed text
  - `X-Response-Text`: Assistant's response
  - `X-Intent`: Detected intent
  - `X-Language-Code`: Response language
  - `X-Speaker`: Speaker used

**Usage:**
1. Create an audio file with a health-related query
2. Set Bruno variable `audio_file` to point to the file
3. Run the "Voice Conversation" test
4. Check headers for transcript and response text
5. Save response as .wav file to play

**Example Queries:**
- "Hello, how are you?" → Greeting response
- "I need to take my medicine" → Medication tracking
- "What should I eat?" → Nutrition advice
- "I'm feeling tired" → Health assessment

### 4. Voice WebSocket
**Endpoint:** `WS /api/voice/ws`

Real-time bidirectional audio streaming for voice conversations.

**Connection:**
- URL: `ws://localhost:8000/api/voice/ws`
- Header: `Authorization: Bearer {{accessToken}}`

**Client Messages:**

1. **Audio (Binary)**
   - Send audio chunks directly
   - Server transcribes and responds

2. **Auth (JSON)**
   ```json
   {
     "type": "auth",
     "user_id": "user123"
   }
   ```

3. **Interrupt (JSON)**
   ```json
   {
     "type": "interrupt"
   }
   ```
   - Stops current TTS playback

4. **Text Input (JSON)**
   ```json
   {
     "type": "text_input",
     "text": "Hello, how are you?"
   }
   ```

**Server Responses:**

1. **Transcript (JSON)**
   ```json
   {
     "type": "transcript",
     "transcript": "नमस्ते",
     "language_code": "hi-IN"
   }
   ```

2. **Audio (Binary)**
   - TTS audio as WAV binary data
   - Play immediately when received

3. **Audio Complete (JSON)**
   ```json
   {
     "type": "audio_complete",
     "text": "Hello! How can I help you today?"
   }
   ```

4. **Error (JSON)**
   ```json
   {
     "type": "error",
     "message": "Error description"
   }
   ```

**Usage:**
1. Open Bruno WebSocket test
2. Click "Connect"
3. Send audio chunks or text messages
4. Receive transcript and audio responses
5. Use interrupt to stop playback
6. Disconnect when done

## Setup

### Prerequisites
1. Bruno installed on your machine
2. Podd backend server running (`uvicorn src.main:app --reload`)
3. Valid access token

### Bruno Variables
Set these in Bruno environment:

```javascript
{
  "baseUrl": "http://localhost:8000",
  "accessToken": "your_jwt_token_here",
  "audio_file": "/path/to/test_audio.wav"
}
```

### Get Access Token
1. Run the "Login" test in Auth collection
2. Copy the access token from response
3. Set `accessToken` variable

## Language Codes

| Language | Code |
|----------|------|
| Hindi | hi-IN |
| English (Indian) | en-IN |
| Bengali | bn-IN |
| Gujarati | gu-IN |
| Kannada | kn-IN |
| Malayalam | ml-IN |
| Marathi | mr-IN |
| Odia | od-IN |
| Punjabi | pa-IN |
| Tamil | ta-IN |
| Telugu | te-IN |

## Speaker Voices

### Bulbul v1 (Default)
**Female:**
- Diya, Maya, Meera, Pavithra, Maitreyi, Misha

**Male:**
- Amol, Arjun, Amartya, Arvind, Neel, Vian

### Bulbul v2
**Female:**
- Anushka, Manisha, Vidya, Arya

**Male:**
- Abhilash, Karun, Hitesh

## Audio Requirements

### STT Input
- **Format:** WAV, MP3, and common audio formats
- **Sample Rate:** Any (auto-resampled)
- **Duration:** Recommended < 30 seconds for real-time API
- **Quality:** Clear audio with minimal background noise

### TTS Output
- **Format:** WAV (PCM)
- **Sample Rates:** 8000, 16000, 22050, 24000 Hz
- **Recommended:** 8000 or 16000 for ESP32
- **Bit Depth:** 16-bit
- **Channels:** Mono

## Testing Tips

### Voice Stream
1. Start with a short, clear audio file
2. Use "unknown" language_code for auto-detection
3. Check confidence score in response
4. Enable with_translation for English output

### Voice Synthesize
1. Start with default parameters
2. Adjust pitch (-0.75 to 0.75) for voice tone
3. Adjust pace (0.5 to 2.0) for speech speed
4. Lower sample_rate for bandwidth-limited scenarios

### Voice Conversation
1. Prepare health-related queries in audio
2. Test different languages
3. Check response headers for workflow info
4. Verify intent detection accuracy

### Voice WebSocket
1. Test with small audio chunks (1-2 seconds)
2. Use interrupt feature to stop playback
3. Test both audio and text input modes
4. Monitor for error messages

## Common Issues

### "401 Unauthorized"
- Check accessToken variable is set correctly
- Token may have expired - run Login again

### "Empty transcript"
- Audio file may be too quiet
- Try different language_code or "unknown"
- Ensure audio is in supported format

### "TTS returns no audio"
- Check text field is not empty
- Verify language_code is valid
- Ensure speaker is compatible with model

### "WebSocket connection fails"
- Ensure server is running on correct port
- Check WebSocket URL is correct
- Verify network connectivity

## ESP32 Integration

### Audio Capture
```cpp
// Capture audio and send to /api/voice/stream
HTTPClient http;
http.begin(baseUrl + "/api/voice/stream");
http.addHeader("Authorization", "Bearer " + token);

// Create multipart form
String boundary = "----WebKitFormBoundary";
// ... send audio data ...

int code = http.sendRequest("POST", audioData, audioLength);
String response = http.getString();
```

### TTS Playback
```cpp
// Get TTS from /api/voice/synthesize
HTTPClient http;
http.begin(baseUrl + "/api/voice/synthesize");
http.addHeader("Content-Type", "application/json");

String body = "{\"text\":\"Hello\",\"language_code\":\"hi-IN\"}";
int code = http.POST(body);

if (code == 200) {
  String audio = http.getString();
  playAudio(audio);
}
```

### WebSocket
```cpp
// Connect to WebSocket
WebSocketsClient ws;
ws.begin(wsUrl);
ws.onEvent(webSocketEvent);
ws.setReconnectInterval(5000);

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_BIN) {
    // Play received audio
    playAudio(payload, length);
  }
}
```

## API Documentation

For complete API documentation, see:
- `docs/voice_pipeline.md` - Full documentation
- `docs/voice_quick_reference.md` - Quick reference
- `docs/voice_README.md` - Implementation overview

## Support

- **Sarvam AI Docs**: https://docs.sarvam.ai
- **Sarvam Dashboard**: https://dashboard.sarvam.ai
- **Podd Backend**: Check backend logs for errors

## Pricing

- **STT**: ₹30/hour of audio
- **TTS**: ₹30/10K characters
- Check Sarvam dashboard for current rates

## Version

- **Bruno Collection Version:** 1.0
- **API Version:** v1
- **Sarvam SDK:** 0.1.25
- **Last Updated:** February 23, 2026
