"""Pydantic schemas for SleepLog API requests and responses."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class SleepLogCreate(BaseModel):
    """Schema for creating a new sleep log entry."""

    sleep_start: datetime = Field(..., description="When sleep started")
    sleep_end: datetime = Field(..., description="When sleep ended")
    quality: Literal["poor", "fair", "good", "excellent"] = Field(
        "good", description="Quality of sleep (poor, fair, good, excellent)"
    )
    notes: Optional[str] = Field(
        None, description="Optional notes about the sleep session"
    )


class SleepLogResponse(BaseModel):
    """Schema for sleep log response."""

    id: str = Field(..., description="Sleep log entry ID")
    user_id: str = Field(..., description="User ID who logged the sleep")
    sleep_start: datetime = Field(..., description="When sleep started")
    sleep_end: datetime = Field(..., description="When sleep ended")
    quality: Literal["poor", "fair", "good", "excellent"] = Field(
        ..., description="Quality of sleep"
    )
    notes: Optional[str] = Field(
        None, description="Optional notes about the sleep session"
    )
    created_at: datetime = Field(..., description="Timestamp when entry was created")
