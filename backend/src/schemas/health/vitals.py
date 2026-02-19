"""Pydantic schemas for Vitals API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VitalsBase(BaseModel):
    """Base Vitals schema with common fields."""

    blood_pressure_systolic: Optional[int] = Field(
        None,
        ge=50,
        le=250,
        description="Systolic blood pressure (mmHg)"
    )
    blood_pressure_diastolic: Optional[int] = Field(
        None,
        ge=30,
        le=150,
        description="Diastolic blood pressure (mmHg)"
    )
    heart_rate: Optional[int] = Field(
        None,
        ge=30,
        le=220,
        description="Heart rate (bpm)"
    )
    blood_sugar: Optional[float] = Field(
        None,
        ge=0,
        le=600,
        description="Blood sugar level (mg/dL)"
    )
    temperature: Optional[float] = Field(
        None,
        ge=30,
        le=45,
        description="Body temperature (Celsius)"
    )
    weight_kg: Optional[float] = Field(
        None,
        ge=0,
        description="Weight in kilograms"
    )
    logged_at: Optional[datetime] = Field(None, description="Timestamp when vitals were recorded")


class VitalsCreate(VitalsBase):
    """Schema for creating a new vitals entry."""

    related_to: list[str] = Field(
        default_factory=list,
        description="IDs of related events to link this vitals reading to"
    )


class VitalsUpdate(VitalsBase):
    """Schema for updating an existing vitals entry."""

    pass


class VitalsResponse(VitalsBase):
    """Schema for vitals response."""

    id: str = Field(..., description="Vitals entry ID")
    user_id: str = Field(..., description="User ID who recorded vitals")
    logged_at: datetime = Field(..., description="Timestamp when vitals were recorded")
    created_at: datetime = Field(..., description="Timestamp when entry was created")
