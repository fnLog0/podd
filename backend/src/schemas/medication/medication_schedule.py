"""Pydantic schemas for MedicationSchedule API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MedicationScheduleBase(BaseModel):
    """Base MedicationSchedule schema with common fields."""

    medication_id: str = Field(
        ...,
        description="ID of the medication this schedule belongs to"
    )
    time_of_day: str = Field(
        ...,
        description="Time to take medication (e.g., '08:00', '12:30')"
    )
    days_of_week: list[str] = Field(
        default_factory=list,
        description="Days of week to take medication (mon, tue, wed, thu, fri, sat, sun)"
    )


class MedicationScheduleCreate(MedicationScheduleBase):
    """Schema for creating a new medication schedule."""

    related_to: list[str] = Field(
        default_factory=list,
        description="IDs of related events to link this schedule to"
    )


class MedicationScheduleUpdate(MedicationScheduleBase):
    """Schema for updating an existing medication schedule."""

    medication_id: Optional[str] = None
    time_of_day: Optional[str] = None


class MedicationScheduleResponse(MedicationScheduleBase):
    """Schema for medication schedule response."""

    id: str = Field(..., description="Medication schedule ID")
    user_id: str = Field(..., description="User ID who owns this schedule")
    medication_name: Optional[str] = Field(None, description="Medication name (joined from medication)")
    created_at: datetime = Field(..., description="Timestamp when schedule was created")
    updated_at: datetime = Field(..., description="Timestamp when schedule was last updated")
