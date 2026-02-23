"""Schemas for chat functionality."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message."""

    id: str = Field(description="Message ID")
    user_id: str = Field(description="User ID")
    role: str = Field(description="Role: 'user' or 'assistant'")
    content: str = Field(description="Message content")
    created_at: datetime = Field(description="Message creation timestamp")
    channel: str = Field(default="text", description="Channel: 'text' or 'voice'")


class ChatRequest(BaseModel):
    """Request to send a chat message."""

    message: str = Field(..., description="User message", min_length=1)
    locale: str = Field(default="en-IN", description="Locale for language preferences")
    channel: str = Field(default="text", description="Channel: 'text' or 'voice'")


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    id: str = Field(description="Response ID")
    user_id: str = Field(description="User ID")
    user_message: str = Field(description="Original user message")
    assistant_message: str = Field(description="Assistant's response")
    intent: str = Field(description="Detected intent of the message")
    created_at: datetime = Field(description="Response timestamp")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class ChatHistoryResponse(BaseModel):
    """Response for chat history endpoint."""

    user_id: str = Field(description="User ID")
    messages: list[ChatMessage] = Field(description="List of chat messages")
    total_count: int = Field(description="Total number of messages")
    retrieved_at: datetime = Field(description="Timestamp of retrieval")
