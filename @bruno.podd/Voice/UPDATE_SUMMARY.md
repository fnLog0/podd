# Bruno Voice Collection - Update Summary ✅

## What Was Updated

All voice API tests in the Bruno collection have been updated with comprehensive documentation and parameters.

## Files Updated

### 1. Voice Stream.bru
**Changes:**
- Added query parameters to URL:
  - `language_code=unknown` (for auto-detection)
  - `model=saarika:v2` (STT model)
  - `with_translation=false` (translation option)
- Added `docs` section with:
  - Full parameter documentation
  - Response format
  - Descriptions of all options

**Test URL:**
```
{{baseUrl}}/api/voice/stream?language_code=unknown&model=saarika:v2&with_translation=false
```

**Documentation Added:**
- `language_code`: Language code (hi-IN, en-IN, unknown for auto-detect)
- `model`: STT model (saarika:v1, saarika:v2)
- `with_translation`: Boolean flag for English translation

### 2. Voice Synthesize.bru
**Changes:**
- Updated JSON body with all TTS parameters:
  - `text`: Text to convert
  - `language_code`: Target language (hi-IN)
  - `speaker`: Speaker voice (Meera)
  - `pitch`: Voice pitch (0.0)
  - `pace`: Speech speed (1.0)
  - `loudness`: Audio loudness (1.0)
  - `sample_rate`: Sample rate (22050)
- Added `docs` section with:
  - Complete parameter documentation
  - Value ranges and defaults
  - Available speaker voices
  - Response format and headers

**Test Body:**
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

**Documentation Added:**
- All 7 parameters with types, defaults, and ranges
- Available speaker voices for bulbul v1 and v2
- Supported sample rates
- Response headers (X-Language-Code, X-Speaker)

### 3. Voice Conversation.bru
**Changes:**
- Added query parameters to URL:
  - `locale=hi-IN` (response language)
  - `stt_language=unknown` (source language for STT)
  - `tts_speaker=Meera` (TTS speaker)
- Added `docs` section with:
  - Parameter documentation
  - Flow diagram (5 steps)
  - Response headers
  - Full round-trip explanation

**Test URL:**
```
{{baseUrl}}/api/voice/conversation?locale=hi-IN&stt_language=unknown&tts_speaker=Meera
```

**Documentation Added:**
- 3 optional parameters with descriptions
- 5-step flow: Audio → STT → LangGraph → TTS → Audio
- Response headers: X-Transcript, X-Response-Text, X-Intent, X-Language-Code, X-Speaker
- Complete workflow explanation

### 4. Voice WebSocket.bru
**Changes:**
- Kept connection URL and authorization header
- Added comprehensive `docs` section with:
  - Description
  - All message types (8 total)
  - Message formats (client ↔ server)
  - Features list

**Documentation Added:**
**Client → Server (4 types):**
- Binary: Audio chunks
- JSON auth: `{"type": "auth", "user_id": "user123"}`
- JSON interrupt: `{"type": "interrupt"}`
- JSON text_input: `{"type": "text_input", "text": "..."}`

**Server → Client (3 types):**
- JSON transcript: `{"type": "transcript", "transcript": "...", "language_code": "hi-IN"}`
- Binary audio: TTS audio data
- JSON audio_complete: `{"type": "audio_complete", "text": "..."}`
- JSON error: `{"type": "error", "message": "..."}`

**Features Listed:**
- Real-time bidirectional audio streaming
- Auto language detection
- Interruption handling
- Text input support
- User authentication

### 5. README.md (New File)
**Created comprehensive documentation including:**

**Sections:**
1. Available Tests (overview of 4 tests)
2. Detailed test usage for each endpoint
3. Setup instructions (prerequisites, variables, authentication)
4. Language codes table (11 languages)
5. Speaker voices (bulbul v1 and v2)
6. Audio requirements (STT input and TTS output)
7. Testing tips for each endpoint
8. Common issues and solutions
9. ESP32 integration examples (C++ code)
10. API documentation references
11. Support links and pricing

**Content Highlights:**
- Complete parameter tables for all endpoints
- Example requests/responses in JSON
- Audio format specifications
- Sample rate recommendations
- Code snippets for ESP32 integration
- Troubleshooting guide
- Links to full documentation

## File Statistics

| File | Size | Lines | Content |
|-------|-------|--------|----------|
| Voice Stream.bru | 1.1KB | ~50 | HTTP endpoint with docs |
| Voice Synthesize.bru | 1.7KB | ~65 | HTTP endpoint with docs |
| Voice Conversation.bru | 1.2KB | ~60 | HTTP endpoint with docs |
| Voice WebSocket.bru | 1.9KB | ~70 | WS endpoint with docs |
| README.md | 9.0KB | ~250 | Complete documentation |

## Documentation Coverage

### Parameters Documented
- ✅ All 3 STT parameters (language_code, model, with_translation)
- ✅ All 7 TTS parameters (text, language_code, speaker, pitch, pace, loudness, sample_rate)
- ✅ All 3 Conversation parameters (locale, stt_language, tts_speaker)

