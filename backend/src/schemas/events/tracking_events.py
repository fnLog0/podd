"""Tracking event schemas for LocusGraph.

This module defines the payloads and event definitions for WaterLog,
SleepLog, ExerciseLog, and MoodLog events.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.schemas.events.locusgraph_events import ContextIdPattern, EventKind


# ==================== WaterLog Events ====================


class WaterLogEventPayload(BaseModel):
    """Payload for WaterLog events stored in LocusGraph."""

    amount_ml: float = Field(..., ge=0, description="Amount of water in milliliters")
    logged_at: datetime = Field(..., description="Timestamp when water was logged")
    user_id: str = Field(..., description="User ID who logged the water")


# ==================== SleepLog Events ====================


class SleepLogEventPayload(BaseModel):
    """Payload for SleepLog events stored in LocusGraph."""

    sleep_start: datetime = Field(..., description="When sleep started")
    sleep_end: datetime = Field(..., description="When sleep ended")
    quality: Literal["poor", "fair", "good", "excellent"] = Field(
        ..., description="Quality of sleep"
    )
    notes: Optional[str] = Field(
        None, description="Optional notes about the sleep session"
    )
    user_id: str = Field(..., description="User ID who logged the sleep")


# ==================== ExerciseLog Events ====================


class ExerciseLogEventPayload(BaseModel):
    """Payload for ExerciseLog events stored in LocusGraph."""

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
    logged_at: datetime = Field(..., description="Timestamp when exercise was logged")
    user_id: str = Field(..., description="User ID who logged the exercise")


# ==================== MoodLog Events ====================


class MoodLogEventPayload(BaseModel):
    """Payload for MoodLog events stored in LocusGraph."""

    mood: Literal["very_bad", "bad", "neutral", "good", "very_good"] = Field(
        ..., description="Current mood"
    )
    energy_level: Literal["very_low", "low", "medium", "high", "very_high"] = Field(
        ..., description="Energy level"
    )
    notes: Optional[str] = Field(
        None, description="Optional notes about the mood entry"
    )
    logged_at: datetime = Field(..., description="Timestamp when mood was logged")
    user_id: str = Field(..., description="User ID who logged the mood")


# ==================== WaterLog Event Definition ====================


class WaterLogEventDefinition:
    """Definition and metadata for WaterLog events in LocusGraph."""

    EVENT_KIND = EventKind.WATER_LOG_CREATE
    CONTEXT_PATTERN = ContextIdPattern.WATER_LOG
    PAYLOAD_MODEL = WaterLogEventPayload

    @staticmethod
    def get_context_id(water_log_id: str) -> str:
        """Generate context ID for a water log entry.

        Args:
            water_log_id: The water log entry's unique identifier

        Returns:
            Context ID in format: water:<water_log_id>
        """
        return ContextIdPattern.WATER_LOG.format(id=water_log_id)

    @staticmethod
    def create_payload(
        amount_ml: float,
        logged_at: datetime,
        user_id: str,
    ) -> dict:
        """Create a WaterLog event payload.

        Args:
            amount_ml: Amount of water in milliliters
            logged_at: Timestamp when water was logged
            user_id: User ID who logged the water

        Returns:
            Dictionary containing the water log data
        """
        payload = WaterLogEventPayload(
            amount_ml=amount_ml,
            logged_at=logged_at,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")


# ==================== SleepLog Event Definition ====================


class SleepLogEventDefinition:
    """Definition and metadata for SleepLog events in LocusGraph."""

    EVENT_KIND = EventKind.SLEEP_LOG_CREATE
    CONTEXT_PATTERN = ContextIdPattern.SLEEP_LOG
    PAYLOAD_MODEL = SleepLogEventPayload

    @staticmethod
    def get_context_id(sleep_log_id: str) -> str:
        """Generate context ID for a sleep log entry.

        Args:
            sleep_log_id: The sleep log entry's unique identifier

        Returns:
            Context ID in format: sleep:<sleep_log_id>
        """
        return ContextIdPattern.SLEEP_LOG.format(id=sleep_log_id)

    @staticmethod
    def create_payload(
        sleep_start: datetime,
        sleep_end: datetime,
        quality: str,
        user_id: str,
        notes: Optional[str] = None,
    ) -> dict:
        """Create a SleepLog event payload.

        Args:
            sleep_start: When sleep started
            sleep_end: When sleep ended
            quality: Quality of sleep (poor, fair, good, excellent)
            user_id: User ID who logged the sleep
            notes: Optional notes about the sleep session

        Returns:
            Dictionary containing the sleep log data
        """
        payload = SleepLogEventPayload(
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            quality=quality,
            notes=notes,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")


# ==================== ExerciseLog Event Definition ====================


class ExerciseLogEventDefinition:
    """Definition and metadata for ExerciseLog events in LocusGraph."""

    EVENT_KIND = EventKind.EXERCISE_LOG_CREATE
    CONTEXT_PATTERN = ContextIdPattern.EXERCISE_LOG
    PAYLOAD_MODEL = ExerciseLogEventPayload

    @staticmethod
    def get_context_id(exercise_log_id: str) -> str:
        """Generate context ID for an exercise log entry.

        Args:
            exercise_log_id: The exercise log entry's unique identifier

        Returns:
            Context ID in format: exercise:<exercise_log_id>
        """
        return ContextIdPattern.EXERCISE_LOG.format(id=exercise_log_id)

    @staticmethod
    def create_payload(
        exercise_type: str,
        duration_minutes: int,
        intensity: str,
        logged_at: datetime,
        user_id: str,
        calories_burned: Optional[float] = None,
    ) -> dict:
        """Create an ExerciseLog event payload.

        Args:
            exercise_type: Type of exercise (e.g., running, swimming, yoga)
            duration_minutes: Duration in minutes
            intensity: Intensity level (low, moderate, high, vigorous)
            logged_at: Timestamp when exercise was logged
            user_id: User ID who logged the exercise
            calories_burned: Calories burned during exercise

        Returns:
            Dictionary containing the exercise log data
        """
        payload = ExerciseLogEventPayload(
            exercise_type=exercise_type,
            duration_minutes=duration_minutes,
            calories_burned=calories_burned,
            intensity=intensity,
            logged_at=logged_at,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")


# ==================== MoodLog Event Definition ====================


class MoodLogEventDefinition:
    """Definition and metadata for MoodLog events in LocusGraph."""

    EVENT_KIND = EventKind.MOOD_LOG_CREATE
    CONTEXT_PATTERN = ContextIdPattern.MOOD_LOG
    PAYLOAD_MODEL = MoodLogEventPayload

    @staticmethod
    def get_context_id(mood_log_id: str) -> str:
        """Generate context ID for a mood log entry.

        Args:
            mood_log_id: The mood log entry's unique identifier

        Returns:
            Context ID in format: mood:<mood_log_id>
        """
        return ContextIdPattern.MOOD_LOG.format(id=mood_log_id)

    @staticmethod
    def create_payload(
        mood: str,
        energy_level: str,
        logged_at: datetime,
        user_id: str,
        notes: Optional[str] = None,
    ) -> dict:
        """Create a MoodLog event payload.

        Args:
            mood: Current mood (very_bad, bad, neutral, good, very_good)
            energy_level: Energy level (very_low, low, medium, high, very_high)
            logged_at: Timestamp when mood was logged
            user_id: User ID who logged the mood
            notes: Optional notes about the mood entry

        Returns:
            Dictionary containing the mood log data
        """
        payload = MoodLogEventPayload(
            mood=mood,
            energy_level=energy_level,
            notes=notes,
            logged_at=logged_at,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")
