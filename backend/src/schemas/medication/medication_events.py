"""Medication event schemas for LocusGraph.

This module defines the payloads and event definitions for Medication,
MedicationLog, and MedicationSchedule events.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.schemas.events.locusgraph_events import ContextIdPattern, EventKind


# ==================== Medication Events ====================


class MedicationEventPayload(BaseModel):
    """Payload for Medication events stored in LocusGraph."""

    name: str = Field(..., description="Medication name")
    dosage: str = Field(..., description="Dosage amount (e.g., '10mg', '5ml')")
    frequency: str = Field(
        ..., description="How often to take (e.g., 'twice daily', 'once daily')"
    )
    instructions: Optional[str] = Field(
        None,
        description="Additional instructions (e.g., 'take with food', 'avoid alcohol')",
    )
    active: bool = Field(True, description="Whether the medication is currently active")
    user_id: str = Field(..., description="User ID who owns this medication")


class MedicationLogEventPayload(BaseModel):
    """Payload for Medication Log events stored in LocusGraph."""

    medication_id: str = Field(..., description="ID of the medication taken")
    scheduled_time: Optional[datetime] = Field(
        None, description="Scheduled time for medication"
    )
    taken_at: datetime = Field(
        ..., description="When the medication was actually taken"
    )
    notes: Optional[str] = Field(
        None, description="Optional notes about the medication intake"
    )
    user_id: str = Field(..., description="User ID who took the medication")


class MedicationScheduleEventPayload(BaseModel):
    """Payload for MedicationSchedule events stored in LocusGraph."""

    medication_id: str = Field(
        ..., description="ID of the medication this schedule belongs to"
    )
    time_of_day: str = Field(
        ..., description="Time to take medication (e.g., '08:00', '12:30')"
    )
    days_of_week: list[Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]] = (
        Field(default_factory=list, description="Days of week to take medication")
    )
    user_id: str = Field(..., description="User ID who owns this schedule")


# ==================== Medication Event Definition ====================


class MedicationEventDefinition:
    """Definition and metadata for Medication events in LocusGraph."""

    EVENT_KIND = EventKind.MEDICATION_CREATE
    CONTEXT_PATTERN = ContextIdPattern.MEDICATION
    PAYLOAD_MODEL = MedicationEventPayload

    @staticmethod
    def get_context_id(medication_id: str) -> str:
        """Generate context ID for a medication entry.

        Args:
            medication_id: The medication's unique identifier

        Returns:
            Context ID in format: medication:<medication_id>
        """
        return ContextIdPattern.MEDICATION.format(id=medication_id)

    @staticmethod
    def create_payload(
        name: str,
        dosage: str,
        frequency: str,
        user_id: str,
        instructions: Optional[str] = None,
        active: bool = True,
    ) -> dict:
        """Create a Medication event payload.

        Args:
            name: Medication name
            dosage: Dosage amount (e.g., '10mg', '5ml')
            frequency: How often to take (e.g., 'twice daily', 'once daily')
            user_id: User ID who owns this medication
            instructions: Additional instructions
            active: Whether the medication is currently active

        Returns:
            Dictionary containing the medication data
        """
        payload = MedicationEventPayload(
            name=name,
            dosage=dosage,
            frequency=frequency,
            instructions=instructions,
            active=active,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")


# ==================== MedicationSchedule Event Definition ====================


class MedicationScheduleEventDefinition:
    """Definition and metadata for MedicationSchedule events in LocusGraph."""

    EVENT_KIND = EventKind.MEDICATION_SCHEDULE_CREATE
    CONTEXT_PATTERN = ContextIdPattern.MEDICATION_SCHEDULE
    PAYLOAD_MODEL = MedicationScheduleEventPayload

    @staticmethod
    def get_context_id(schedule_id: str) -> str:
        """Generate context ID for a medication schedule entry.

        Args:
            schedule_id: The schedule's unique identifier

        Returns:
            Context ID in format: med_schedule:<schedule_id>
        """
        return ContextIdPattern.MEDICATION_SCHEDULE.format(id=schedule_id)

    @staticmethod
    def create_payload(
        medication_id: str,
        time_of_day: str,
        user_id: str,
        days_of_week: Optional[list[str]] = None,
    ) -> dict:
        """Create a MedicationSchedule event payload.

        Args:
            medication_id: ID of the medication this schedule belongs to
            time_of_day: Time to take medication (e.g., '08:00', '12:30')
            user_id: User ID who owns this schedule
            days_of_week: Days of week to take medication

        Returns:
            Dictionary containing the medication schedule data
        """
        payload = MedicationScheduleEventPayload(
            medication_id=medication_id,
            time_of_day=time_of_day,
            days_of_week=days_of_week or [],
            user_id=user_id,
        )
        return payload.model_dump(mode="json")


# ==================== MedicationLog Event Definition ====================


class MedicationLogEventDefinition:
    """Definition and metadata for MedicationLog events in LocusGraph."""

    EVENT_KIND = EventKind.MEDICATION_LOG
    CONTEXT_PATTERN = ContextIdPattern.MEDICATION_LOG
    PAYLOAD_MODEL = MedicationLogEventPayload

    @staticmethod
    def get_context_id(log_id: str) -> str:
        """Generate context ID for a medication log entry.

        Args:
            log_id: The medication log entry's unique identifier

        Returns:
            Context ID in format: med_log:<log_id>
        """
        return ContextIdPattern.MEDICATION_LOG.format(id=log_id)

    @staticmethod
    def create_payload(
        medication_id: str,
        taken_at: datetime,
        user_id: str,
        scheduled_time: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> dict:
        """Create a MedicationLog event payload.

        Args:
            medication_id: ID of the medication taken
            taken_at: When the medication was actually taken
            user_id: User ID who took the medication
            scheduled_time: Scheduled time for medication
            notes: Optional notes about the medication intake

        Returns:
            Dictionary containing the medication log data
        """
        payload = MedicationLogEventPayload(
            medication_id=medication_id,
            scheduled_time=scheduled_time,
            taken_at=taken_at,
            notes=notes,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")
