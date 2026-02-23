"""Pydantic schemas for Meditation API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MeditationSessionBase(BaseModel):
    """Base MeditationSession schema with common fields."""

    title: str = Field(..., description="Title of the meditation session")
    description: Optional[str] = Field(
        None, description="Description of the meditation session"
    )
    audio_url: Optional[str] = Field(
        None, description="URL to audio file for the meditation session"
    )
    duration_minutes: int = Field(..., description="Duration of the session in minutes")
    category: Optional[str] = Field(
        None, description="Category (e.g., 'mindfulness', 'breathing', 'sleep')"
    )


class MeditationSessionCreate(MeditationSessionBase):
    """Schema for creating a new meditation session."""

    pass


class MeditationSessionResponse(MeditationSessionBase):
    """Schema for meditation session response."""

    id: str = Field(..., description="Meditation session ID")
    created_at: datetime = Field(
        ..., description="Timestamp when meditation session was created"
    )


class MeditationLogBase(BaseModel):
    """Base MeditationLog schema with common fields."""

    session_id: str = Field(..., description="ID of the meditation session completed")
    duration_minutes: int = Field(
        ..., description="Actual duration of the meditation in minutes"
    )
    completed: bool = Field(
        True, description="Whether the meditation session was completed"
    )


class MeditationLogCreate(MeditationLogBase):
    """Schema for creating a new meditation log."""

    pass


class MeditationLogResponse(MeditationLogBase):
    """Schema for meditation log response."""

    id: str = Field(..., description="Meditation log ID")
    user_id: str = Field(..., description="User ID who completed the meditation")
    logged_at: datetime = Field(..., description="When the meditation was logged")
    created_at: datetime = Field(..., description="Timestamp when log was created")
