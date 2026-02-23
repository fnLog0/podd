"""Routes for MedicationSchedule CRUD operations."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_current_user
from src.schemas.events import EventKind
from src.schemas.medication import (
    MedicationScheduleCreate,
    MedicationScheduleEventDefinition,
    MedicationScheduleResponse,
    MedicationScheduleUpdate,
)
from src.services.locusgraph.service import locusgraph_service

router = APIRouter(
    prefix="/medication-schedules",
    tags=["medication-schedules"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[MedicationScheduleResponse])
async def get_medication_schedules(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    medication_id: Optional[str] = Query(None, description="Filter by medication ID"),
    current_user=Depends(get_current_user),
):
    """Retrieve all medication schedules for the current user."""
    query_parts = ["medication schedules", f"user {current_user.id}"]
    if medication_id:
        query_parts.append(f"medication {medication_id}")

    memories = await locusgraph_service.retrieve_context(
        query=" ".join(query_parts),
        limit=limit,
    )

    schedules = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            if medication_id and payload.get("medication_id") != medication_id:
                continue

            # Try to fetch medication name if possible
            medication_name = None
            med_id = payload.get("medication_id")
            if med_id:
                try:
                    med_memories = await locusgraph_service.retrieve_context(
                        query=f"medication {med_id}",
                        context_ids=[
                            MedicationScheduleEventDefinition.get_context_id(
                                med_id
                            ).replace("med_schedule", "medication")
                        ],
                        limit=1,
                    )
                    if med_memories:
                        medication_name = med_memories[0].get("payload", {}).get("name")
                except Exception:
                    pass

            # Extract ID from multiple possible locations
            schedule_id = (
                memory.get("id")
                or memory.get("event_id")
            )
            if not schedule_id:
                context_id = memory.get("context_id", "")
                if ":" in context_id:
                    schedule_id = context_id.split(":")[-1]

            schedules.append(
                MedicationScheduleResponse(
                    id=schedule_id or "",
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


@router.get("/{schedule_id}", response_model=MedicationScheduleResponse)
async def get_medication_schedule(
    schedule_id: str, current_user=Depends(get_current_user)
):
    """Retrieve a specific medication schedule."""
    context_id = MedicationScheduleEventDefinition.get_context_id(schedule_id)
    memories = await locusgraph_service.retrieve_context(
        query=f"medication schedule {schedule_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication schedule not found",
        )

    memory = memories[0]
    payload = memory.get("payload", {})

    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Try to fetch medication name if possible
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

    # Extract ID from multiple possible locations
    extracted_id = (
        memory.get("id")
        or memory.get("event_id")
    )
    if not extracted_id:
        context_id = memory.get("context_id", "")
        if ":" in context_id:
            extracted_id = context_id.split(":")[-1]

    return MedicationScheduleResponse(
        id=extracted_id or "",
        user_id=payload.get("user_id", ""),
        medication_id=payload.get("medication_id", ""),
        medication_name=medication_name,
        time_of_day=payload.get("time_of_day", ""),
        days_of_week=payload.get("days_of_week", []),
        created_at=datetime.fromisoformat(memory.get("timestamp", "")),
        updated_at=datetime.fromisoformat(memory.get("timestamp", "")),
    )


@router.post(
    "", response_model=MedicationScheduleResponse, status_code=status.HTTP_201_CREATED
)
async def create_medication_schedule(
    schedule_data: MedicationScheduleCreate,
    current_user=Depends(get_current_user),
):
    """Create a new medication schedule."""
    schedule_id = locusgraph_service.new_id()
    context_id = MedicationScheduleEventDefinition.get_context_id(schedule_id)

    # Look up medication_id if only medication_name is provided
    medication_id = schedule_data.medication_id
    if not medication_id and schedule_data.medication_name:
        memories = await locusgraph_service.retrieve_context(
            query=f"medication {schedule_data.medication_name} user {current_user.id}",
            limit=10,
        )
        for memory in memories:
            payload = memory.get("payload", {})
            if (
                payload.get("user_id") == str(current_user.id)
                and payload.get("name") == schedule_data.medication_name
            ):
                # Try multiple ways to extract medication_id
                medication_id = (
                    payload.get("id")
                    or memory.get("id")
                    or memory.get("event_id")
                )
                # If still no ID, try extracting from context_id
                if not medication_id:
                    context_id = memory.get("context_id", "")
                    if ":" in context_id:
                        medication_id = context_id.split(":")[-1]
                break
        if not medication_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medication '{schedule_data.medication_name}' not found. Please create the medication first.",
            )

    if not medication_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either medication_id or medication_name must be provided",
        )

    payload = MedicationScheduleEventDefinition.create_payload(
        medication_id=medication_id,
        time_of_day=schedule_data.time_of_day,
        days_of_week=schedule_data.days_of_week,
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.MEDICATION_SCHEDULE_CREATE,
        context_id=context_id,
        payload=payload,
    )

    # Try to fetch medication name if not already provided
    medication_name = schedule_data.medication_name
    if not medication_name and medication_id:
        try:
            from src.schemas.medication import MedicationEventDefinition

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

    now = datetime.now(timezone.utc)
    return MedicationScheduleResponse(
        id=schedule_id,
        user_id=str(current_user.id),
        medication_id=medication_id,
        medication_name=medication_name,
        time_of_day=schedule_data.time_of_day,
        days_of_week=schedule_data.days_of_week,
        created_at=now,
        updated_at=now,
    )


@router.put("/{schedule_id}", response_model=MedicationScheduleResponse)
async def update_medication_schedule(
    schedule_id: str,
    schedule_data: MedicationScheduleUpdate,
    current_user=Depends(get_current_user),
):
    """Update an existing medication schedule."""
    context_id = MedicationScheduleEventDefinition.get_context_id(schedule_id)

    # Verify schedule exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"medication schedule {schedule_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication schedule not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Merge existing data with updates
    updated_payload = MedicationScheduleEventDefinition.create_payload(
        medication_id=schedule_data.medication_id or payload.get("medication_id"),
        time_of_day=schedule_data.time_of_day or payload.get("time_of_day"),
        days_of_week=(
            schedule_data.days_of_week
            if schedule_data.days_of_week is not None
            else payload.get("days_of_week", [])
        ),
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.MEDICATION_SCHEDULE_UPDATE,
        context_id=context_id,
        payload=updated_payload,
    )

    return MedicationScheduleResponse(
        id=schedule_id,
        user_id=str(current_user.id),
        medication_id=updated_payload["medication_id"],
        medication_name=None,
        time_of_day=updated_payload["time_of_day"],
        days_of_week=updated_payload["days_of_week"],
        created_at=datetime.fromisoformat(memories[0].get("timestamp", "")),
        updated_at=datetime.now(timezone.utc),
    )


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication_schedule(
    schedule_id: str, current_user=Depends(get_current_user)
):
    """Delete a medication schedule."""
    context_id = MedicationScheduleEventDefinition.get_context_id(schedule_id)

    # Verify schedule exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"medication schedule {schedule_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication schedule not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Store deletion event
    await locusgraph_service.store_event(
        event_kind=EventKind.MEDICATION_SCHEDULE_DELETE,
        context_id=context_id,
        payload={
            "deleted": True,
            "schedule_id": schedule_id,
            "user_id": str(current_user.id),
        },
    )

    return None
