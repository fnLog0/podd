"""Routes for voice functionality using Sarvam AI.

This module provides endpoints for:
- Speech-to-Text (STT) using Saaras v2.5
- Text-to-Speech (TTS) using Bulbul v3
- Full conversation pipeline (STT -> LangGraph -> TTS)
- Real-time WebSocket voice communication
"""

import base64
import io
import json
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse

from src.auth.dependencies import get_current_user
from src.schemas.voice import (
    VoiceConversationRequest,
    VoiceConversationResponse,
    VoiceStreamRequest,
    VoiceStreamResponse,
    VoiceSynthesizeRequest,
    VoiceSynthesizeResponse,
)
from src.services.sarvam_service import sarvam_service
from src.workflows.health_workflow import run_workflow

router = APIRouter(prefix="/voice", tags=["voice"], dependencies=[Depends(get_current_user)])


@router.post("/stream", response_model=VoiceStreamResponse, status_code=status.HTTP_200_OK)
async def voice_stream(
    file: UploadFile = File(...),
    language_code: str = "hi-IN",
    current_user=Depends(get_current_user),
):
    """Convert speech to text using Sarvam AI Saaras STT.

    Uploads an audio file and returns the transcribed text.
    Supports 11 Indian languages with auto-detection and code-mixing.

    Audio formats supported: WAV, MP3, FLAC, OGG, M4A
    """
    user_id = str(current_user.id)

    try:
        # Read audio file
        audio_content = await file.read()

        # Create a file-like object for Sarvam API
        audio_file = io.BytesIO(audio_content)
        audio_file.name = file.filename or "audio.wav"

        # Call Sarvam STT
        stt_result = await sarvam_service.speech_to_text(
            audio_file=audio_file,
            language_code=language_code,
        )

        # Extract transcript and metadata
        transcript = stt_result.get("transcript", "")
        detected_language = stt_result.get("language", language_code)
        confidence = stt_result.get("confidence", 0.0)
        duration = stt_result.get("duration")

        if not transcript:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Could not transcribe audio",
                    "detail": "No speech detected or audio format unsupported",
                },
            )

        return VoiceStreamResponse(
            transcript=transcript,
            language_code=detected_language,
            confidence=confidence,
            duration=duration,
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Failed to process audio",
                "detail": str(e),
            },
        )


@router.post("/synthesize", response_model=VoiceSynthesizeResponse, status_code=status.HTTP_200_OK)
async def voice_synthesize(
    request: VoiceSynthesizeRequest,
    current_user=Depends(get_current_user),
):
    """Convert text to speech using Sarvam AI Bulbul TTS.

    Returns synthesized audio in WAV format.
    Supports 30+ Indian voices in 11 languages.
    """
    user_id = str(current_user.id)

    try:
        # Call Sarvam TTS
        audio_bytes = await sarvam_service.text_to_speech(
            text=request.text,
            language_code=request.language_code,
            speaker=request.speaker,
        )

        # Convert audio bytes to base64 for JSON response
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        # Estimate duration (rough calculation: ~150ms per character for TTS)
        estimated_duration = len(request.text) * 0.15

        return VoiceSynthesizeResponse(
            audio_content=audio_base64,
            audio_format="wav",
            language_code=request.language_code,
            speaker=request.speaker,
            duration=estimated_duration,
            character_count=len(request.text),
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Failed to synthesize speech",
                "detail": str(e),
            },
        )


