"""Routes for Meditation CRUD operations."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_current_user
from src.schemas.events import EventKind
from src.schemas.meditation import (
    MeditationLogCreate,
    MeditationLogEventDefinition,
    MeditationLogResponse,
    MeditationSessionCreate,
    MeditationSessionEventDefinition,
    MeditationSessionResponse,
)
from src.services.locusgraph.service import locusgraph_service
from src.services.validation.duplicate import MeditationSessionDuplicateDetector
from src.services.batch.operations import BatchMeditationSessionCreator
from src.services.validation.memory import URLValidator
from src.services.locusgraph.cache import MeditationSessionCache

router = APIRouter(
    prefix="/meditation", tags=["meditation"], dependencies=[Depends(get_current_user)]
)


@router.get("/sessions", response_model=list[MeditationSessionResponse])
async def get_sessions(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    category: Optional[str] = Query(
        None,
        description="Filter by category (e.g., 'mindfulness', 'breathing', 'sleep')",
    ),
    use_cache: bool = Query(True, description="Use cached data if available"),
    current_user=Depends(get_current_user),
):
    """List available meditation sessions (filterable by category) with caching."""
    # Try cache first
    if use_cache:
        cached = await MeditationSessionCache.get_sessions(category)
        if cached:
            return [MeditationSessionResponse(**session) for session in cached]

    # Fetch from LocusGraph
    query = "meditation sessions"
    if category:
        query += f" {category}"

    memories = await locusgraph_service.retrieve_context(
        query=query,
        limit=limit,
    )

    sessions = []
    for memory in memories:
        payload = memory.get("payload", {})
        # Filter by category if specified
        if category and payload.get("category") != category:
            continue

        # Extract session_id from context_id or use event_id
        session_id = memory.get("id")
        if not session_id:
            # Try to extract from context_id (format: "meditation_session:{session_id}")
            context_id = memory.get("context_id", "")
            if ":" in context_id:
                session_id = context_id.split(":")[-1]
            else:
                session_id = memory.get("event_id", "")

        sessions.append(
            {
                "id": session_id,
                "title": payload.get("title", ""),
                "description": payload.get("description"),
                "audio_url": payload.get("audio_url"),
                "duration_minutes": payload.get("duration_minutes", 0),
                "category": payload.get("category"),
                "created_at": datetime.fromisoformat(memory.get("timestamp", "")),
            }
        )

    # Cache the results
    if use_cache:
        await MeditationSessionCache.set_sessions(sessions, category)

    return [MeditationSessionResponse(**session) for session in sessions]


@router.get("/sessions/{session_id}", response_model=MeditationSessionResponse)
async def get_session(session_id: str, current_user=Depends(get_current_user)):
    """Get single session details."""
    context_id = MeditationSessionEventDefinition.get_context_id(session_id)
    memories = await locusgraph_service.retrieve_context(
        query=f"meditation session {session_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meditation session not found",
        )

    memory = memories[0]
    payload = memory.get("payload", {})

    return MeditationSessionResponse(
        id=session_id,
        title=payload.get("title", ""),
        description=payload.get("description"),
        audio_url=payload.get("audio_url"),
        duration_minutes=payload.get("duration_minutes", 0),
        category=payload.get("category"),
        created_at=datetime.fromisoformat(memory.get("timestamp", "")),
    )


@router.post(
    "/sessions",
    response_model=MeditationSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    session_data: MeditationSessionCreate, current_user=Depends(get_current_user)
):
    """Create a new meditation session with duplicate detection and URL validation."""
    # Validate audio URL if provided
    if session_data.audio_url:
        is_valid, error_msg = await URLValidator.validate(
            url=session_data.audio_url,
            user_id=str(current_user.id) if current_user else None,
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid audio URL: {error_msg}",
            )

    # Check for duplicate sessions
    duplicate = await MeditationSessionDuplicateDetector.detect_duplicate(
        title=session_data.title,
        category=session_data.category,
        limit=10,
    )

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A meditation session with this title already exists",
        )

    session_id = locusgraph_service.new_id()
    context_id = MeditationSessionEventDefinition.get_context_id(session_id)

    payload = MeditationSessionEventDefinition.create_payload(
        title=session_data.title,
        description=session_data.description,
        audio_url=session_data.audio_url,
        duration_minutes=session_data.duration_minutes,
        category=session_data.category,
    )

    await locusgraph_service.store_event(
        event_kind=EventKind.MEDITATION_SESSION_CREATE,
        context_id=context_id,
        payload=payload,
    )

    # Invalidate cache for this category
    await MeditationSessionCache.invalidate_sessions(session_data.category)

    # Remember successful URL validation
    if session_data.audio_url:
        await URLValidator.mark_success(
            url=session_data.audio_url,
            user_id=str(current_user.id) if current_user else None,
        )

    now = datetime.now(timezone.utc)
    return MeditationSessionResponse(
        id=session_id,
        title=session_data.title,
        description=session_data.description,
        audio_url=session_data.audio_url,
        duration_minutes=session_data.duration_minutes,
        category=session_data.category,
        created_at=now,
    )


@router.post(
    "/log", response_model=MeditationLogResponse, status_code=status.HTTP_201_CREATED
)
async def create_meditation_log(
    log_data: MeditationLogCreate, current_user=Depends(get_current_user)
):
    """Log a completed meditation."""
    log_id = locusgraph_service.new_id()
    context_id = MeditationLogEventDefinition.get_context_id(log_id)

    # Verify session exists
    session_context_id = MeditationSessionEventDefinition.get_context_id(
        log_data.session_id
    )
    session_memories = await locusgraph_service.retrieve_context(
        query=f"meditation session {log_data.session_id}",
        context_ids=[session_context_id],
        limit=1,
    )

    if not session_memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meditation session not found",
        )

    payload = MeditationLogEventDefinition.create_payload(
        session_id=log_data.session_id,
        duration_minutes=log_data.duration_minutes,
        completed=log_data.completed,
        logged_at=datetime.now(timezone.utc),
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.MEDITATION_LOG,
        context_id=context_id,
        payload=payload,
    )

    now = datetime.now(timezone.utc)
    return MeditationLogResponse(
        id=log_id,
        user_id=str(current_user.id),
        session_id=log_data.session_id,
        duration_minutes=log_data.duration_minutes,
        completed=log_data.completed,
        logged_at=now,
        created_at=now,
    )


@router.get("/history", response_model=list[MeditationLogResponse])
async def get_meditation_history(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    current_user=Depends(get_current_user),
):
    """Get meditation history for the current user."""
    memories = await locusgraph_service.retrieve_context(
        query=f"meditation logs user {current_user.id}",
        limit=limit,
    )

    history = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            logged_at = payload.get("logged_at")
            if isinstance(logged_at, str):
                logged_at = datetime.fromisoformat(logged_at)
            elif logged_at is None:
                logged_at = datetime.fromisoformat(memory.get("timestamp", ""))

            # Extract log_id from event_id
            log_id = memory.get("id") or memory.get("event_id", "")

            history.append(
                MeditationLogResponse(
                    id=log_id,
                    user_id=payload.get("user_id", ""),
                    session_id=payload.get("session_id", ""),
                    duration_minutes=payload.get("duration_minutes", 0),
                    completed=payload.get("completed", True),
                    logged_at=logged_at,
                    created_at=datetime.fromisoformat(memory.get("timestamp", "")),
                )
            )

    # Sort by logged_at descending (most recent first)
    history.sort(key=lambda x: x.logged_at, reverse=True)

    return history


@router.post(
    "/sessions/batch", response_model=dict, status_code=status.HTTP_201_CREATED
)
async def create_sessions_batch(
    sessions: list[MeditationSessionCreate],
    current_user=Depends(get_current_user),
):
    """Create multiple meditation sessions in a batch with duplicate checking."""
    # Convert Pydantic models to dicts
    sessions_data = [
        {
            "title": session.title,
            "description": session.description,
            "audio_url": session.audio_url,
            "duration_minutes": session.duration_minutes,
            "category": session.category,
        }
        for session in sessions
    ]

    result = await BatchMeditationSessionCreator.create_sessions(
        sessions=sessions_data,
    )

    # Invalidate all caches
    await MeditationSessionCache.invalidate_sessions()

    return result
