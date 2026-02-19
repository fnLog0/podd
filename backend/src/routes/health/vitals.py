"""Routes for Vitals CRUD operations."""

from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_current_user
from src.schemas.events import EventKind
from src.schemas.health import VitalsCreate, VitalsResponse, VitalsUpdate, VitalsEventDefinition
from src.services.locusgraph_service import locusgraph_service

router = APIRouter(
    prefix="/vitals", tags=["vitals"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[VitalsResponse])
async def get_vitals(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    date_from: Optional[date] = Query(
        None, description="Filter from date (YYYY-MM-DD)"
    ),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    current_user=Depends(get_current_user),
):
    """Retrieve all vitals entries for the current user with optional date range filtering."""
    query_parts = [f"vitals user {current_user.id}"]
    if date_from:
        query_parts.append(f"from {date_from.isoformat()}")
    if date_to:
        query_parts.append(f"to {date_to.isoformat()}")

    query = " ".join(query_parts)
    print(f"DEBUG: Querying vitals with: '{query}'")
    print(f"DEBUG: Current user ID: {current_user.id}")

    memories = await locusgraph_service.retrieve_context(
        query=query,
        limit=limit,
    )
    print(f"DEBUG: Retrieved {len(memories)} memories")

    vitals_entries = []
    for memory in memories:
        payload = memory.get("payload", {})
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

    return vitals_entries


@router.get("/{vitals_id}", response_model=VitalsResponse)
async def get_vitals(vitals_id: str, current_user=Depends(get_current_user)):
    """Retrieve a specific vitals entry."""
    context_id = VitalsEventDefinition.get_context_id(vitals_id)
    memories = await locusgraph_service.retrieve_context(
        query=f"vitals {vitals_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vitals entry not found",
        )

    memory = memories[0]
    payload = memory.get("payload", {})

    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return VitalsResponse(
        id=memory.get("id", ""),
        user_id=payload.get("user_id", ""),
        blood_pressure_systolic=payload.get("blood_pressure_systolic"),
        blood_pressure_diastolic=payload.get("blood_pressure_diastolic"),
        heart_rate=payload.get("heart_rate"),
        blood_sugar=payload.get("blood_sugar"),
        temperature=payload.get("temperature"),
        weight_kg=payload.get("weight_kg"),
        logged_at=datetime.fromisoformat(payload.get("logged_at", "")),
        created_at=datetime.fromisoformat(memory.get("timestamp", "")),
    )


@router.post("", response_model=VitalsResponse, status_code=status.HTTP_201_CREATED)
async def create_vitals(
    vitals_data: VitalsCreate,
    related_to: Optional[str] = Query(
        None, description="Related event ID (e.g., medication log)"
    ),
    current_user=Depends(get_current_user),
):
    """Create a new vitals entry. Can be linked to medication logs or other events via related_to."""
    vitals_id = locusgraph_service.new_id()
    context_id = VitalsEventDefinition.get_context_id(vitals_id)

    # Set logged_at to current time if not provided
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

    print(f"DEBUG: Storing vitals for user {current_user.id} with context_id={context_id}")
    print(f"DEBUG: Payload: {payload}")

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


@router.put("/{vitals_id}", response_model=VitalsResponse)
async def update_vitals(
    vitals_id: str,
    vitals_data: VitalsUpdate,
    current_user=Depends(get_current_user),
):
    """Update an existing vitals entry."""
    context_id = VitalsEventDefinition.get_context_id(vitals_id)

    # Verify vitals exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"vitals {vitals_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vitals entry not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Merge existing data with updates
    updated_payload = VitalsEventDefinition.create_payload(
        blood_pressure_systolic=vitals_data.blood_pressure_systolic
        if vitals_data.blood_pressure_systolic is not None
        else payload.get("blood_pressure_systolic"),
        blood_pressure_diastolic=vitals_data.blood_pressure_diastolic
        if vitals_data.blood_pressure_diastolic is not None
        else payload.get("blood_pressure_diastolic"),
        heart_rate=vitals_data.heart_rate
        if vitals_data.heart_rate is not None
        else payload.get("heart_rate"),
        blood_sugar=vitals_data.blood_sugar
        if vitals_data.blood_sugar is not None
        else payload.get("blood_sugar"),
        temperature=vitals_data.temperature
        if vitals_data.temperature is not None
        else payload.get("temperature"),
        weight_kg=vitals_data.weight_kg
        if vitals_data.weight_kg is not None
        else payload.get("weight_kg"),
        logged_at=datetime.fromisoformat(payload.get("logged_at")),
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.VITALS_UPDATE,
        context_id=context_id,
        payload=updated_payload,
    )

    return VitalsResponse(
        id=vitals_id,
        user_id=str(current_user.id),
        blood_pressure_systolic=updated_payload.get("blood_pressure_systolic"),
        blood_pressure_diastolic=updated_payload.get("blood_pressure_diastolic"),
        heart_rate=updated_payload.get("heart_rate"),
        blood_sugar=updated_payload.get("blood_sugar"),
        temperature=updated_payload.get("temperature"),
        weight_kg=updated_payload.get("weight_kg"),
        logged_at=datetime.fromisoformat(updated_payload["logged_at"]),
        created_at=datetime.fromisoformat(memories[0].get("timestamp", "")),
    )


@router.delete("/{vitals_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vitals(vitals_id: str, current_user=Depends(get_current_user)):
    """Delete a vitals entry."""
    context_id = VitalsEventDefinition.get_context_id(vitals_id)

    # Verify vitals exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"vitals {vitals_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vitals entry not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Store deletion event
    await locusgraph_service.store_event(
        event_kind=EventKind.VITALS_DELETE,
        context_id=context_id,
        payload={
            "deleted": True,
            "vitals_id": vitals_id,
            "user_id": str(current_user.id),
        },
    )

    return None
