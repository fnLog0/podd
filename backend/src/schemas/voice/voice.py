"""Schemas for voice functionality."""
from typing import Optional

from pydantic import BaseModel, Field


class VoiceStreamRequest(BaseModel):
    """Request for voice streaming (STT)."""

    language_code: str = Field(
        default="hi-IN", description="Language code (e.g., hi-IN, en-IN)"
    )


class VoiceStreamResponse(BaseModel):
    """Response from voice streaming (STT)."""

    transcript: str = Field(description="Transcribed text from audio")
    language_code: str = Field(description="Detected language code")
    confidence: float = Field(description="Confidence score of transcription")
    duration: Optional[float] = Field(default=None, description="Audio duration in seconds")


class VoiceSynthesizeRequest(BaseModel):
    """Request for voice synthesis (TTS)."""

    text: str = Field(..., description="Text to synthesize", min_length=1)
    language_code: str = Field(
        default="hi-IN", description="Language code (e.g., hi-IN, en-IN)"
    )
    speaker: str = Field(
        default="shubh", description="Speaker name for TTS"
    )


class VoiceSynthesizeResponse(BaseModel):
    """Response from voice synthesis (TTS)."""

    audio_content: str = Field(description="Base64 encoded audio content")
    audio_format: str = Field(default="wav", description="Audio format (wav, mp3)")
    language_code: str = Field(description="Language code used")
    speaker: str = Field(description="Speaker used for synthesis")
    duration: Optional[float] = Field(default=None, description="Audio duration in seconds")
    character_count: int = Field(description="Number of characters synthesized")


class VoiceConversationRequest(BaseModel):
    """Request for full voice conversation (STT -> LLM -> TTS)."""

    language_code: str = Field(
        default="hi-IN", description="Language code (e.g., hi-IN, en-IN)"
    )
    speaker: str = Field(
        default="shubh", description="Speaker name for TTS"
    )


class VoiceConversationResponse(BaseModel):
    """Response from voice conversation."""

    transcript: str = Field(description="Transcribed user input")
    intent: str = Field(description="Detected intent from user message")
    assistant_response: str = Field(description="Assistant's text response")
    audio_content: str = Field(description="Base64 encoded audio of response")
    audio_format: str = Field(default="wav", description="Audio format")
    language_code: str = Field(description="Language code used")
