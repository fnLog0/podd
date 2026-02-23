"""Meditation event schemas for LocusGraph.

This module defines the payloads and event definitions for MeditationSession and MeditationLog events.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.schemas.events.locusgraph_events import ContextIdPattern, EventKind


# ==================== MeditationSession Events ====================


class MeditationSessionEventPayload(BaseModel):
    """Payload for MeditationSession events stored in LocusGraph."""

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


class MeditationSessionEventDefinition:
    """Definition and metadata for MeditationSession events in LocusGraph."""

    EVENT_KIND = EventKind.MEDITATION_SESSION_CREATE
    CONTEXT_PATTERN = ContextIdPattern.MEDITATION_SESSION
    PAYLOAD_MODEL = MeditationSessionEventPayload

    @staticmethod
    def get_context_id(session_id: str) -> str:
        """Generate context ID for a meditation session entry.

        Args:
            session_id: The meditation session's unique identifier

        Returns:
            Context ID in format: meditation_session:<session_id>
        """
        return ContextIdPattern.MEDITATION_SESSION.format(id=session_id)

    @staticmethod
    def create_payload(
        title: str,
        duration_minutes: int,
        description: Optional[str] = None,
        audio_url: Optional[str] = None,
        category: Optional[str] = None,
    ) -> dict:
        """Create a MeditationSession event payload.

        Args:
            title: Title of the meditation session
            duration_minutes: Duration of the session in minutes
            description: Description of the meditation session
            audio_url: URL to audio file for the meditation session
            category: Category (e.g., 'mindfulness', 'breathing', 'sleep')

        Returns:
            Dictionary containing the meditation session data
        """
        payload = MeditationSessionEventPayload(
            title=title,
            description=description,
            audio_url=audio_url,
            duration_minutes=duration_minutes,
            category=category,
        )
        return payload.model_dump(mode="json")


# ==================== MeditationLog Events ====================


class MeditationLogEventPayload(BaseModel):
    """Payload for MeditationLog events stored in LocusGraph."""

    session_id: str = Field(..., description="ID of the meditation session completed")
    duration_minutes: int = Field(
        ..., description="Actual duration of the meditation in minutes"
    )
    completed: bool = Field(
        True, description="Whether the meditation session was completed"
    )
    logged_at: datetime = Field(..., description="When the meditation was logged")
    user_id: str = Field(..., description="User ID who completed the meditation")


class MeditationLogEventDefinition:
    """Definition and metadata for MeditationLog events in LocusGraph."""

    EVENT_KIND = EventKind.MEDITATION_LOG
    CONTEXT_PATTERN = ContextIdPattern.MEDITATION_LOG
    PAYLOAD_MODEL = MeditationLogEventPayload

    @staticmethod
    def get_context_id(log_id: str) -> str:
        """Generate context ID for a meditation log entry.

        Args:
            log_id: The meditation log entry's unique identifier

        Returns:
            Context ID in format: meditation_log:<log_id>
        """
        return ContextIdPattern.MEDITATION_LOG.format(id=log_id)

    @staticmethod
    def create_payload(
        session_id: str,
        duration_minutes: int,
        user_id: str,
        completed: bool = True,
        logged_at: Optional[datetime] = None,
    ) -> dict:
        """Create a MeditationLog event payload.

        Args:
            session_id: ID of the meditation session completed
            duration_minutes: Actual duration of the meditation in minutes
            user_id: User ID who completed the meditation
            completed: Whether the meditation session was completed
            logged_at: When the meditation was logged

        Returns:
            Dictionary containing the meditation log data
        """
        payload = MeditationLogEventPayload(
            session_id=session_id,
            duration_minutes=duration_minutes,
            completed=completed,
            logged_at=logged_at or datetime.now(),
            user_id=user_id,
        )
        return payload.model_dump(mode="json")
