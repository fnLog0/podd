# Voice Pipeline Implementation Summary

## Completed Implementation

This implementation provides a complete voice pipeline using Sarvam AI SDK for the Podd Health Assistant.

### Files Created/Modified

1. **src/services/sarvam_service.py** - Complete Sarvam AI SDK wrapper
   - Speech-to-Text (STT) using saarika:v2
   - Text-to-Speech (TTS) using bulbul:v1/v2
   - Language identification
   - Text translation
   - Base64 audio handling

2. **src/schemas/voice/voice.py** - Voice request/response schemas
   - VoiceStreamRequest/Response
   - VoiceSynthesizeRequest (with pitch, pace, loudness controls)
   - VoiceConversationRequest/Response
   - VoiceWebSocketMessage

3. **src/routes/voice/voice.py** - Voice API endpoints
   - POST /api/voice/stream - STT endpoint
   - POST /api/voice/synthesize - TTS endpoint
   - POST /api/voice/conversation - Full round-trip (STT → LangGraph → TTS)
   - WS /api/voice/ws - Real-time WebSocket streaming

4. **requirements.txt** - Added sarvamai==0.1.25

5. **docs/voice_pipeline.md** - Comprehensive documentation

6. **test_sarvam_voice.py** - Test suite for voice functionality

### API Endpoints Implemented

#### 1. POST /api/voice/stream
- Receives audio file (multipart/form-data)
- Returns transcript with language code and confidence
- Supports auto language detection
- Optional translation to English

#### 2. POST /api/voice/synthesize
- Receives text and voice parameters (JSON)
- Returns WAV audio file
- Adjustable pitch (-0.75 to 0.75)
- Adjustable pace (0.5 to 2.0)
- Adjustable loudness (0.3 to 3.0)
- Multiple sample rates (8kHz, 16kHz, 22.05kHz, 24kHz)

#### 3. POST /api/voice/conversation
- Receives audio input
- Transcribes using Sarvam STT
- Processes through LangGraph health workflow
- Generates TTS response
- Returns audio with metadata headers

#### 4. WS /api/voice/ws
- Real-time bidirectional audio streaming
- Supports audio chunk processing
- Handles interruptions
- Supports text input
- WebSocket message protocol

### Supported Languages

**STT & TTS (11 primary languages):**
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

**TTS Only (additional 11 languages):**
- Assamese, Bodo, Dogri, Konkani, Kashmiri, Maithili, Manipuri, Nepali, Sanskrit, Santali, Sindhi, Urdu

### Speaker Voices

**Bulbul v1 (12 speakers):**
- Female: Diya, Maya, Meera, Pavithra, Maitreyi, Misha
- Male: Amol, Arjun, Amartya, Arvind, Neel, Vian

**Bulbul v2 (7 speakers):**
- Female: Anushka, Manisha, Vidya, Arya
- Male: Abhilash, Karun, Hitesh

### Configuration Required

Add to `.env` file:
```env
SARVAM_API_KEY=your_api_key_here
```

Get API key from: https://dashboard.sarvam.ai

### Key Features

1. **Auto Language Detection**: STT can auto-detect from 11 Indian languages
2. **Code-Mixing Support**: Handles mixed language input
3. **Customizable Audio**: Adjust pitch, pace, loudness for TTS
4. **Real-time Streaming**: WebSocket endpoint for low-latency voice interaction
5. **LangGraph Integration**: Seamless workflow integration for health queries
6. **Interrupt Handling**: WebSocket supports user interruptions during playback

### Pricing (as per Sarvam AI docs)

- **STT**: ₹30/hour of audio
- **TTS**: ₹30/10K characters
- Refer to https://dashboard.sarvam.ai for current pricing

### Testing

Run the test suite:
```bash
python test_sarvam_voice.py
```

Test with Bruno:
- Use pre-configured requests in @bruno.podd/Voice/
- Requires authentication token
- Test audio files for STT endpoints

### Integration with ESP32

The implementation includes code examples for:
- Audio capture from ESP32 microphone
- TTS playback on ESP32 speaker
- Full conversation loop via WebSocket
- Audio optimization tips for ESP32 bandwidth constraints

See `docs/voice_pipeline.md` for detailed ESP32 integration examples.

### Models Used

- **STT**: saarika:v2 (supports auto-detection, 11 languages)
- **TTS**: bulbul:v1 (12 speakers, 11 languages)
- **Translation**: mayura:v1 (12 languages, full transliteration support)

### Next Steps for Production

1. Set SARVAM_API_KEY in `.env` file
2. Test with actual audio files
3. Configure appropriate sample rate for ESP32 (8kHz recommended)
4. Implement proper audio buffering for WebSocket
5. Add monitoring for API usage and costs
6. Implement rate limiting for public endpoints
7. Add proper error handling for network failures
8. Consider audio compression for bandwidth optimization

### Implementation Notes

- All endpoints require authentication (via JWT)
- WebSocket supports anonymous connections but can authenticate
- Audio files are processed as raw bytes
- TTS returns WAV format (compatible with ESP32)
- STT supports WAV, MP3, and other common audio formats
- Language detection works best with clear audio samples
- Code-mixing detection is automatic for supported language pairs

## Files Summary

**New Files:**
- src/schemas/voice/__init__.py
- src/schemas/voice/voice.py
- docs/voice_pipeline.md
- test_sarvam_voice.py

**Modified Files:**
- src/services/sarvam_service.py
- src/routes/voice/voice.py
- src/schemas/__init__.py
- requirements.txt

## Verification

All Python files compile without syntax errors:
```bash
python3 -m py_compile src/services/sarvam_service.py
python3 -m py_compile src/schemas/voice/voice.py
python3 -m py_compile src/routes/voice/voice.py
```

✅ Implementation complete and ready for testing with SARVAM_API_KEY!
