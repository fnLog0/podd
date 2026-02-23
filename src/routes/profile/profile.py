from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_user
from src.schemas.events import EventKind
from src.schemas.profile import (
    ProfileCreate,
    ProfileEventDefinition,
    ProfileResponse,
    ProfileUpdate,
)
from src.services.locusgraph.service import locusgraph_service

router = APIRouter(
    prefix="/profile", tags=["profile"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=ProfileResponse)
async def get_profile(current_user=Depends(get_current_user)):
    context_id = ProfileEventDefinition.get_context_id(current_user.id)
    memories = await locusgraph_service.retrieve_context(
        query="profile data",
        context_ids=[context_id],
        limit=5,
    )

    if memories:
        # Get the most recent profile update
        latest_memory = memories[0]
        profile_data = latest_memory.get("payload", {})
        return ProfileResponse(
            user_id=current_user.id,
            **profile_data,
            updated_at=latest_memory.get("timestamp", ""),
        )

    # Return empty profile if none exists
    return ProfileResponse(user_id=current_user.id, updated_at=locusgraph_service.now())


@router.post("", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreate, current_user=Depends(get_current_user)
):
    context_id = ProfileEventDefinition.get_context_id(current_user.id)

    # Check if profile already exists
    existing = await locusgraph_service.retrieve_context(
        query="profile data",
        context_ids=[context_id],
        limit=1,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT to update.",
        )

    # Store profile creation event
    stored = await locusgraph_service.store_event(
        event_kind=EventKind.PROFILE_CREATE,
        context_id=context_id,
        payload=ProfileEventDefinition.create_payload(
            date_of_birth=profile_data.date_of_birth,
            gender=profile_data.gender,
            height_cm=profile_data.height_cm,
            weight_kg=profile_data.weight_kg,
            blood_type=profile_data.blood_type,
            allergies=profile_data.allergies,
            medical_conditions=profile_data.medical_conditions,
            dietary_preferences=profile_data.dietary_preferences,
        ),
    )

    return ProfileResponse(
        user_id=current_user.id,
        **profile_data.model_dump(exclude_none=True),
        updated_at=stored.get("timestamp", locusgraph_service.now()),
    )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate, current_user=Depends(get_current_user)
):
    context_id = ProfileEventDefinition.get_context_id(current_user.id)

    profile_dict = profile_data.model_dump(exclude_none=True)

    # Store profile update event
    stored = await locusgraph_service.store_event(
        event_kind=EventKind.PROFILE_UPDATE,
        context_id=context_id,
        payload=ProfileEventDefinition.create_payload(
            date_of_birth=profile_data.date_of_birth,
            gender=profile_data.gender,
            height_cm=profile_data.height_cm,
            weight_kg=profile_data.weight_kg,
            blood_type=profile_data.blood_type,
            allergies=profile_data.allergies,
            medical_conditions=profile_data.medical_conditions,
            dietary_preferences=profile_data.dietary_preferences,
        ),
    )

    return ProfileResponse(
        user_id=current_user.id,
        **profile_dict,
        updated_at=stored.get("timestamp", locusgraph_service.now()),
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(current_user=Depends(get_current_user)):
    context_id = ProfileEventDefinition.get_context_id(current_user.id)

    # Store profile deletion event
    await locusgraph_service.store_event(
        event_kind=EventKind.PROFILE_DELETE,
        context_id=context_id,
        payload={"deleted": True, "user_id": current_user.id},
    )

    return None
