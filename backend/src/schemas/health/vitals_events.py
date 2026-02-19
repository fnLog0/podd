"""Vitals event schemas for LocusGraph.

This module defines the payload and event definition for Vitals events.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.events.locusgraph_events import ContextIdPattern, EventKind


# ==================== Vitals Events ====================


class VitalsEventPayload(BaseModel):
    """Payload for Vitals events stored in LocusGraph."""

    blood_pressure_systolic: Optional[int] = Field(
        None, ge=50, le=250, description="Systolic blood pressure (mmHg)"
    )
    blood_pressure_diastolic: Optional[int] = Field(
        None, ge=30, le=150, description="Diastolic blood pressure (mmHg)"
    )
    heart_rate: Optional[int] = Field(
        None, ge=30, le=220, description="Heart rate (bpm)"
    )
    blood_sugar: Optional[float] = Field(
        None, ge=0, le=600, description="Blood sugar level (mg/dL)"
    )
    temperature: Optional[float] = Field(
        None, ge=30, le=45, description="Body temperature (Celsius)"
    )
    weight_kg: Optional[float] = Field(None, ge=0, description="Weight in kilograms")
    logged_at: datetime = Field(..., description="Timestamp when vitals were recorded")
    user_id: str = Field(..., description="User ID who recorded vitals")


# ==================== Vitals Event Definition ====================


class VitalsEventDefinition:
    """Definition and metadata for Vitals events in LocusGraph."""

    EVENT_KIND = EventKind.VITALS_CREATE
    CONTEXT_PATTERN = ContextIdPattern.VITALS
    PAYLOAD_MODEL = VitalsEventPayload

    @staticmethod
    def get_context_id(vitals_id: str) -> str:
        """Generate context ID for a vitals entry.

        Args:
            vitals_id: The vitals entry's unique identifier

        Returns:
            Context ID in format: vitals:<vitals_id>
        """
        return ContextIdPattern.VITALS.format(id=vitals_id)

    @staticmethod
    def create_payload(
        logged_at: datetime,
        user_id: str,
        blood_pressure_systolic: Optional[int] = None,
        blood_pressure_diastolic: Optional[int] = None,
        heart_rate: Optional[int] = None,
        blood_sugar: Optional[float] = None,
        temperature: Optional[float] = None,
        weight_kg: Optional[float] = None,
    ) -> dict:
        """Create a Vitals event payload.

        Args:
            logged_at: Timestamp when vitals were recorded
            user_id: User ID who recorded vitals
            blood_pressure_systolic: Systolic blood pressure (mmHg)
            blood_pressure_diastolic: Diastolic blood pressure (mmHg)
            heart_rate: Heart rate (bpm)
            blood_sugar: Blood sugar level (mg/dL)
            temperature: Body temperature (Celsius)
            weight_kg: Weight in kilograms

        Returns:
            Dictionary containing the vitals data
        """
        payload = VitalsEventPayload(
            blood_pressure_systolic=blood_pressure_systolic,
            blood_pressure_diastolic=blood_pressure_diastolic,
            heart_rate=heart_rate,
            blood_sugar=blood_sugar,
            temperature=temperature,
            weight_kg=weight_kg,
            logged_at=logged_at,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")