@router.post("/conversation", response_model=VoiceConversationResponse, status_code=status.HTTP_200_OK)
async def voice_conversation(
    file: UploadFile = File(...),
    language_code: str = "hi-IN",
    speaker: str = "shubh",
    current_user=Depends(get_current_user),
):
    """Full voice conversation pipeline: STT -> LangGraph -> TTS.

    1. Converts user's speech to text (STT)
    2. Processes text through LangGraph workflow
    3. Converts assistant's response to speech (TTS)
    4. Returns both transcript and audio
    """
    user_id = str(current_user.id)

    try:
        # Step 1: STT - Convert speech to text
        audio_content = await file.read()
        audio_file = io.BytesIO(audio_content)
        audio_file.name = "audio.wav"

        stt_result = await sarvam_service.speech_to_text(
            audio_file=audio_file,
            language_code=language_code,
        )

        transcript = stt_result.get("transcript", "")
        if not transcript:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Could not transcribe audio",
                    "detail": "No speech detected",
                },
            )

        # Step 2: LangGraph - Process text
        workflow_result = await run_workflow(
            user_id=user_id,
            user_text=transcript,
            locale=language_code,
            channel="voice",
        )

        assistant_text = workflow_result.get("assistant_text", "Sorry, I couldn't process that.")
        intent = workflow_result.get("intent", "unknown")

        # Step 3: TTS - Convert response to speech
        audio_bytes = await sarvam_service.text_to_speech(
            text=assistant_text,
            language_code=language_code,
            speaker=speaker,
        )

        # Convert audio to base64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        # Estimate duration
        estimated_duration = len(assistant_text) * 0.15

        return VoiceConversationResponse(
            transcript=transcript,
            intent=intent,
            assistant_response=assistant_text,
            audio_content=audio_base64,
            audio_format="wav",
            language_code=language_code,
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Failed to process voice conversation",
                "detail": str(e),
            },
        )


@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket):
    """Real-time bidirectional voice communication via WebSocket.

    Supports:
    - Streaming audio input from client
    - Interruptible TTS playback
    - Real-time conversation flow

    Protocol:
    1. Client connects
    2. Client sends audio chunks
    3. Server processes and streams TTS audio back
    4. Client can interrupt by sending new audio
    """
    await websocket.accept()

    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established for voice communication",
        })

        # Main conversation loop
        while True:
            # Receive message from client
            data = await websocket.receive()

            # Handle different message types
            if data["type"] == "websocket.disconnect":
                break

            if "bytes" in data:
                # Audio data received
                audio_bytes = data["bytes"]

                # Process audio (STT)
                try:
                    audio_file = io.BytesIO(audio_bytes)
                    stt_result = await sarvam_service.speech_to_text(
                        audio_file=audio_file,
                        language_code="hi-IN",
                    )

                    transcript = stt_result.get("transcript", "")

                    if transcript:
                        # Send transcript acknowledgment
                        await websocket.send_json({
                            "type": "transcript",
                            "transcript": transcript,
                        })

                        # Process through LangGraph
                        # Note: We'd need user_id from auth in WebSocket
                        # For now, using placeholder
                        workflow_result = await run_workflow(
                            user_id="temp_user",  # TODO: Get from WebSocket auth
                            user_text=transcript,
                            locale="hi-IN",
                            channel="voice",
                        )

                        assistant_text = workflow_result.get("assistant_text", "")

                        # Generate TTS
                        tts_audio = await sarvam_service.text_to_speech(
                            text=assistant_text,
                            language_code="hi-IN",
                            speaker="shubh",
                        )

                        # Stream audio back
                        await websocket.send_bytes(tts_audio)

                        # Send completion message
                        await websocket.send_json({
                            "type": "response_complete",
                            "response_text": assistant_text,
                        })
                    else:
                        # No speech detected
                        await websocket.send_json({
                            "type": "no_speech",
                            "message": "No speech detected in audio",
                        })

                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "error": str(e),
                    })

            elif "text" in data:
                # Text message (could be control commands)
                text_data = data["text"]
                try:
                    json_data = json.loads(text_data)
                    message_type = json_data.get("type")

                    if message_type == "interrupt":
                        # Client wants to interrupt current playback
                        await websocket.send_json({
                            "type": "interrupted",
                            "message": "Playback interrupted",
                        })

                    elif message_type == "config":
                        # Client sending configuration
                        config = json_data.get("config", {})
                        await websocket.send_json({
                            "type": "config_ack",
                            "config": config,
                        })

                except json.JSONDecodeError:
                    # Plain text message
                    await websocket.send_json({
                        "type": "echo",
                        "message": f"Received: {text_data}",
                    })

    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected")
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        await websocket.send_json({
            "type": "error",
            "error": str(e),
        })
    finally:
        await websocket.close()
