from pydantic import BaseModel, Field
from typing import Literal, Optional


class VoiceStreamRequest(BaseModel):
    pass


class VoiceStreamResponse(BaseModel):
    transcript: str
    language_code: Optional[str] = None
    confidence: Optional[float] = None


class VoiceSynthesizeRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    language_code: str = Field(default="hi-IN", description="Target language code (e.g., hi-IN, en-IN)")
    speaker: Optional[str] = Field(default="Meera", description="Speaker voice name")
    voice: Optional[str] = Field(default=None, description="Alias for speaker parameter")
    pitch: Optional[float] = Field(default=0.0, ge=-0.75, le=0.75, description="Voice pitch (-0.75 to 0.75)")
    pace: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed (0.5 to 2.0)")
    loudness: Optional[float] = Field(default=1.0, ge=0.3, le=3.0, description="Audio loudness (0.3 to 3.0)")
    sample_rate: Optional[int] = Field(default=22050, description="Sample rate in Hz (8000, 16000, 22050, 24000)")

    def get_speaker(self) -> str:
        return self.voice if self.voice else self.speaker


class VoiceConversationRequest(BaseModel):
    pass


class VoiceConversationResponse(BaseModel):
    transcript: str
    response: str
    intent: Optional[str] = None


class VoiceWebSocketMessage(BaseModel):
    type: Literal["audio", "text", "interrupt", "error"]
    data: Optional[bytes | str | dict] = None
