"""Alarm and Notification schemas for LocusGraph.

This module defines the payloads and event definitions for Alarm and Notification events.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.schemas.events.locusgraph_events import ContextIdPattern, EventKind


# ==================== Alarm Types ====================


AlarmType = Literal["medication", "water", "meal", "meditation", "appointment"]


# ==================== Alarm Events ====================


class AlarmEventPayload(BaseModel):
    """Payload for Alarm events stored in LocusGraph."""

    type: AlarmType = Field(..., description="Type of alarm (medication, water, meal, meditation, appointment)")
    title: str = Field(..., description="Title of the alarm")
    message: Optional[str] = Field(None, description="Additional message for the alarm")
    time: str = Field(..., description="Time in HH:MM format (24-hour)")
    days_of_week: list[str] = Field(
        default_factory=lambda: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        description="Days of the week the alarm should fire (3-letter lowercase)",
    )
    active: bool = Field(True, description="Whether the alarm is currently active")
    reference_id: Optional[str] = Field(
        None, description="Reference ID to linked entity (e.g., medication_id, appointment_id)"
    )
    user_id: str = Field(..., description="User ID who owns this alarm")


class AlarmEventDefinition:
    """Definition and metadata for Alarm events in LocusGraph."""

    EVENT_KIND = EventKind.ALARM_CREATE
    CONTEXT_PATTERN = ContextIdPattern.ALARM
    PAYLOAD_MODEL = AlarmEventPayload

    @staticmethod
    def get_context_id(alarm_id: str) -> str:
        """Generate context ID for an alarm entry.

        Args:
            alarm_id: The alarm's unique identifier

        Returns:
            Context ID in format: alarm:<alarm_id>
        """
        return ContextIdPattern.ALARM.format(id=alarm_id)

    @staticmethod
    def create_payload(
        type: AlarmType,
        title: str,
        time: str,
        user_id: str,
        message: Optional[str] = None,
        days_of_week: Optional[list[str]] = None,
        active: bool = True,
        reference_id: Optional[str] = None,
    ) -> dict:
        """Create an Alarm event payload.

        Args:
            type: Type of alarm
            title: Title of the alarm
            time: Time in HH:MM format
            user_id: User ID who owns this alarm
            message: Additional message
            days_of_week: Days of the week (3-letter lowercase)
            active: Whether alarm is active
            reference_id: Reference to linked entity

        Returns:
            Dictionary containing the alarm data
        """
        payload = AlarmEventPayload(
            type=type,
            title=title,
            message=message,
            time=time,
            days_of_week=days_of_week or ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
            active=active,
            reference_id=reference_id,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")


# ==================== Notification Events ====================


class NotificationEventPayload(BaseModel):
    """Payload for Notification events stored in LocusGraph."""

    alarm_id: str = Field(..., description="ID of the alarm that triggered this notification")
    title: str = Field(..., description="Title of the notification")
    message: str = Field(..., description="Message content of the notification")
    type: AlarmType = Field(..., description="Type of notification (matches alarm type)")
    read: bool = Field(False, description="Whether the notification has been read")
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp when notification was created",
    )
    user_id: str = Field(..., description="User ID who owns this notification")


class NotificationEventDefinition:
    """Definition and metadata for Notification events in LocusGraph."""

    EVENT_KIND = EventKind.NOTIFICATION_CREATE
    CONTEXT_PATTERN = ContextIdPattern.NOTIFICATION
    PAYLOAD_MODEL = NotificationEventPayload

    @staticmethod
    def get_context_id(notification_id: str) -> str:
        """Generate context ID for a notification entry.

        Args:
            notification_id: The notification's unique identifier

        Returns:
            Context ID in format: notification:<notification_id>
        """
        return ContextIdPattern.NOTIFICATION.format(id=notification_id)

    @staticmethod
    def create_payload(
        alarm_id: str,
        title: str,
        message: str,
        type: AlarmType,
        user_id: str,
    ) -> dict:
        """Create a Notification event payload.

        Args:
            alarm_id: ID of the alarm that triggered this notification
            title: Title of the notification
            message: Message content
            type: Type of notification
            user_id: User ID who owns this notification

        Returns:
            Dictionary containing the notification data
        """
        payload = NotificationEventPayload(
            alarm_id=alarm_id,
            title=title,
            message=message,
            type=type,
            read=False,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")
