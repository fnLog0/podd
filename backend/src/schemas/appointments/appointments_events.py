"""Appointment event schemas for LocusGraph.

This module defines the payloads and event definitions for Appointment events.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.events.locusgraph_events import ContextIdPattern, EventKind


# ==================== Appointment Events ====================


class AppointmentEventPayload(BaseModel):
    """Payload for Appointment events stored in LocusGraph."""

    title: str = Field(..., description="Title of the appointment")
    doctor_name: Optional[str] = Field(None, description="Name of the doctor")
    location: Optional[str] = Field(None, description="Location of the appointment")
    scheduled_at: datetime = Field(..., description="When the appointment is scheduled")
    notes: Optional[str] = Field(
        None, description="Additional notes about the appointment"
    )
    reminder_minutes_before: Optional[int] = Field(
        None, description="Minutes before appointment to send reminder"
    )
    user_id: str = Field(..., description="User ID who owns this appointment")


class AppointmentEventDefinition:
    """Definition and metadata for Appointment events in LocusGraph."""

    EVENT_KIND = EventKind.APPOINTMENT_CREATE
    CONTEXT_PATTERN = ContextIdPattern.APPOINTMENT
    PAYLOAD_MODEL = AppointmentEventPayload

    @staticmethod
    def get_context_id(appointment_id: str) -> str:
        """Generate context ID for an appointment entry.

        Args:
            appointment_id: The appointment's unique identifier

        Returns:
            Context ID in format: appointment:<appointment_id>
        """
        return ContextIdPattern.APPOINTMENT.format(id=appointment_id)

    @staticmethod
    def create_payload(
        title: str,
        scheduled_at: datetime,
        user_id: str,
        doctor_name: Optional[str] = None,
        location: Optional[str] = None,
        notes: Optional[str] = None,
        reminder_minutes_before: Optional[int] = None,
    ) -> dict:
        """Create an Appointment event payload.

        Args:
            title: Title of the appointment
            scheduled_at: When the appointment is scheduled
            user_id: User ID who owns this appointment
            doctor_name: Name of the doctor
            location: Location of the appointment
            notes: Additional notes about the appointment
            reminder_minutes_before: Minutes before appointment to send reminder

        Returns:
            Dictionary containing the appointment data
        """
        payload = AppointmentEventPayload(
            title=title,
            doctor_name=doctor_name,
            location=location,
            scheduled_at=scheduled_at,
            notes=notes,
            reminder_minutes_before=reminder_minutes_before,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")
