from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ProfileBase(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = Field(None, ge=0, description="Height in centimeters")
    weight_kg: Optional[float] = Field(None, ge=0, description="Weight in kilograms")
    blood_type: Optional[str] = Field(None, pattern=r'^[ABO][+-]$', description="Blood type (A+, A-, B+, B-, O+, O-, AB+, AB-)")
    allergies: Optional[list[str]] = Field(default_factory=list, description="List of known allergies")
    medical_conditions: Optional[list[str]] = Field(default_factory=list, description="List of medical conditions")
    dietary_preferences: Optional[list[str]] = Field(default_factory=list, description="Dietary preferences (e.g., vegetarian, vegan, gluten-free)")


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    user_id: str
    updated_at: str
