"""Routes for Medication CRUD operations."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_current_user
from src.schemas.events import EventKind
from src.schemas.medication import (
    MedicationCreate,
    MedicationEventDefinition,
    MedicationResponse,
    MedicationScheduleCreate,
    MedicationScheduleResponse,
    MedicationUpdate,
)
from src.services.locusgraph_service import locusgraph_service

router = APIRouter(
    prefix="/medication", tags=["medication"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[MedicationResponse])
async def get_medications(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    active_only: bool = Query(False, description="Filter to active medications only"),
    current_user=Depends(get_current_user),
):
    """Retrieve all medications for the current user."""
    memories = await locusgraph_service.retrieve_context(
        query=f"medications user {current_user.id}",
        limit=limit,
    )

    medications = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            if active_only and not payload.get("active", True):
                continue

            medications.append(
                MedicationResponse(
                    id=memory.get("id", ""),
                    user_id=payload.get("user_id", ""),
                    name=payload.get("name", ""),
                    dosage=payload.get("dosage", ""),
                    frequency=payload.get("frequency", ""),
                    instructions=payload.get("instructions"),
                    active=payload.get("active", True),
                    created_at=datetime.fromisoformat(memory.get("timestamp", "")),
                    updated_at=datetime.fromisoformat(memory.get("timestamp", "")),
                )
            )

    return medications


@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication(medication_id: str, current_user=Depends(get_current_user)):
    """Retrieve a specific medication."""
    context_id = MedicationEventDefinition.get_context_id(medication_id)
    memories = await locusgraph_service.retrieve_context(
        query=f"medication {medication_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found",
        )

    memory = memories[0]
    payload = memory.get("payload", {})

    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return MedicationResponse(
        id=memory.get("id", ""),
        user_id=payload.get("user_id", ""),
        name=payload.get("name", ""),
        dosage=payload.get("dosage", ""),
        frequency=payload.get("frequency", ""),
        instructions=payload.get("instructions"),
        active=payload.get("active", True),
        created_at=datetime.fromisoformat(memory.get("timestamp", "")),
        updated_at=datetime.fromisoformat(memory.get("timestamp", "")),
    )


@router.post("", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
async def create_medication(
    medication_data: MedicationCreate, current_user=Depends(get_current_user)
):
    """Create a new medication."""
    medication_id = locusgraph_service.new_id()
    context_id = MedicationEventDefinition.get_context_id(medication_id)

    payload = MedicationEventDefinition.create_payload(
        name=medication_data.name,
        dosage=medication_data.dosage,
        frequency=medication_data.frequency,
        instructions=medication_data.instructions,
        active=medication_data.active,
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.MEDICATION_CREATE,
        context_id=context_id,
        payload=payload,
    )

    now = datetime.now(timezone.utc)
    return MedicationResponse(
        id=medication_id,
        user_id=str(current_user.id),
        name=medication_data.name,
        dosage=medication_data.dosage,
        frequency=medication_data.frequency,
        instructions=medication_data.instructions,
        active=medication_data.active,
        created_at=now,
        updated_at=now,
    )


@router.put("/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: str,
    medication_data: MedicationUpdate,
    current_user=Depends(get_current_user),
):
    """Update an existing medication."""
    context_id = MedicationEventDefinition.get_context_id(medication_id)

    # Verify medication exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"medication {medication_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Merge existing data with updates
    updated_payload = MedicationEventDefinition.create_payload(
        name=medication_data.name or payload.get("name"),
        dosage=medication_data.dosage or payload.get("dosage"),
        frequency=medication_data.frequency or payload.get("frequency"),
        instructions=medication_data.instructions
        if medication_data.instructions is not None
        else payload.get("instructions"),
        active=medication_data.active
        if medication_data.active is not None
        else payload.get("active", True),
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.MEDICATION_UPDATE,
        context_id=context_id,
        payload=updated_payload,
    )

    return MedicationResponse(
        id=medication_id,
        user_id=str(current_user.id),
        name=updated_payload["name"],
        dosage=updated_payload["dosage"],
        frequency=updated_payload["frequency"],
        instructions=updated_payload.get("instructions"),
        active=updated_payload["active"],
        created_at=datetime.fromisoformat(memories[0].get("timestamp", "")),
        updated_at=datetime.now(timezone.utc),
    )


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication(medication_id: str, current_user=Depends(get_current_user)):
    """Delete a medication."""
    context_id = MedicationEventDefinition.get_context_id(medication_id)

    # Verify medication exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"medication {medication_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Store deletion event
    await locusgraph_service.store_event(
        event_kind=EventKind.MEDICATION_DELETE,
        context_id=context_id,
        payload={
            "deleted": True,
            "medication_id": medication_id,
            "user_id": str(current_user.id),
        },
    )

    return None


@router.post("/log", response_model=dict, status_code=status.HTTP_201_CREATED)
async def log_medication(
    log_data: dict,
    related_to: Optional[str] = Query(
        None, description="Related event ID (e.g., vitals reading ID)"
    ),
    current_user=Depends(get_current_user),
):
    """Log that a medication was taken. Can be linked to vitals readings via related_to."""
    from src.schemas.events import EventKind
    from src.schemas.medication import MedicationLogEventDefinition, MedicationLogCreate, MedicationLogResponse

    log_create = MedicationLogCreate(**log_data)
    log_id = locusgraph_service.new_id()
    context_id = MedicationLogEventDefinition.get_context_id(log_id)
    taken_at = log_create.taken_at or datetime.now(timezone.utc)

    # Look up medication_id if only medication_name is provided
    medication_id = log_create.medication_id
    if not medication_id and log_create.medication_name:
        memories = await locusgraph_service.retrieve_context(
            query=f"medication {log_create.medication_name} user {current_user.id}",
            limit=10,
        )
        for memory in memories:
            payload = memory.get("payload", {})
            if payload.get("user_id") == str(current_user.id) and payload.get("name") == log_create.medication_name:
                medication_id = payload.get("id", memory.get("id"))
                break
        if not medication_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medication '{log_create.medication_name}' not found. Please create the medication first.",
            )

    if not medication_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either medication_id or medication_name must be provided",
        )

    payload = MedicationLogEventDefinition.create_payload(
        medication_id=medication_id,
        taken_at=taken_at,
        user_id=str(current_user.id),
        scheduled_time=log_create.scheduled_time,
        notes=log_create.notes,
    )

    # Use related_to from query parameter or from the request body
    related_to_list = None
    if related_to:
        related_to_list = [related_to]
    elif hasattr(log_create, "related_to") and log_create.related_to:
        related_to_list = (
            [log_create.related_to]
            if isinstance(log_create.related_to, str)
            else log_create.related_to
        )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.MEDICATION_LOG,
        context_id=context_id,
        payload=payload,
        related_to=related_to_list,
    )

    # Try to fetch medication name if not already provided
    medication_name = log_create.medication_name
    if not medication_name and medication_id:
        try:
            med_context_id = MedicationEventDefinition.get_context_id(medication_id)
            med_memories = await locusgraph_service.retrieve_context(
                query=f"medication {medication_id}",
                context_ids=[med_context_id],
                limit=1,
            )
            if med_memories:
                medication_name = med_memories[0].get("payload", {}).get("name")
        except Exception:
            pass

    return MedicationLogResponse(
        id=stored.get("event_id", log_id),
        user_id=str(current_user.id),
        medication_id=medication_id,
        medication_name=medication_name,
        taken_at=taken_at,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/schedule", response_model=list[MedicationScheduleResponse])
async def get_medication_schedules(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    current_user=Depends(get_current_user),
):
    """Get all active medication schedules for the current user."""
    from src.schemas.medication import MedicationScheduleEventDefinition

    memories = await locusgraph_service.retrieve_context(
        query=f"medication schedules user {current_user.id}",
        limit=limit,
    )

    schedules = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            medication_name = None
            med_id = payload.get("medication_id")
            if med_id:
                try:
                    med_memories = await locusgraph_service.retrieve_context(
                        query=f"medication {med_id}",
                        context_ids=[f"medication:{med_id}"],
                        limit=1,
                    )
                    if med_memories:
                        medication_name = med_memories[0].get("payload", {}).get("name")
                except Exception:
                    pass

            schedules.append(
                MedicationScheduleResponse(
                    id=memory.get("id", ""),
                    user_id=payload.get("user_id", ""),
                    medication_id=payload.get("medication_id", ""),
                    medication_name=medication_name,
                    time_of_day=payload.get("time_of_day", ""),
                    days_of_week=payload.get("days_of_week", []),
                    created_at=datetime.fromisoformat(memory.get("timestamp", "")),
                    updated_at=datetime.fromisoformat(memory.get("timestamp", "")),
                )
            )

    return schedules


@router.post(
    "/schedule",
    response_model=MedicationScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_medication_schedule(
    schedule_data: MedicationScheduleCreate,
    related_to: Optional[str] = Query(
        None, description="Related event ID (e.g., medication ID)"
    ),
    current_user=Depends(get_current_user),
):
    """Add a new medication schedule. Can be linked to medication via related_to."""
    from src.schemas.medication import MedicationScheduleEventDefinition

    schedule_id = locusgraph_service.new_id()
    context_id = MedicationScheduleEventDefinition.get_context_id(schedule_id)

    payload = MedicationScheduleEventDefinition.create_payload(
        medication_id=schedule_data.medication_id,
        time_of_day=schedule_data.time_of_day,
        days_of_week=schedule_data.days_of_week,
        user_id=str(current_user.id),
    )

    # Use related_to from query parameter or from the request body
    related_to_list = None
    if related_to:
        related_to_list = [related_to]
    elif hasattr(schedule_data, "related_to") and schedule_data.related_to:
        related_to_list = (
            [schedule_data.related_to]
            if isinstance(schedule_data.related_to, str)
            else schedule_data.related_to
        )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.MEDICATION_SCHEDULE_CREATE,
        context_id=context_id,
        payload=payload,
        related_to=related_to_list,
    )

    now = datetime.now(timezone.utc)
    return MedicationScheduleResponse(
        id=stored.get("event_id", schedule_id),
        user_id=str(current_user.id),
        medication_id=schedule_data.medication_id,
        medication_name=None,
        time_of_day=schedule_data.time_of_day,
        days_of_week=schedule_data.days_of_week,
        created_at=now,
        updated_at=now,
    )
