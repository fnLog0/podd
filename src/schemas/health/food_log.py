"""Pydantic schemas for FoodLog API requests and responses."""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class FoodLogBase(BaseModel):
    """Base FoodLog schema with common fields."""

    description: str = Field(..., description="Food item or meal description")
    calories: Optional[float] = Field(
        None, ge=0, description="Calories in the food item"
    )
    protein_g: Optional[float] = Field(None, ge=0, description="Protein in grams")
    carbs_g: Optional[float] = Field(None, ge=0, description="Carbohydrates in grams")
    fat_g: Optional[float] = Field(None, ge=0, description="Fat in grams")
    meal_type: Literal["breakfast", "lunch", "dinner", "snack", "other"] = Field(
        ..., description="Type of meal (breakfast, lunch, dinner, snack, other)"
    )
    logged_at: Optional[datetime] = Field(
        None, description="Timestamp when food was logged"
    )


class FoodLogCreate(FoodLogBase):
    """Schema for creating a new food log entry."""

    related_to: list[str] = Field(
        default_factory=list, description="IDs of related events to link this log to"
    )


class FoodLogUpdate(FoodLogBase):
    """Schema for updating an existing food log entry."""

    description: Optional[str] = None
    meal_type: Optional[str] = None


class FoodLogResponse(FoodLogBase):
    """Schema for food log response."""

    id: str = Field(..., description="Food log entry ID")
    user_id: str = Field(..., description="User ID who logged the food")
    logged_at: datetime = Field(..., description="Timestamp when food was logged")
    created_at: datetime = Field(..., description="Timestamp when entry was created")
