"""Pydantic schemas for Appointments API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AppointmentBase(BaseModel):
    """Base Appointment schema with common fields."""

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


class AppointmentCreate(AppointmentBase):
    """Schema for creating a new appointment."""

    pass


class AppointmentUpdate(AppointmentBase):
    """Schema for updating an existing appointment."""

    title: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response."""

    id: str = Field(..., description="Appointment ID")
    user_id: str = Field(..., description="User ID who owns this appointment")
    created_at: datetime = Field(
        ..., description="Timestamp when appointment was created"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when appointment was last updated"
    )
