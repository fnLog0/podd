"""Routes for FoodLog CRUD operations."""

from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_current_user
from src.schemas.events import EventKind
from src.schemas.health import (
    FoodLogEventDefinition,
    FoodLogCreate,
    FoodLogResponse,
    FoodLogUpdate,
)
from src.services.locusgraph.service import locusgraph_service

router = APIRouter(
    prefix="/food-logs", tags=["food-logs"], dependencies=[Depends(get_current_user)]
)


def safe_parse_datetime(timestamp_str: str | None, fallback_timestamp: str | None = None) -> datetime:
    """Safely parse ISO format datetime string with fallback options."""
    if timestamp_str:
        try:
            return datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            pass

    if fallback_timestamp:
        try:
            return datetime.fromisoformat(fallback_timestamp)
        except (ValueError, TypeError):
            pass

    return datetime.now(timezone.utc)



@router.get("", response_model=list[FoodLogResponse])
async def get_food_logs(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
    date: Optional[date] = Query(
        None, description="Filter by specific date (YYYY-MM-DD)"
    ),
    current_user=Depends(get_current_user),
):
    """Retrieve all food logs for the current user with optional date filtering."""
    query_parts = ["food logs", f"user {current_user.id}"]
    if meal_type:
        query_parts.append(f"meal type {meal_type}")
    if date:
        query_parts.append(f"date {date.isoformat()}")

    memories = await locusgraph_service.retrieve_context(
        query=" ".join(query_parts),
        limit=limit,
    )

    food_logs = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            if meal_type and payload.get("meal_type") != meal_type:
                continue

            # Filter by date if specified
            if date:
                logged_at = safe_parse_datetime(
                    payload.get("logged_at"),
                    memory.get("timestamp")
                )
                if logged_at.date() != date:
                    continue

            food_logs.append(
                FoodLogResponse(
                    id=memory.get("id", ""),
                    user_id=payload.get("user_id", ""),
                    description=payload.get("description", ""),
                    calories=payload.get("calories"),
                    protein_g=payload.get("protein_g"),
                    carbs_g=payload.get("carbs_g"),
                    fat_g=payload.get("fat_g"),
                    meal_type=payload.get("meal_type", ""),
                    logged_at=safe_parse_datetime(
                        payload.get("logged_at"),
                        memory.get("timestamp")
                    ),
                    created_at=datetime.fromisoformat(memory.get("timestamp", "")),
                )
            )

    return food_logs


@router.get("/{food_log_id}", response_model=FoodLogResponse)
async def get_food_log(food_log_id: str, current_user=Depends(get_current_user)):
    """Retrieve a specific food log entry."""
    context_id = FoodLogEventDefinition.get_context_id(food_log_id)
    memories = await locusgraph_service.retrieve_context(
        query=f"food log {food_log_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log entry not found",
        )

    memory = memories[0]
    payload = memory.get("payload", {})

    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return FoodLogResponse(
        id=memory.get("id", ""),
        user_id=payload.get("user_id", ""),
        description=payload.get("description", ""),
        calories=payload.get("calories"),
        protein_g=payload.get("protein_g"),
        carbs_g=payload.get("carbs_g"),
        fat_g=payload.get("fat_g"),
        meal_type=payload.get("meal_type", ""),
        logged_at=datetime.fromisoformat(payload.get("logged_at", "")),
        created_at=datetime.fromisoformat(memory.get("timestamp", "")),
    )


@router.post("", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def create_food_log(
    food_log_data: FoodLogCreate,
    related_to: Optional[str] = Query(
        None, description="Related event ID (e.g., vitals or medication)"
    ),
    current_user=Depends(get_current_user),
):
    """Create a new food log entry. Can be linked to other health events via related_to."""
    food_log_id = locusgraph_service.new_id()
    context_id = FoodLogEventDefinition.get_context_id(food_log_id)

    # Set logged_at to current time if not provided
    logged_at = food_log_data.logged_at or datetime.now(timezone.utc)

    payload = FoodLogEventDefinition.create_payload(
        description=food_log_data.description,
        calories=food_log_data.calories,
        protein_g=food_log_data.protein_g,
        carbs_g=food_log_data.carbs_g,
        fat_g=food_log_data.fat_g,
        meal_type=food_log_data.meal_type,
        logged_at=logged_at,
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.FOOD_LOG_CREATE,
        context_id=context_id,
        payload=payload,
        related_to=[related_to] if related_to else None,
    )

    return FoodLogResponse(
        id=food_log_id,
        user_id=str(current_user.id),
        description=food_log_data.description,
        calories=food_log_data.calories,
        protein_g=food_log_data.protein_g,
        carbs_g=food_log_data.carbs_g,
        fat_g=food_log_data.fat_g,
        meal_type=food_log_data.meal_type,
        logged_at=logged_at,
        created_at=datetime.now(timezone.utc),
    )


@router.put("/{food_log_id}", response_model=FoodLogResponse)
async def update_food_log(
    food_log_id: str,
    food_log_data: FoodLogUpdate,
    current_user=Depends(get_current_user),
):
    """Update an existing food log entry."""
    context_id = FoodLogEventDefinition.get_context_id(food_log_id)

    # Verify food log exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"food log {food_log_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log entry not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Merge existing data with updates
    updated_payload = FoodLogEventDefinition.create_payload(
        description=food_log_data.description or payload.get("description"),
        calories=(
            food_log_data.calories
            if food_log_data.calories is not None
            else payload.get("calories")
        ),
        protein_g=(
            food_log_data.protein_g
            if food_log_data.protein_g is not None
            else payload.get("protein_g")
        ),
        carbs_g=(
            food_log_data.carbs_g
            if food_log_data.carbs_g is not None
            else payload.get("carbs_g")
        ),
        fat_g=(
            food_log_data.fat_g
            if food_log_data.fat_g is not None
            else payload.get("fat_g")
        ),
        meal_type=food_log_data.meal_type or payload.get("meal_type"),
        logged_at=datetime.fromisoformat(payload.get("logged_at")),
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.FOOD_LOG_UPDATE,
        context_id=context_id,
        payload=updated_payload,
    )

    return FoodLogResponse(
        id=food_log_id,
        user_id=str(current_user.id),
        description=updated_payload["description"],
        calories=updated_payload.get("calories"),
        protein_g=updated_payload.get("protein_g"),
        carbs_g=updated_payload.get("carbs_g"),
        fat_g=updated_payload.get("fat_g"),
        meal_type=updated_payload["meal_type"],
        logged_at=datetime.fromisoformat(updated_payload["logged_at"]),
        created_at=datetime.fromisoformat(memories[0].get("timestamp", "")),
    )


@router.delete("/{food_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food_log(food_log_id: str, current_user=Depends(get_current_user)):
    """Delete a food log entry."""
    context_id = FoodLogEventDefinition.get_context_id(food_log_id)

    # Verify food log exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"food log {food_log_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food log entry not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Store deletion event
    await locusgraph_service.store_event(
        event_kind=EventKind.FOOD_LOG_DELETE,
        context_id=context_id,
        payload={
            "deleted": True,
            "food_log_id": food_log_id,
            "user_id": str(current_user.id),
        },
    )

    return None
