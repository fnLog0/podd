"""Pydantic schemas for WaterLog API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WaterLogCreate(BaseModel):
    """Schema for creating a new water log entry."""

    amount_ml: float = Field(..., ge=0, description="Amount of water in milliliters")
    logged_at: Optional[datetime] = Field(
        None, description="Timestamp when water was logged"
    )


class WaterLogResponse(BaseModel):
    """Schema for water log response."""

    id: str = Field(..., description="Water log entry ID")
    user_id: str = Field(..., description="User ID who logged the water")
    amount_ml: float = Field(..., description="Amount of water in milliliters")
    logged_at: datetime = Field(..., description="Timestamp when water was logged")
    created_at: datetime = Field(..., description="Timestamp when entry was created")
