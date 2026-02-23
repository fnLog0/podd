from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message to the health assistant", min_length=1, max_length=1000)
    locale: Optional[Literal["en-IN", "hi-IN"]] = Field(
        default="en-IN", description="Language/locale for the response"
    )
    channel: Optional[Literal["text", "voice"]] = Field(
        default="text", description="Channel through which the message is sent"
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant's response")
    intent: str = Field(..., description="Detected intent of the user's message")
    locale: str = Field(..., description="Locale used for the response")


class ChatHistoryResponse(BaseModel):
    conversations: list[dict] = Field(default_factory=list, description="List of conversation turns")
    total_count: int = Field(..., description="Total number of conversation turns")
