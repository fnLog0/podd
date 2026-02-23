"""Routes for Appointments CRUD operations."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_current_user
from src.schemas.appointments import (
    AppointmentCreate,
    AppointmentEventDefinition,
    AppointmentResponse,
    AppointmentUpdate,
)
from src.schemas.events import EventKind
from src.services.locusgraph.service import locusgraph_service
from src.services.temporal.scheduler import TemporalScheduler, get_temporal_contexts
from src.services.validation.duplicate import AppointmentDuplicateDetector
from src.services.batch.operations import BatchAppointmentCreator
from src.services.locusgraph.cache import AppointmentCache

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[AppointmentResponse])
async def get_appointments(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    query_type: Optional[str] = Query(
        None, description="Query type: 'upcoming' or 'past'"
    ),
    use_cache: bool = Query(True, description="Use cached data if available"),
    current_user=Depends(get_current_user),
):
    """List appointments (query: upcoming, past). Uses LocusGraph temporal queries."""
    # Try cache first
    if use_cache:
        cached = await AppointmentCache.get_appointments(
            str(current_user.id), query_type
        )
        if cached:
            return [AppointmentResponse(**apt) for apt in cached]

    # Use temporal query from LocusGraph
    if query_type in ("upcoming", "past"):
        memories = await get_temporal_contexts(
            user_id=str(current_user.id),
            temporal_type=query_type,
            limit=limit,
        )
    else:
        memories = await locusgraph_service.retrieve_context(
            query=f"appointments user {current_user.id}",
            limit=limit,
        )

    appointments = []
    now = datetime.now(timezone.utc)

    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            scheduled_at = payload.get("scheduled_at")
            if isinstance(scheduled_at, str):
                scheduled_at = datetime.fromisoformat(scheduled_at)

            # Apply temporal filter if using non-temporal query
            if query_type == "upcoming" and scheduled_at < now:
                continue
            if query_type == "past" and scheduled_at >= now:
                continue

            appointment_data = {
                "id": memory.get("id", ""),
                "user_id": payload.get("user_id", ""),
                "title": payload.get("title", ""),
                "doctor_name": payload.get("doctor_name"),
                "location": payload.get("location"),
                "scheduled_at": scheduled_at,
                "notes": payload.get("notes"),
                "reminder_minutes_before": payload.get("reminder_minutes_before"),
                "created_at": datetime.fromisoformat(memory.get("timestamp", "")),
                "updated_at": datetime.fromisoformat(memory.get("timestamp", "")),
            }
            appointments.append(appointment_data)

    # Sort by scheduled_at
    if query_type == "past":
        appointments.sort(key=lambda x: x["scheduled_at"], reverse=True)
    else:
        # Default: upcoming first
        appointments.sort(key=lambda x: x["scheduled_at"])

    # Cache the results
    if use_cache:
        await AppointmentCache.set_appointments(
            str(current_user.id), appointments, query_type
        )

    return [AppointmentResponse(**apt) for apt in appointments]


@router.post(
    "", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_appointment(
    appointment_data: AppointmentCreate, current_user=Depends(get_current_user)
):
    """Create a new appointment with duplicate detection and reminder scheduling."""
    # Check for duplicates
    duplicate = await AppointmentDuplicateDetector.detect_duplicates(
        title=appointment_data.title,
        scheduled_at=appointment_data.scheduled_at,
        doctor_name=appointment_data.doctor_name,
        location=appointment_data.location,
        user_id=str(current_user.id),
        time_window_minutes=30,
    )

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Similar appointment already exists at the same time",
        )

    appointment_id = locusgraph_service.new_id()
    context_id = AppointmentEventDefinition.get_context_id(appointment_id)

    # Enrich payload with temporal metadata
    base_payload = {
        "title": appointment_data.title,
        "doctor_name": appointment_data.doctor_name,
        "location": appointment_data.location,
        "scheduled_at": (
            appointment_data.scheduled_at.isoformat()
            if hasattr(appointment_data.scheduled_at, "isoformat")
            else appointment_data.scheduled_at
        ),
        "notes": appointment_data.notes,
        "reminder_minutes_before": appointment_data.reminder_minutes_before,
        "user_id": str(current_user.id),
    }

    payload = AppointmentEventDefinition.create_payload(
        title=base_payload["title"],
        doctor_name=base_payload["doctor_name"],
        location=base_payload["location"],
        scheduled_at=(
            datetime.fromisoformat(base_payload["scheduled_at"])
            if isinstance(base_payload["scheduled_at"], str)
            else base_payload["scheduled_at"]
        ),
        notes=base_payload["notes"],
        reminder_minutes_before=base_payload["reminder_minutes_before"],
        user_id=base_payload["user_id"],
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.APPOINTMENT_CREATE,
        context_id=context_id,
        payload=payload,
    )

    # Schedule reminder if specified
    if appointment_data.reminder_minutes_before:
        scheduled_at = (
            datetime.fromisoformat(base_payload["scheduled_at"])
            if isinstance(base_payload["scheduled_at"], str)
            else base_payload["scheduled_at"]
        )
        await TemporalScheduler.schedule_reminder(
            target_entity_type="appointment",
            target_entity_id=appointment_id,
            trigger_at=scheduled_at,
            reminder_minutes_before=appointment_data.reminder_minutes_before,
            user_id=str(current_user.id),
            title=f"Appointment: {appointment_data.title}",
            message=f"You have an appointment with {appointment_data.doctor_name or 'doctor'} at {scheduled_at.strftime('%I:%M %p')}",
        )

    # Invalidate cache for this user
    await AppointmentCache.invalidate_user_appointments(str(current_user.id))

    now = datetime.now(timezone.utc)
    return AppointmentResponse(
        id=stored.get("event_id", appointment_id),
        user_id=str(current_user.id),
        title=appointment_data.title,
        doctor_name=appointment_data.doctor_name,
        location=appointment_data.location,
        scheduled_at=scheduled_at,
        notes=appointment_data.notes,
        reminder_minutes_before=appointment_data.reminder_minutes_before,
        created_at=now,
        updated_at=now,
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str, current_user=Depends(get_current_user)):
    """Retrieve a specific appointment."""
    context_id = AppointmentEventDefinition.get_context_id(appointment_id)
    memories = await locusgraph_service.retrieve_context(
        query=f"appointment {appointment_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    memory = memories[0]
    payload = memory.get("payload", {})

    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    scheduled_at = payload.get("scheduled_at")
    if isinstance(scheduled_at, str):
        scheduled_at = datetime.fromisoformat(scheduled_at)

    return AppointmentResponse(
        id=appointment_id,
        user_id=payload.get("user_id", ""),
        title=payload.get("title", ""),
        doctor_name=payload.get("doctor_name"),
        location=payload.get("location"),
        scheduled_at=scheduled_at,
        notes=payload.get("notes"),
        reminder_minutes_before=payload.get("reminder_minutes_before"),
        created_at=datetime.fromisoformat(memory.get("timestamp", "")),
        updated_at=datetime.fromisoformat(memory.get("timestamp", "")),
    )


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    appointment_data: AppointmentUpdate,
    current_user=Depends(get_current_user),
):
    """Update an existing appointment."""
    context_id = AppointmentEventDefinition.get_context_id(appointment_id)

    # Verify appointment exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"appointment {appointment_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Merge existing data with updates
    updated_payload = AppointmentEventDefinition.create_payload(
        title=appointment_data.title or payload.get("title"),
        doctor_name=appointment_data.doctor_name or payload.get("doctor_name"),
        location=appointment_data.location or payload.get("location"),
        scheduled_at=(
            appointment_data.scheduled_at
            if appointment_data.scheduled_at
            else payload.get("scheduled_at")
        ),
        notes=(
            appointment_data.notes
            if appointment_data.notes is not None
            else payload.get("notes")
        ),
        reminder_minutes_before=(
            appointment_data.reminder_minutes_before
            if appointment_data.reminder_minutes_before is not None
            else payload.get("reminder_minutes_before")
        ),
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.APPOINTMENT_UPDATE,
        context_id=context_id,
        payload=updated_payload,
    )

    scheduled_at = updated_payload.get("scheduled_at")
    if isinstance(scheduled_at, str):
        scheduled_at = datetime.fromisoformat(scheduled_at)

    return AppointmentResponse(
        id=appointment_id,
        user_id=str(current_user.id),
        title=updated_payload["title"],
        doctor_name=updated_payload.get("doctor_name"),
        location=updated_payload.get("location"),
        scheduled_at=scheduled_at,
        notes=updated_payload.get("notes"),
        reminder_minutes_before=updated_payload.get("reminder_minutes_before"),
        created_at=datetime.fromisoformat(memories[0].get("timestamp", "")),
        updated_at=datetime.now(timezone.utc),
    )


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: str, current_user=Depends(get_current_user)
):
    """Delete an appointment and cancel any reminders."""
    context_id = AppointmentEventDefinition.get_context_id(appointment_id)

    # Verify appointment exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"appointment {appointment_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Cancel any scheduled reminders
    await TemporalScheduler.cancel_reminder(
        f"{TemporalScheduler.REMINDER_CONTEXT_PREFIX}:{appointment_id}"
    )

    # Store deletion event
    await locusgraph_service.store_event(
        event_kind=EventKind.APPOINTMENT_DELETE,
        context_id=context_id,
        payload={
            "deleted": True,
            "appointment_id": appointment_id,
            "user_id": str(current_user.id),
        },
    )

    # Invalidate cache for this user
    await AppointmentCache.invalidate_user_appointments(str(current_user.id))

    return None


@router.post("/batch", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_appointments_batch(
    appointments: list[AppointmentCreate],
    current_user=Depends(get_current_user),
):
    """Create multiple appointments in a batch with duplicate checking and reminder scheduling."""
    # Convert Pydantic models to dicts
    appointments_data = [
        {
            "title": apt.title,
            "doctor_name": apt.doctor_name,
            "location": apt.location,
            "scheduled_at": (
                apt.scheduled_at.isoformat()
                if hasattr(apt.scheduled_at, "isoformat")
                else apt.scheduled_at
            ),
            "notes": apt.notes,
            "reminder_minutes_before": apt.reminder_minutes_before,
        }
        for apt in appointments
    ]

    result = await BatchAppointmentCreator.create_appointments(
        appointments=appointments_data,
        user_id=str(current_user.id),
        schedule_reminders=True,
    )

    # Invalidate cache for this user
    await AppointmentCache.invalidate_user_appointments(str(current_user.id))

    return result
