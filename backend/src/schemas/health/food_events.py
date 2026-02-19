"""FoodLog event schemas for LocusGraph.

This module defines the payload and event definition for FoodLog events.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.schemas.events.locusgraph_events import ContextIdPattern, EventKind


# ==================== FoodLog Events ====================


class FoodLogEventPayload(BaseModel):
    """Payload for FoodLog events stored in LocusGraph."""

    description: str = Field(..., description="Food item or meal description")
    calories: Optional[float] = Field(
        None, ge=0, description="Calories in food item"
    )
    protein_g: Optional[float] = Field(None, ge=0, description="Protein in grams")
    carbs_g: Optional[float] = Field(None, ge=0, description="Carbohydrates in grams")
    fat_g: Optional[float] = Field(None, ge=0, description="Fat in grams")
    meal_type: Literal["breakfast", "lunch", "dinner", "snack", "other"] = Field(
        ..., description="Type of meal"
    )
    logged_at: datetime = Field(..., description="Timestamp when food was logged")
    user_id: str = Field(..., description="User ID who logged the food")


# ==================== FoodLog Event Definition ====================


class FoodLogEventDefinition:
    """Definition and metadata for FoodLog events in LocusGraph."""

    EVENT_KIND = EventKind.FOOD_LOG_CREATE
    CONTEXT_PATTERN = ContextIdPattern.FOOD_LOG
    PAYLOAD_MODEL = FoodLogEventPayload

    @staticmethod
    def get_context_id(food_log_id: str) -> str:
        """Generate context ID for a food log entry.

        Args:
            food_log_id: The food log entry's unique identifier

        Returns:
            Context ID in format: food:<food_log_id>
        """
        return ContextIdPattern.FOOD_LOG.format(id=food_log_id)

    @staticmethod
    def create_payload(
        description: str,
        meal_type: str,
        logged_at: datetime,
        user_id: str,
        calories: Optional[float] = None,
        protein_g: Optional[float] = None,
        carbs_g: Optional[float] = None,
        fat_g: Optional[float] = None,
    ) -> dict:
        """Create a FoodLog event payload.

        Args:
            description: Food item or meal description
            meal_type: Type of meal (breakfast, lunch, dinner, snack, other)
            logged_at: Timestamp when food was logged
            user_id: User ID who logged the food
            calories: Calories in food item
            protein_g: Protein in grams
            carbs_g: Carbohydrates in grams
            fat_g: Fat in grams

        Returns:
            Dictionary containing the food log data
        """
        payload = FoodLogEventPayload(
            description=description,
            calories=calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            meal_type=meal_type,
            logged_at=logged_at,
            user_id=user_id,
        )
        return payload.model_dump(mode="json")
