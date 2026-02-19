from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.auth.dependencies import get_current_user
from src.schemas.health import FoodLogEventDefinition, FoodLogCreate, FoodLogResponse, VitalsCreate, VitalsEventDefinition, VitalsResponse
from src.services.locusgraph_service import locusgraph_service

router = APIRouter(
    prefix="/health", tags=["health"], dependencies=[Depends(get_current_user)]
)


@router.get("/food/logs", response_model=list[FoodLogResponse])
async def get_food_logs(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    meal_type: Optional[str] = Query(None, description="Filter by meal type"),
    date: Optional[date] = Query(
        None, description="Filter by specific date (YYYY-MM-DD)"
    ),
    current_user=Depends(get_current_user),
):
    """Get food logs for the current user."""
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
                logged_at = datetime.fromisoformat(payload.get("logged_at", ""))
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
                    logged_at=datetime.fromisoformat(payload.get("logged_at", "")),
                    created_at=datetime.fromisoformat(memory.get("timestamp", "")),
                )
            )

    return food_logs


@router.post("/food/log", response_model=FoodLogResponse)
async def create_food_log(
    food_log_data: FoodLogCreate,
    related_to: Optional[str] = Query(
        None, description="Related event ID (e.g., vitals or medication)"
    ),
    current_user=Depends(get_current_user),
):
    """Log a food item or meal. Can be linked to other health events via related_to."""
    from src.schemas.events import EventKind

    food_log_id = locusgraph_service.new_id()
    context_id = FoodLogEventDefinition.get_context_id(food_log_id)

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


@router.get("/vitals", response_model=list[VitalsResponse])
async def get_vitals(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    date_from: Optional[date] = Query(
        None, description="Filter from date (YYYY-MM-DD)"
    ),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    current_user=Depends(get_current_user),
):
    """Get vitals history for the current user with optional date range filtering."""

    query_parts = [f"vitals user {current_user.id}"]
    if date_from:
        query_parts.append(f"from {date_from.isoformat()}")
    if date_to:
        query_parts.append(f"to {date_to.isoformat()}")

    query = " ".join(query_parts)
    print(f"DEBUG [HEALTH]: Querying vitals with: '{query}'")
    print(f"DEBUG [HEALTH]: Current user ID: {current_user.id}")

    memories = await locusgraph_service.retrieve_context(
        query=query,
        limit=limit,
    )
    print(f"DEBUG [HEALTH]: Retrieved {len(memories)} memories")

    vitals_entries = []
    for memory in memories:
        payload = memory.get("payload", {})
        print(f"DEBUG [HEALTH]: Memory payload user_id: {payload.get('user_id')}")
        if payload.get("user_id") == str(current_user.id):
            logged_at = datetime.fromisoformat(payload.get("logged_at", ""))

            # Filter by date range if specified
            if date_from and logged_at.date() < date_from:
                continue
            if date_to and logged_at.date() > date_to:
                continue

            vitals_entries.append(
                VitalsResponse(
                    id=memory.get("id", ""),
                    user_id=payload.get("user_id", ""),
                    blood_pressure_systolic=payload.get("blood_pressure_systolic"),
                    blood_pressure_diastolic=payload.get("blood_pressure_diastolic"),
                    heart_rate=payload.get("heart_rate"),
                    blood_sugar=payload.get("blood_sugar"),
                    temperature=payload.get("temperature"),
                    weight_kg=payload.get("weight_kg"),
                    logged_at=logged_at,
                    created_at=datetime.fromisoformat(memory.get("timestamp", "")),
                )
            )
        else:
            print(f"DEBUG [HEALTH]: Skipping memory - user_id mismatch")

    print(f"DEBUG [HEALTH]: Returning {len(vitals_entries)} vitals entries")
    return vitals_entries


@router.post("/vitals", response_model=VitalsResponse)
async def create_vitals(
    vitals_data: VitalsCreate,
    related_to: Optional[str] = Query(
        None, description="Related event ID (e.g., medication log)"
    ),
    current_user=Depends(get_current_user),
):
    """Log a vitals reading. Can be linked to medication logs or other events via related_to."""
    from src.schemas.events import EventKind

    vitals_id = locusgraph_service.new_id()
    context_id = VitalsEventDefinition.get_context_id(vitals_id)

    logged_at = vitals_data.logged_at or datetime.now(timezone.utc)

    payload = VitalsEventDefinition.create_payload(
        blood_pressure_systolic=vitals_data.blood_pressure_systolic,
        blood_pressure_diastolic=vitals_data.blood_pressure_diastolic,
        heart_rate=vitals_data.heart_rate,
        blood_sugar=vitals_data.blood_sugar,
        temperature=vitals_data.temperature,
        weight_kg=vitals_data.weight_kg,
        logged_at=logged_at,
        user_id=str(current_user.id),
    )

    print(f"DEBUG [HEALTH]: Storing vitals for user {current_user.id} with context_id={context_id}")
    print(f"DEBUG [HEALTH]: Payload: {payload}")

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.VITALS_CREATE,
        context_id=context_id,
        payload=payload,
        related_to=[related_to] if related_to else None,
    )

    return VitalsResponse(
        id=vitals_id,
        user_id=str(current_user.id),
        blood_pressure_systolic=vitals_data.blood_pressure_systolic,
        blood_pressure_diastolic=vitals_data.blood_pressure_diastolic,
        heart_rate=vitals_data.heart_rate,
        blood_sugar=vitals_data.blood_sugar,
        temperature=vitals_data.temperature,
        weight_kg=vitals_data.weight_kg,
        logged_at=logged_at,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/recommendations")
async def get_recommendations():
    return {"message": "not implemented"}


@router.get("/insights")
async def get_insights():
    return {"message": "not implemented"}