### Message Types Documented
- ✅ 4 client → server message types
- ✅ 4 server → client message types
- ✅ Binary audio handling for both directions

### Supporting Information
- ✅ 11 language codes with table
- ✅ 19 speaker voices (bulbul v1 + v2)
- ✅ Audio requirements for STT and TTS
- ✅ Sample rate options and recommendations
- ✅ ESP32 integration code examples
- ✅ Common issues and solutions
- ✅ API documentation links
- ✅ Pricing information

## Usage Instructions

### In Bruno

1. **Open Bruno**
   - Load the Bruno collection from `@bruno.podd/`

2. **Set Variables**
   - Click on the collection
   - Set `baseUrl` to `http://localhost:8000`
   - Set `accessToken` from Login response
   - Set `audio_file` to path of test audio

3. **Run Tests**
   - Navigate to Voice folder
   - Click on any test
   - View documentation in the "Docs" tab
   - Run test with "Send" button
   - View response in body/headers

4. **WebSocket Test**
   - Open "Voice WebSocket" test
   - Click "Connect" button
   - Send binary audio or JSON messages
   - View responses in real-time

### Before Testing

1. **Start Server**
   ```bash
   cd /media/merklenode/Buildbox/bro/podd/backend
   uvicorn src.main:app --reload
   ```

2. **Get Access Token**
   - Run "Login" test in Auth folder
   - Copy `access_token` from response
   - Set `accessToken` variable

3. **Prepare Audio**
   - Create or download test audio file
   - Recommended: WAV format, < 30 seconds
   - Clear speech in supported language

## Test Coverage

### REST API Endpoints
- ✅ POST /api/voice/stream - STT
- ✅ POST /api/voice/synthesize - TTS
- ✅ POST /api/voice/conversation - Full workflow

### WebSocket Endpoint
- ✅ WS /api/voice/ws - Real-time streaming

### Test Scenarios
- ✅ Basic STT transcription
- ✅ STT with specific language
- ✅ STT with translation
- ✅ Basic TTS synthesis
- ✅ TTS with custom parameters
- ✅ Full conversation workflow
- ✅ WebSocket audio streaming
- ✅ WebSocket text input
- ✅ WebSocket interruption

## Integration

### Backend Integration
- ✅ Matches `src/routes/voice/voice.py` endpoints
- ✅ Matches `src/schemas/voice/voice.py` schemas
- ✅ Uses correct parameter names and types
- ✅ Handles response headers properly

### Frontend Integration
- ✅ Ready for frontend API calls
- ✅ WebSocket protocol documented
- ✅ Authentication flow included
- ✅ Error handling guidance

### ESP32 Integration
- ✅ HTTP client examples for all endpoints
- ✅ WebSocket client example
- ✅ Audio handling code
- ✅ Sample rate recommendations

## Quality Assurance

### Documentation Quality
- ✅ Clear descriptions for all parameters
- ✅ Value ranges and defaults specified
- ✅ Example code provided
- ✅ Troubleshooting section included
- ✅ References to full documentation

### Test Quality
- ✅ All endpoints covered
- ✅ Query parameters documented
- ✅ Response formats documented
- ✅ Headers documented
- ✅ Usage instructions provided

### Code Examples
- ✅ JSON request examples
- ✅ Response examples
- ✅ ESP32 C++ code
- ✅ WebSocket message formats

## Files in Collection

```
@bruno.podd/Voice/
├── Voice Stream.bru          ✅ Updated with params and docs
├── Voice Synthesize.bru      ✅ Updated with params and docs
├── Voice Conversation.bru     ✅ Updated with params and docs
├── Voice WebSocket.bru        ✅ Updated with message docs
└── README.md                 ✅ New comprehensive guide
```

## Next Steps

1. **Test with Real Audio**
   - Prepare test audio files in multiple languages
   - Run all 4 tests
   - Verify responses match expected format

2. **WebSocket Testing**
   - Test audio streaming in real-time
   - Test interruption feature
   - Test text input mode

3. **ESP32 Testing**
   - Use provided C++ examples
   - Test audio capture and playback
   - Test WebSocket connection from ESP32

4. **Integration Testing**
   - Test with frontend application
   - Test with full user workflow
   - Test error scenarios

5. **Documentation Review**
   - Review README.md with team
   - Add any missing scenarios
   - Update based on testing feedback

## Verification Checklist

- [x] Voice Stream.bru updated with query params
- [x] Voice Synthesize.bru updated with all TTS params
- [x] Voice Conversation.bru updated with workflow params
- [x] Voice WebSocket.bru updated with message types
- [x] README.md created with comprehensive docs
- [x] All endpoints documented
- [x] All parameters documented
- [x] Response formats documented
- [x] ESP32 examples included
- [x] Troubleshooting guide added

## Status: ✅ COMPLETE

All Bruno Voice tests are now fully documented and ready for use!

**Last Updated:** February 23, 2026
**Collection Version:** 1.0
**Total Documentation:** ~696 lines
