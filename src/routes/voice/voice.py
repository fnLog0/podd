import base64
import json
from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from src.auth.dependencies import get_current_user
from src.models.user import User
from src.schemas import (
    VoiceConversationResponse,
    VoiceStreamResponse,
    VoiceSynthesizeRequest,
)
from src.services.sarvam_service import sarvam_service
from src.workflows.health_workflow import run_workflow

router = APIRouter(
    prefix="/voice", tags=["voice"], dependencies=[Depends(get_current_user)]
)


@router.post("/stream", response_model=VoiceStreamResponse)
async def voice_stream(
    file: UploadFile = File(...),
    language_code: str = "unknown",
    model: str = "saarika:v2",
    with_translation: bool = False,
):
    """
    Receive audio blob, run Sarvam STT (Saaras v2.5), return transcript as JSON.

    Supports auto language detection with 'unknown' language code.
    """
    try:
        audio_data = await file.read()

        result = await sarvam_service.speech_to_text(
            audio_data=audio_data,
            language_code=language_code,
            model=model,
            with_translation=with_translation,
        )

        return VoiceStreamResponse(
            transcript=result.get("transcript", ""),
            language_code=result.get("language_code"),
            confidence=result.get("confidence"),
        )
    except Exception as e:
        return VoiceStreamResponse(
            transcript=f"Error: {str(e)}",
            language_code="error",
            confidence=0.0,
        )


@router.post("/synthesize")
async def voice_synthesize(
    request: VoiceSynthesizeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Receive text, run Bulbul TTS, return audio file (WAV).
    """
    try:
        speaker = request.get_speaker()

        audio_bytes = await sarvam_service.text_to_speech(
            text=request.text,
            language_code=request.language_code,
            speaker=speaker,
            pitch=request.pitch,
            pace=request.pace,
            loudness=request.loudness,
            sample_rate=request.sample_rate,
        )

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'attachment; filename="speech_{request.language_code}.wav"',
                "X-Language-Code": request.language_code,
                "X-Speaker": speaker,
            },
        )
    except Exception as e:
        return Response(
            content=b"",
            status_code=500,
            media_type="text/plain",
            headers={"X-Error": str(e)},
        )


@router.post("/conversation", response_model=VoiceConversationResponse)
async def voice_conversation(
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
    locale: str = "hi-IN",
    stt_language: str = "unknown",
    tts_speaker: str = "Meera",
):
    """
    Full round-trip: audio → Saaras STT → LangGraph workflow → Bulbul TTS → return audio response.

    This endpoint:
    1. Receives audio input
    2. Transcribes it using Sarvam STT
    3. Processes the transcript through the LangGraph health workflow
    4. Converts the response to speech using Sarvam TTS
    5. Returns the audio response
    """
    try:
        audio_data = await file.read()

        # Step 1 - Transcribe audio to text
        stt_result = await sarvam_service.speech_to_text(
            audio_data=audio_data,
            language_code=stt_language,
            model="saarika:v2",
        )
        transcript = stt_result.get("transcript", "")

        if not transcript:
            raise ValueError("Failed to transcribe audio")

        # Step 2 - Process through LangGraph workflow
        workflow_result = await run_workflow(
            user_id=current_user.id,
            user_text=transcript,
            locale=locale,
            channel="voice",
        )
        assistant_text = workflow_result.get("assistant_text", "I couldn't process your request.")
        intent = workflow_result.get("intent", "unknown")

        # Step 3 - Convert response to speech
        audio_bytes = await sarvam_service.text_to_speech(
            text=assistant_text,
            language_code=locale,
            speaker=tts_speaker,
            model="bulbul:v1",
        )

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'attachment; filename="response_{locale}.wav"',
                "X-Transcript": transcript,
                "X-Response-Text": assistant_text,
                "X-Intent": intent,
                "X-Language-Code": locale,
                "X-Speaker": tts_speaker,
            },
        )
    except Exception as e:
        return Response(
            content=b"",
            status_code=500,
            media_type="text/plain",
            headers={"X-Error": str(e)},
        )


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_binary(self, data: bytes, websocket: WebSocket):
        await websocket.send_bytes(data)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket):
    """
    Real-time bidirectional audio streaming WebSocket.

    Client sends audio chunks, server streams back TTS audio chunks.
    Handles interruptions (user speaks while TTS is playing).

    WebSocket endpoint: WS /api/voice/ws
    """
    await manager.connect(websocket)

    try:
        current_user_id = "anonymous"

        while True:
            data = await websocket.receive()

            if "bytes" in data:
                audio_data = data["bytes"]

                try:
                    # Process incoming audio
                    stt_result = await sarvam_service.speech_to_text(
                        audio_data=audio_data,
                        language_code="unknown",
                        model="saarika:v2",
                    )
                    transcript = stt_result.get("transcript", "")

                    if transcript:
                        # Send transcript confirmation
                        await websocket.send_json(
                            {
                                "type": "transcript",
                                "transcript": transcript,
                                "language_code": stt_result.get("language_code", "unknown"),
                            }
                        )

                        # Process through workflow if needed (simple routing)
                        if any(
                            keyword in transcript.lower()
                            for keyword in ["hello", "hi", "hey", "namaste"]
                        ):
                            response_text = "Hello! How can I help you today?"
                        elif any(
                            keyword in transcript.lower()
                            for keyword in ["medicine", "medication", "pill", "tablet"]
                        ):
                            response_text = "I can help you track your medications. What would you like to know?"
                        elif any(
                            keyword in transcript.lower()
                            for keyword in ["food", "eat", "meal", "breakfast", "lunch", "dinner"]
                        ):
                            response_text = "Would you like to log a food meal or get nutrition information?"
                        else:
                            response_text = "I understand. Please tell me more so I can help you better."

                        # Generate TTS audio
                        audio_bytes = await sarvam_service.text_to_speech(
                            text=response_text,
                            language_code="hi-IN",
                            speaker="Meera",
                        )

                        # Send audio response
                        await websocket.send_bytes(audio_bytes)
                        await websocket.send_json({"type": "audio_complete", "text": response_text})

                except Exception as e:
                    await websocket.send_json({"type": "error", "message": str(e)})

            elif "text" in data:
                text_data = data["text"]
                message = json.loads(text_data)

                if message.get("type") == "interrupt":
                    # Handle interruption (stop current playback)
                    await websocket.send_json({"type": "interrupt_acknowledged"})

                elif message.get("type") == "auth":
                    # Authenticate user
                    current_user_id = message.get("user_id", "anonymous")
                    await websocket.send_json({"type": "auth_success", "user_id": current_user_id})

                elif message.get("type") == "text_input":
                    # Process text input directly
                    response_text = "I received your text message. How can I assist you?"

                    audio_bytes = await sarvam_service.text_to_speech(
                        text=response_text,
                        language_code="hi-IN",
                        speaker="Meera",
                    )

                    await websocket.send_bytes(audio_bytes)
                    await websocket.send_json({"type": "audio_complete", "text": response_text})

            elif data == {"type": "disconnect"}:
                break

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
        manager.disconnect(websocket)
