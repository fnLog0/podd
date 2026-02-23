from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.auth.dependencies import get_current_user
from src.schemas.events import EventKind
from src.schemas.events.tracking_events import (
    ExerciseLogEventDefinition,
    MoodLogEventDefinition,
    SleepLogEventDefinition,
    WaterLogEventDefinition,
)
from src.schemas.health import (
    ExerciseLogCreate,
    ExerciseLogResponse,
    MoodLogCreate,
    MoodLogResponse,
    SleepLogCreate,
    SleepLogResponse,
    WaterLogCreate,
    WaterLogResponse,
)
from src.services.locusgraph.service import locusgraph_service

router = APIRouter(
    prefix="/tracking", tags=["tracking"], dependencies=[Depends(get_current_user)]
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



# ==================== Water Tracking ====================


@router.post(
    "/water/log", response_model=WaterLogResponse, status_code=status.HTTP_201_CREATED
)
async def create_water_log(
    water_data: WaterLogCreate,
    current_user=Depends(get_current_user),
):
    """Log water intake."""
    water_log_id = locusgraph_service.new_id()
    context_id = WaterLogEventDefinition.get_context_id(water_log_id)

    logged_at = water_data.logged_at or datetime.now(timezone.utc)

    payload = WaterLogEventDefinition.create_payload(
        amount_ml=water_data.amount_ml,
        logged_at=logged_at,
        user_id=str(current_user.id),
    )

    await locusgraph_service.store_event(
        event_kind=EventKind.WATER_LOG_CREATE,
        context_id=context_id,
        payload=payload,
    )

    return WaterLogResponse(
        id=water_log_id,
        user_id=str(current_user.id),
        amount_ml=water_data.amount_ml,
        logged_at=logged_at,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/water/history", response_model=list[WaterLogResponse])
async def get_water_history(
    date: Optional[date] = Query(
        None, description="Filter by specific date (YYYY-MM-DD)"
    ),
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    current_user=Depends(get_current_user),
):
    """Get water logs history."""
    query_parts = ["water logs", f"user {current_user.id}"]
    if date:
        query_parts.append(f"date {date.isoformat()}")

    memories = await locusgraph_service.retrieve_context(
        query=" ".join(query_parts),
        limit=limit,
    )

    water_logs = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            logged_at = safe_parse_datetime(
                payload.get("logged_at"),
                memory.get("timestamp")
            )
            created_at = datetime.fromisoformat(memory.get("timestamp", ""))

            if date and logged_at.date() != date:
                continue

            water_logs.append(
                WaterLogResponse(
                    id=memory.get("id", ""),
                    user_id=payload.get("user_id", ""),
                    amount_ml=payload.get("amount_ml", 0),
                    logged_at=logged_at,
                    created_at=created_at,
                )
            )

    return water_logs


# ==================== Sleep Tracking ====================


@router.post(
    "/sleep/log", response_model=SleepLogResponse, status_code=status.HTTP_201_CREATED
)
async def create_sleep_log(
    sleep_data: SleepLogCreate,
    current_user=Depends(get_current_user),
):
    """Log a sleep session."""
    sleep_log_id = locusgraph_service.new_id()
    context_id = SleepLogEventDefinition.get_context_id(sleep_log_id)

    payload = SleepLogEventDefinition.create_payload(
        sleep_start=sleep_data.sleep_start,
        sleep_end=sleep_data.sleep_end,
        quality=sleep_data.quality,
        user_id=str(current_user.id),
        notes=sleep_data.notes,
    )

    await locusgraph_service.store_event(
        event_kind=EventKind.SLEEP_LOG_CREATE,
        context_id=context_id,
        payload=payload,
    )

    return SleepLogResponse(
        id=sleep_log_id,
        user_id=str(current_user.id),
        sleep_start=sleep_data.sleep_start,
        sleep_end=sleep_data.sleep_end,
        quality=sleep_data.quality,
        notes=sleep_data.notes,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/sleep/history", response_model=list[SleepLogResponse])
async def get_sleep_history(
    date_from: Optional[date] = Query(
        None, description="Filter by date from (YYYY-MM-DD)"
    ),
    date_to: Optional[date] = Query(None, description="Filter by date to (YYYY-MM-DD)"),
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    current_user=Depends(get_current_user),
):
    """Get sleep logs history."""
    query_parts = ["sleep logs", f"user {current_user.id}"]
    if date_from:
        query_parts.append(f"from {date_from.isoformat()}")
    if date_to:
        query_parts.append(f"to {date_to.isoformat()}")

    memories = await locusgraph_service.retrieve_context(
        query=" ".join(query_parts),
        limit=limit,
    )

    sleep_logs = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            try:
                sleep_start = datetime.fromisoformat(payload.get("sleep_start", ""))
                sleep_end = datetime.fromisoformat(payload.get("sleep_end", ""))
                created_at = datetime.fromisoformat(memory.get("timestamp", ""))
            except (ValueError, TypeError):
                continue

            if date_from and sleep_start.date() < date_from:
                continue
            if date_to and sleep_start.date() > date_to:
                continue

            sleep_logs.append(
                SleepLogResponse(
                    id=memory.get("id", ""),
                    user_id=payload.get("user_id", ""),
                    sleep_start=sleep_start,
                    sleep_end=sleep_end,
                    quality=payload.get("quality", "good"),
                    notes=payload.get("notes"),
                    created_at=created_at,
                )
            )

    return sleep_logs


# ==================== Exercise Tracking ====================


@router.post(
    "/exercise/log",
    response_model=ExerciseLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_exercise_log(
    exercise_data: ExerciseLogCreate,
    current_user=Depends(get_current_user),
):
    """Log an exercise session."""
    exercise_log_id = locusgraph_service.new_id()
    context_id = ExerciseLogEventDefinition.get_context_id(exercise_log_id)

    logged_at = exercise_data.logged_at or datetime.now(timezone.utc)

    payload = ExerciseLogEventDefinition.create_payload(
        exercise_type=exercise_data.exercise_type,
        duration_minutes=exercise_data.duration_minutes,
        intensity=exercise_data.intensity,
        logged_at=logged_at,
        user_id=str(current_user.id),
        calories_burned=exercise_data.calories_burned,
    )

    await locusgraph_service.store_event(
        event_kind=EventKind.EXERCISE_LOG_CREATE,
        context_id=context_id,
        payload=payload,
    )

    return ExerciseLogResponse(
        id=exercise_log_id,
        user_id=str(current_user.id),
        exercise_type=exercise_data.exercise_type,
        duration_minutes=exercise_data.duration_minutes,
        calories_burned=exercise_data.calories_burned,
        intensity=exercise_data.intensity,
        logged_at=logged_at,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/exercise/history", response_model=list[ExerciseLogResponse])
async def get_exercise_history(
    date: Optional[date] = Query(
        None, description="Filter by specific date (YYYY-MM-DD)"
    ),
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    current_user=Depends(get_current_user),
):
    """Get exercise logs history."""
    query_parts = ["exercise logs", f"user {current_user.id}"]
    if date:
        query_parts.append(f"date {date.isoformat()}")

    memories = await locusgraph_service.retrieve_context(
        query=" ".join(query_parts),
        limit=limit,
    )

    exercise_logs = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            try:
                logged_at = datetime.fromisoformat(payload.get("logged_at", ""))
                created_at = datetime.fromisoformat(memory.get("timestamp", ""))
            except (ValueError, TypeError):
                continue

            if date and logged_at.date() != date:
                continue

            exercise_logs.append(
                ExerciseLogResponse(
                    id=memory.get("id", ""),
                    user_id=payload.get("user_id", ""),
                    exercise_type=payload.get("exercise_type", ""),
                    duration_minutes=payload.get("duration_minutes", 0),
                    calories_burned=payload.get("calories_burned"),
                    intensity=payload.get("intensity", "moderate"),
                    logged_at=logged_at,
                    created_at=created_at,
                )
            )

    return exercise_logs


# ==================== Mood Tracking ====================


@router.post(
    "/mood/log", response_model=MoodLogResponse, status_code=status.HTTP_201_CREATED
)
async def create_mood_log(
    mood_data: MoodLogCreate,
    current_user=Depends(get_current_user),
):
    """Log a mood entry."""
    mood_log_id = locusgraph_service.new_id()
    context_id = MoodLogEventDefinition.get_context_id(mood_log_id)

    logged_at = mood_data.logged_at or datetime.now(timezone.utc)

    payload = MoodLogEventDefinition.create_payload(
        mood=mood_data.mood,
        energy_level=mood_data.energy_level,
        logged_at=logged_at,
        user_id=str(current_user.id),
        notes=mood_data.notes,
    )

    await locusgraph_service.store_event(
        event_kind=EventKind.MOOD_LOG_CREATE,
        context_id=context_id,
        payload=payload,
    )

    return MoodLogResponse(
        id=mood_log_id,
        user_id=str(current_user.id),
        mood=mood_data.mood,
        energy_level=mood_data.energy_level,
        notes=mood_data.notes,
        logged_at=logged_at,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/mood/history", response_model=list[MoodLogResponse])
async def get_mood_history(
    date_from: Optional[date] = Query(
        None, description="Filter by date from (YYYY-MM-DD)"
    ),
    date_to: Optional[date] = Query(None, description="Filter by date to (YYYY-MM-DD)"),
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    current_user=Depends(get_current_user),
):
    """Get mood logs history."""
    query_parts = ["mood logs", f"user {current_user.id}"]
    if date_from:
        query_parts.append(f"from {date_from.isoformat()}")
    if date_to:
        query_parts.append(f"to {date_to.isoformat()}")

    memories = await locusgraph_service.retrieve_context(
        query=" ".join(query_parts),
        limit=limit,
    )

    mood_logs = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            try:
                logged_at = datetime.fromisoformat(payload.get("logged_at", ""))
                created_at = datetime.fromisoformat(memory.get("timestamp", ""))
            except (ValueError, TypeError):
                continue

            if date_from and logged_at.date() < date_from:
                continue
            if date_to and logged_at.date() > date_to:
                continue

            mood_logs.append(
                MoodLogResponse(
                    id=memory.get("id", ""),
                    user_id=payload.get("user_id", ""),
                    mood=payload.get("mood", "neutral"),
                    energy_level=payload.get("energy_level", "medium"),
                    notes=payload.get("notes"),
                    logged_at=logged_at,
                    created_at=created_at,
                )
            )

    return mood_logs
