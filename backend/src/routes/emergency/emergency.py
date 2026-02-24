"""Routes for Emergency Contacts CRUD operations."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_current_user
from src.schemas.emergency import (
    EmergencyContactCreate,
    EmergencyContactEventDefinition,
    EmergencyContactResponse,
    EmergencyContactUpdate,
)
from src.schemas.events import EventKind
from src.services.locusgraph.service import locusgraph_service
from src.services.validation.memory import PhoneValidator, ValidationMemory
from src.services.validation.duplicate import EmergencyContactDuplicateDetector
from src.services.batch.operations import BatchEmergencyContactCreator
from src.services.locusgraph.cache import EmergencyContactCache

router = APIRouter(
    prefix="/emergency-contacts",
    tags=["emergency"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[EmergencyContactResponse])
async def get_emergency_contacts(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return"),
    use_cache: bool = Query(True, description="Use cached data if available"),
    current_user=Depends(get_current_user),
):
    """List all emergency contacts for the current user with caching."""
    # Try cache first
    if use_cache:
        cached = await EmergencyContactCache.get_contacts(str(current_user.id))
        if cached:
            # Sort: primary contacts first, then by name
            cached.sort(
                key=lambda x: (
                    not x.get("is_primary", False),
                    x.get("name", "").lower(),
                )
            )
            return [EmergencyContactResponse(**contact) for contact in cached]

    # Fetch from LocusGraph
    memories = await locusgraph_service.retrieve_context(
        query=f"emergency contacts user {current_user.id}",
        limit=limit,
    )

    contacts = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            contacts.append(
                {
                    "id": memory.get("id", ""),
                    "user_id": payload.get("user_id", ""),
                    "name": payload.get("name", ""),
                    "relationship": payload.get("relationship"),
                    "phone": payload.get("phone", ""),
                    "is_primary": payload.get("is_primary", False),
                    "created_at": datetime.fromisoformat(memory.get("timestamp", "")),
                    "updated_at": datetime.fromisoformat(memory.get("timestamp", "")),
                }
            )

    # Sort: primary contacts first, then by name
    contacts.sort(
        key=lambda x: (not x.get("is_primary", False), x.get("name", "").lower())
    )

    # Cache the results
    if use_cache:
        await EmergencyContactCache.set_contacts(str(current_user.id), contacts)

    return [EmergencyContactResponse(**contact) for contact in contacts]


@router.post(
    "", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED
)
async def create_emergency_contact(
    contact_data: EmergencyContactCreate, current_user=Depends(get_current_user)
):
    """Add a new emergency contact with validation and duplicate checking."""
    # Validate phone number using validation memory
    is_valid, error_msg = await PhoneValidator.validate(
        phone=contact_data.phone,
        user_id=str(current_user.id),
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    # Check for duplicates by phone
    duplicate = await EmergencyContactDuplicateDetector.detect_duplicate(
        phone=contact_data.phone,
        user_id=str(current_user.id),
        name=contact_data.name,
    )

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Emergency contact with this phone number already exists",
        )

    # Check primary contact constraint
    if contact_data.is_primary:
        existing_primary = (
            await EmergencyContactDuplicateDetector.check_primary_contact_exists(
                user_id=str(current_user.id),
            )
        )

        if existing_primary:
            # Make existing primary contact non-primary
            await _update_primary_flag(
                context_id=existing_primary.get("context_id", ""),
                is_primary=False,
            )

    contact_id = locusgraph_service.new_id()
    context_id = EmergencyContactEventDefinition.get_context_id(contact_id)

    payload = EmergencyContactEventDefinition.create_payload(
        name=contact_data.name,
        relationship=contact_data.relationship,
        phone=contact_data.phone,
        is_primary=contact_data.is_primary,
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.EMERGENCY_CONTACT_CREATE,
        context_id=context_id,
        payload=payload,
    )

    # Remember successful phone validation
    await PhoneValidator.mark_success(
        phone=contact_data.phone,
        user_id=str(current_user.id),
    )

    # Invalidate cache for this user
    await EmergencyContactCache.invalidate_user_contacts(str(current_user.id))

    now = datetime.now(timezone.utc)
    return EmergencyContactResponse(
        id=contact_id,
        user_id=str(current_user.id),
        name=contact_data.name,
        relationship=contact_data.relationship,
        phone=contact_data.phone,
        is_primary=contact_data.is_primary,
        created_at=now,
        updated_at=now,
    )


@router.get("/{contact_id}", response_model=EmergencyContactResponse)
async def get_emergency_contact(
    contact_id: str, current_user=Depends(get_current_user)
):
    """Retrieve a specific emergency contact."""
    context_id = EmergencyContactEventDefinition.get_context_id(contact_id)
    memories = await locusgraph_service.retrieve_context(
        query=f"emergency contact {contact_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency contact not found",
        )

    memory = memories[0]
    payload = memory.get("payload", {})

    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return EmergencyContactResponse(
        id=contact_id,
        user_id=payload.get("user_id", ""),
        name=payload.get("name", ""),
        relationship=payload.get("relationship"),
        phone=payload.get("phone", ""),
        is_primary=payload.get("is_primary", False),
        created_at=datetime.fromisoformat(memory.get("timestamp", "")),
        updated_at=datetime.fromisoformat(memory.get("timestamp", "")),
    )


@router.put("/{contact_id}", response_model=EmergencyContactResponse)
async def update_emergency_contact(
    contact_id: str,
    contact_data: EmergencyContactUpdate,
    current_user=Depends(get_current_user),
):
    """Update an existing emergency contact."""
    context_id = EmergencyContactEventDefinition.get_context_id(contact_id)

    # Verify contact exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"emergency contact {contact_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency contact not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Merge existing data with updates
    updated_payload = EmergencyContactEventDefinition.create_payload(
        name=contact_data.name or payload.get("name"),
        relationship=contact_data.relationship or payload.get("relationship"),
        phone=contact_data.phone or payload.get("phone"),
        is_primary=(
            contact_data.is_primary
            if contact_data.is_primary is not None
            else payload.get("is_primary", False)
        ),
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.EMERGENCY_CONTACT_UPDATE,
        context_id=context_id,
        payload=updated_payload,
    )

    return EmergencyContactResponse(
        id=contact_id,
        user_id=str(current_user.id),
        name=updated_payload["name"],
        relationship=updated_payload.get("relationship"),
        phone=updated_payload["phone"],
        is_primary=updated_payload["is_primary"],
        created_at=datetime.fromisoformat(memories[0].get("timestamp", "")),
        updated_at=datetime.now(timezone.utc),
    )


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_emergency_contact(
    contact_id: str, current_user=Depends(get_current_user)
):
    """Delete an emergency contact."""
    context_id = EmergencyContactEventDefinition.get_context_id(contact_id)

    # Verify contact exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"emergency contact {contact_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency contact not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Prevent deleting last emergency contact
    all_contacts = await get_emergency_contacts(
        limit=100,
        current_user=current_user,
    )

    if len(all_contacts) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last emergency contact",
        )

    # Store deletion event
    await locusgraph_service.store_event(
        event_kind=EventKind.EMERGENCY_CONTACT_DELETE,
        context_id=context_id,
        payload={
            "deleted": True,
            "contact_id": contact_id,
            "user_id": str(current_user.id),
        },
    )

    # Invalidate cache for this user
    await EmergencyContactCache.invalidate_user_contacts(str(current_user.id))

    return None


@router.post("/batch", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_emergency_contacts_batch(
    contacts: list[EmergencyContactCreate],
    current_user=Depends(get_current_user),
):
    """Create multiple emergency contacts in a batch with validation."""
    # Validate all phone numbers first
    contacts_data = []
    for contact in contacts:
        is_valid, error_msg = await PhoneValidator.validate(
            phone=contact.phone,
            user_id=str(current_user.id),
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid phone number for {contact.name}: {error_msg}",
            )

        contacts_data.append(
            {
                "name": contact.name,
                "relationship": contact.relationship,
                "phone": contact.phone,
                "is_primary": contact.is_primary,
            }
        )

    result = await BatchEmergencyContactCreator.create_emergency_contacts(
        contacts=contacts_data,
        user_id=str(current_user.id),
        ensure_one_primary=True,
    )

    # Invalidate cache for this user
    await EmergencyContactCache.invalidate_user_contacts(str(current_user.id))

    return result


# Helper function to update primary flag
async def _update_primary_flag(context_id: str, is_primary: bool) -> None:
    """Update the primary flag for an existing emergency contact."""
    memories = await locusgraph_service.retrieve_context(
        query=f"emergency contact {context_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        return

    payload = memories[0].get("payload", {})
    payload["is_primary"] = is_primary

    await locusgraph_service.store_event(
        event_kind=EventKind.EMERGENCY_CONTACT_UPDATE,
        context_id=context_id,
        payload=payload,
    )
