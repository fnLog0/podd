"""Pydantic schemas for MedicationLog API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class MedicationLogBase(BaseModel):
    """Base MedicationLog schema with common fields."""

    medication_id: Optional[str] = Field(None, description="ID of the medication taken")
    medication_name: Optional[str] = Field(
        None, description="Name of the medication taken"
    )
    scheduled_time: Optional[datetime] = Field(
        None, description="Scheduled time for medication"
    )
    taken_at: Optional[datetime] = Field(
        None, description="When the medication was actually taken"
    )
    notes: Optional[str] = Field(
        None, description="Optional notes about the medication intake"
    )

    @model_validator(mode="after")
    def validate_medication_reference(self):
        """Ensure at least one of medication_id or medication_name is provided."""
        if not self.medication_id and not self.medication_name:
            raise ValueError("Either medication_id or medication_name must be provided")
        return self


class MedicationLogCreate(MedicationLogBase):
    """Schema for creating a new medication log entry."""

    related_to: list[str] = Field(
        default_factory=list,
        description="IDs of related events to link this log to (e.g., vitals readings)",
    )


class MedicationLogResponse(MedicationLogBase):
    """Schema for medication log response."""

    id: str = Field(..., description="Medication log entry ID")
    user_id: str = Field(..., description="User ID who took the medication")
    medication_name: Optional[str] = Field(
        None, description="Medication name (joined from medication)"
    )
    taken_at: datetime = Field(..., description="When the medication was taken")
    created_at: datetime = Field(..., description="Timestamp when log was created")
