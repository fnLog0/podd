"""Emergency contact event schemas for LocusGraph.

This module defines the payloads and event definitions for EmergencyContact events.
"""

from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.events.locusgraph_events import ContextIdPattern, EventKind


# ==================== EmergencyContact Events ====================


class EmergencyContactEventPayload(BaseModel):
    """Payload for EmergencyContact events stored in LocusGraph."""

    name: str = Field(..., description="Name of the emergency contact")
    relationship: Optional[str] = Field(
        None, description="Relationship to the user (e.g., 'spouse', 'parent')"
    )
    phone: str = Field(..., description="Phone number of the emergency contact")
    is_primary: bool = Field(
        False, description="Whether this is the primary emergency contact"
    )
    user_id: str = Field(..., description="User ID who owns this emergency contact")


class EmergencyContactEventDefinition:
    """Definition and metadata for EmergencyContact events in LocusGraph."""

    EVENT_KIND = EventKind.EMERGENCY_CONTACT_CREATE
    CONTEXT_PATTERN = ContextIdPattern.EMERGENCY_CONTACT
    PAYLOAD_MODEL = EmergencyContactEventPayload

    @staticmethod
    def get_context_id(contact_id: str) -> str:
        """Generate context ID for an emergency contact entry.

        Args:
            contact_id: The emergency contact's unique identifier

        Returns:
            Context ID in format: emergency_contact:<contact_id>
        """
        return ContextIdPattern.EMERGENCY_CONTACT.format(id=contact_id)

    @staticmethod
    def create_payload(
        name: str,
        phone: str,
        user_id: str,
        relationship: Optional[str] = None,
        is_primary: bool = False,
    ) -> dict:
        """Create an EmergencyContact event payload.

        Args:
            name: Name of the emergency contact
            phone: Phone number of the emergency contact
            user_id: User ID who owns this emergency contact
            relationship: Relationship to the user
            is_primary: Whether this is the primary emergency contact

        Returns:
            Dictionary containing the emergency contact data
        """
        payload = EmergencyContactEventPayload(
            name=name,
            relationship=relationship,
            phone=phone,
            is_primary=is_primary,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")
