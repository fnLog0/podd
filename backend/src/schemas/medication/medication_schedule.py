"""Pydantic schemas for MedicationSchedule API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class MedicationScheduleBase(BaseModel):
    """Base MedicationSchedule schema with common fields."""

    medication_id: Optional[str] = Field(
        None, description="ID of the medication this schedule belongs to"
    )
    time_of_day: str = Field(
        ..., description="Time to take medication (e.g., '08:00', '12:30')"
    )
    days_of_week: list[str] = Field(
        default_factory=list,
        description="Days of week to take medication (mon, tue, wed, thu, fri, sat, sun)",
    )


class MedicationScheduleCreate(MedicationScheduleBase):
    """Schema for creating a new medication schedule."""

    medication_name: Optional[str] = Field(
        None, description="Name of the medication (alternative to medication_id)"
    )
    related_to: list[str] = Field(
        default_factory=list,
        description="IDs of related events to link this schedule to",
    )

    @model_validator(mode="after")
    def validate_medication_reference(self):
        """Ensure at least one of medication_id or medication_name is provided."""
        if not self.medication_id and not self.medication_name:
            raise ValueError("Either medication_id or medication_name must be provided")
        return self


class MedicationScheduleUpdate(MedicationScheduleBase):
    """Schema for updating an existing medication schedule."""

    medication_id: Optional[str] = None
    time_of_day: Optional[str] = None


class MedicationScheduleResponse(MedicationScheduleBase):
    """Schema for medication schedule response."""

    id: str = Field(..., description="Medication schedule ID")
    user_id: str = Field(..., description="User ID who owns this schedule")
    medication_name: Optional[str] = Field(
        None, description="Medication name (joined from medication)"
    )
    created_at: datetime = Field(..., description="Timestamp when schedule was created")
    updated_at: datetime = Field(
        ..., description="Timestamp when schedule was last updated"
    )
