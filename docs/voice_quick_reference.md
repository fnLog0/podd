# Voice Pipeline - Quick Reference

## Setup

```bash
# Install dependencies
pip install sarvamai==0.1.25

# Set API key in .env
echo "SARVAM_API_KEY=your_key_here" >> .env
```

## API Quick Start

### 1. Speech-to-Text (STT)

```bash
# Basic STT with auto language detection
curl -X POST http://localhost:8000/api/voice/stream \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@audio.wav"

# STT with specific language
curl -X POST "http://localhost:8000/api/voice/stream?language_code=hi-IN" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@audio.wav"

# STT with translation
curl -X POST "http://localhost:8000/api/voice/stream?with_translation=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@audio.wav"
```

**Response:**
```json
{
  "transcript": "नमस्ते, मैं ठीक हूं",
  "language_code": "hi-IN",
  "confidence": 0.95
}
```

### 2. Text-to-Speech (TTS)

```bash
curl -X POST http://localhost:8000/api/voice/synthesize \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test",
    "language_code": "hi-IN",
    "speaker": "Meera",
    "pitch": 0.0,
    "pace": 1.0,
    "loudness": 1.0,
    "sample_rate": 22050
  }' \
  --output speech.wav
```

**Parameters:**
- `text`: Text to convert (required)
- `language_code`: Language code (default: hi-IN)
- `speaker`: Speaker name (default: Meera)
- `pitch`: -0.75 to 0.75 (default: 0.0)
- `pace`: 0.5 to 2.0 (default: 1.0)
- `loudness`: 0.3 to 3.0 (default: 1.0)
- `sample_rate`: 8000, 16000, 22050, 24000 (default: 22050)

### 3. Full Conversation

```bash
curl -X POST "http://localhost:8000/api/voice/conversation?locale=hi-IN&stt_language=unknown&tts_speaker=Meera" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@input.wav" \
  --output response.wav \
  -D headers.txt
```

**Response Headers:**
```
X-Transcript: नमस्ते
X-Response-Text: Hello! How can I help you today?
X-Intent: greeting
X-Language-Code: hi-IN
X-Speaker: Meera
```

### 4. WebSocket

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/voice/ws');

// Send audio chunk
ws.send(audioBuffer);

// Send text input
ws.send(JSON.stringify({
  type: "text_input",
  text: "Hello, how are you?"
}));

// Send auth
ws.send(JSON.stringify({
  type: "auth",
  user_id: "user123"
}));

// Handle responses
ws.onmessage = (event) => {
  if (event.data instanceof Blob) {
    // Binary audio data
    playAudio(event.data);
  } else {
    // JSON message
    const msg = JSON.parse(event.data);
    console.log(msg.type, msg.data);
  }
};

// Send interrupt
ws.send(JSON.stringify({ type: "interrupt" }));
```

## Language Codes

| Language | Code |
|----------|------|
| Hindi | hi-IN |
| English | en-IN |
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

**Bulbul v1:**
- Female: Diya, Maya, Meera, Pavithra, Maitreyi, Misha
- Male: Amol, Arjun, Amartya, Arvind, Neel, Vian

**Bulbul v2:**
- Female: Anushka, Manisha, Vidya, Arya
- Male: Abhilash, Karun, Hitesh

## Python Usage

### Direct Service Usage

```python
from src.services.sarvam_service import sarvam_service

# STT
result = await sarvam_service.speech_to_text(
    audio_data=audio_bytes,
    language_code="unknown",  # auto-detect
    model="saarika:v2"
)
print(result["transcript"])

# TTS
audio_bytes = await sarvam_service.text_to_speech(
    text="Hello, how are you?",
    language_code="hi-IN",
    speaker="Meera",
    pitch=0.0,
    pace=1.0
)
with open("speech.wav", "wb") as f:
    f.write(audio_bytes)

# Translation
result = await sarvam_service.translate_text(
    text="नमस्ते",
    source_language_code="auto",
    target_language_code="en-IN"
)
print(result["translated_text"])  # "Hello"

# Language identification
result = await sarvam_service.identify_language("नमस्ते")
print(result["language_code"])  # "hi-IN"
```

## ESP32 Quick Examples

### Simple TTS Request

```cpp
HTTPClient http;
http.begin("http://your-server/api/voice/synthesize");
http.addHeader("Authorization", "Bearer " + token);
http.addHeader("Content-Type", "application/json");

String body = "{\"text\":\"Hello\",\"language_code\":\"hi-IN\"}";
int code = http.POST(body);

if (code == 200) {
  String audio = http.getString();
  playAudio(audio);
}
```

### Simple STT Request

```cpp
HTTPClient http;
http.begin("http://your-server/api/voice/stream");
http.addHeader("Authorization", "Bearer " + token);

// Create multipart form boundary
String boundary = "----WebKitFormBoundary";
String header = "--" + boundary + "\r\n";
header += "Content-Disposition: form-data; name=\"file\"; filename=\"audio.wav\"\r\n\r\n";

String footer = "\r\n--" + boundary + "--\r\n";

// Send request
http.sendHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
http.send(header);
http.send(audioData, audioLength);
http.send(footer);

// Get response
String response = http.getString();
parseTranscript(response);
```

## Testing

```bash
# Run test suite
python test_sarvam_voice.py

# Test TTS only
python3 -c "
import asyncio
from src.services.sarvam_service import sarvam_service

async def test():
    audio = await sarvam_service.text_to_speech(
        text='Hello, world!',
        language_code='hi-IN',
        speaker='Meera'
    )
    with open('test.wav', 'wb') as f:
        f.write(audio)
    print('Saved test.wav')

asyncio.run(test())
"

# Test imports
python3 -c "from src.services.sarvam_service import sarvam_service; print('OK')"
python3 -c "from src.schemas.voice import VoiceSynthesizeRequest; print('OK')"
```

## Common Issues

**Issue:** "SARVAM_API_KEY not set"
**Fix:** Add to .env: `SARVAM_API_KEY=your_key`

**Issue:** Empty transcript
**Fix:** Check audio quality, try different language_code or "unknown"

**Issue:** TTS returns no audio
**Fix:** Verify text is not empty, check language_code is valid

**Issue:** WebSocket disconnects
**Fix:** Check network, verify endpoint URL, ensure server running

## File Locations

```
backend/
├── src/
│   ├── services/sarvam_service.py       # Main service
│   ├── schemas/voice/                   # Request/Response schemas
│   └── routes/voice/                  # API endpoints
├── docs/
│   ├── voice_pipeline.md                 # Full documentation
│   ├── voice_implementation_summary.md    # Implementation summary
│   └── voice_checklist.md               # Checklist
├── test_sarvam_voice.py                # Test suite
└── .env                               # API configuration
```

## Support

- Sarvam AI Docs: https://docs.sarvam.ai
- Sarvam Dashboard: https://dashboard.sarvam.ai
- PyPI: https://pypi.org/project/sarvamai/

## Pricing (Approximate)

- STT: ₹30/hour
- TTS: ₹30/10K characters
- Check dashboard for current rates
