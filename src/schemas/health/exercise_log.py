"""Pydantic schemas for ExerciseLog API requests and responses."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ExerciseLogCreate(BaseModel):
    """Schema for creating a new exercise log entry."""

    exercise_type: str = Field(
        ..., description="Type of exercise (e.g., 'running', 'swimming', 'yoga')"
    )
    duration_minutes: int = Field(..., ge=0, description="Duration in minutes")
    calories_burned: Optional[float] = Field(
        None, ge=0, description="Calories burned during exercise"
    )
    intensity: Literal["low", "moderate", "high", "vigorous"] = Field(
        ..., description="Intensity level of the exercise"
    )
    logged_at: Optional[datetime] = Field(
        None, description="Timestamp when exercise was logged"
    )


class ExerciseLogResponse(BaseModel):
    """Schema for exercise log response."""

    id: str = Field(..., description="Exercise log entry ID")
    user_id: str = Field(..., description="User ID who logged the exercise")
    exercise_type: str = Field(..., description="Type of exercise")
    duration_minutes: int = Field(..., description="Duration in minutes")
    calories_burned: Optional[float] = Field(None, description="Calories burned")
    intensity: Literal["low", "moderate", "high", "vigorous"] = Field(
        ..., description="Intensity level"
    )
    logged_at: datetime = Field(..., description="Timestamp when exercise was logged")
    created_at: datetime = Field(..., description="Timestamp when entry was created")
