"""Pydantic schemas for Emergency Contacts API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EmergencyContactBase(BaseModel):
    """Base EmergencyContact schema with common fields."""

    name: str = Field(..., description="Name of the emergency contact")
    relationship: Optional[str] = Field(
        None, description="Relationship to the user (e.g., 'spouse', 'parent')"
    )
    phone: str = Field(..., description="Phone number of the emergency contact")
    is_primary: bool = Field(
        False, description="Whether this is the primary emergency contact"
    )


class EmergencyContactCreate(EmergencyContactBase):
    """Schema for creating a new emergency contact."""

    pass


class EmergencyContactUpdate(EmergencyContactBase):
    """Schema for updating an existing emergency contact."""

    name: Optional[str] = None
    phone: Optional[str] = None
    is_primary: Optional[bool] = None


class EmergencyContactResponse(EmergencyContactBase):
    """Schema for emergency contact response."""

    id: str = Field(..., description="Emergency contact ID")
    user_id: str = Field(..., description="User ID who owns this emergency contact")
    created_at: datetime = Field(
        ..., description="Timestamp when emergency contact was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when emergency contact was last updated"
    )
