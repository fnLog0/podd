"""Pydantic schemas for MoodLog API requests and responses."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class MoodLogCreate(BaseModel):
    """Schema for creating a new mood log entry."""

    mood: Literal[
        "very_bad", "bad", "neutral", "good", "very_good"
    ] = Field(..., description="Current mood")
    energy_level: Literal["very_low", "low", "medium", "high", "very_high"] = Field(
        ..., description="Energy level"
    )
    notes: Optional[str] = Field(None, description="Optional notes about the mood entry")
    logged_at: Optional[datetime] = Field(None, description="Timestamp when mood was logged")


class MoodLogResponse(BaseModel):
    """Schema for mood log response."""

    id: str = Field(..., description="Mood log entry ID")
    user_id: str = Field(..., description="User ID who logged the mood")
    mood: Literal["very_bad", "bad", "neutral", "good", "very_good"] = Field(..., description="Current mood")
    energy_level: Literal["very_low", "low", "medium", "high", "very_high"] = Field(..., description="Energy level")
    notes: Optional[str] = Field(None, description="Optional notes")
    logged_at: datetime = Field(..., description="Timestamp when mood was logged")
    created_at: datetime = Field(..., description="Timestamp when entry was created")
