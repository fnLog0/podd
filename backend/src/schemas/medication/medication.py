"""Pydantic schemas for Medication API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MedicationBase(BaseModel):
    """Base Medication schema with common fields."""

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


class MedicationCreate(MedicationBase):
    """Schema for creating a new medication."""

    pass


class MedicationUpdate(MedicationBase):
    """Schema for updating an existing medication."""

    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None


class MedicationResponse(MedicationBase):
    """Schema for medication response."""

    id: str = Field(..., description="Medication ID")
    user_id: str = Field(..., description="User ID who owns this medication")
    created_at: datetime = Field(
        ..., description="Timestamp when medication was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when medication was last updated"
    )
