"""Profile event schemas for LocusGraph.

This module defines the payload and event definition for Profile events.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.events.locusgraph_events import ContextIdPattern, EventKind


# ==================== Profile Events ====================


class ProfileEventPayload(BaseModel):
    """Payload for Profile events stored in LocusGraph."""

    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, description="User's gender")
    height_cm: Optional[float] = Field(None, ge=0, description="Height in centimeters")
    weight_kg: Optional[float] = Field(None, ge=0, description="Weight in kilograms")
    blood_type: Optional[str] = Field(
        None,
        pattern=r"^[ABO][+-]$",
        description="Blood type (A+, A-, B+, B-, O+, O-, AB+, AB-)",
    )
    allergies: list[str] = Field(
        default_factory=list, description="List of known allergies"
    )
    medical_conditions: list[str] = Field(
        default_factory=list, description="List of medical conditions"
    )
    dietary_preferences: list[str] = Field(
        default_factory=list,
        description="Dietary preferences (e.g., vegetarian, vegan, gluten-free)",
    )


# ==================== Profile Event Definition ====================


class ProfileEventDefinition:
    """Definition and metadata for Profile events in LocusGraph."""

    EVENT_KIND = EventKind.PROFILE_CREATE
    CONTEXT_PATTERN = ContextIdPattern.PROFILE
    PAYLOAD_MODEL = ProfileEventPayload

    @staticmethod
    def get_context_id(user_id: str) -> str:
        """Generate context ID for a user's profile.

        Args:
            user_id: The user's unique identifier

        Returns:
            Context ID in format: profile:<user_id>
        """
        return ContextIdPattern.PROFILE.format(user_id=user_id)

    @staticmethod
    def create_payload(
        date_of_birth: Optional[date] = None,
        gender: Optional[str] = None,
        height_cm: Optional[float] = None,
        weight_kg: Optional[float] = None,
        blood_type: Optional[str] = None,
        allergies: Optional[list[str]] = None,
        medical_conditions: Optional[list[str]] = None,
        dietary_preferences: Optional[list[str]] = None,
    ) -> dict:
        """Create a Profile event payload.

        Args:
            date_of_birth: User's date of birth
            gender: User's gender
            height_cm: Height in centimeters
            weight_kg: Weight in kilograms
            blood_type: Blood type
            allergies: List of known allergies
            medical_conditions: List of medical conditions
            dietary_preferences: Dietary preferences

        Returns:
            Dictionary containing the profile data
        """
        payload = ProfileEventPayload(
            date_of_birth=date_of_birth,
            gender=gender,
            height_cm=height_cm,
            weight_kg=weight_kg,
            blood_type=blood_type,
            allergies=allergies or [],
            medical_conditions=medical_conditions or [],
            dietary_preferences=dietary_preferences or [],
        )
        return payload.model_dump(mode="json")
