"""Routes for Alarms and Notifications CRUD operations."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_current_user
from src.schemas.alarms import (
    AlarmCreate,
    AlarmEventDefinition,
    AlarmResponse,
    AlarmUpdate,
    NotificationEventDefinition,
    NotificationResponse,
)
from src.schemas.events import EventKind
from src.services.locusgraph.service import locusgraph_service

router = APIRouter(tags=["alarms"], dependencies=[Depends(get_current_user)])


# ==================== Alarm Endpoints ====================


@router.get("/alarms", response_model=list[AlarmResponse])
async def get_alarms(
    active_only: bool = Query(False, description="Filter to only active alarms"),
    current_user=Depends(get_current_user),
):
    """List all alarms for the current user."""
    query = f"alarms user {current_user.id}"
    memories = await locusgraph_service.retrieve_context(query=query, limit=100)

    alarms = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            # Filter by active status if requested
            if active_only and not payload.get("active", True):
                continue

            alarm_data = {
                "id": memory.get("event_id", ""),
                "user_id": payload.get("user_id", ""),
                "type": payload.get("type", "medication"),
                "title": payload.get("title", ""),
                "message": payload.get("message"),
                "time": payload.get("time", "09:00"),
                "days_of_week": payload.get("days_of_week", []),
                "active": payload.get("active", True),
                "reference_id": payload.get("reference_id"),
                "created_at": datetime.fromisoformat(memory.get("timestamp", "")),
                "updated_at": datetime.fromisoformat(memory.get("timestamp", "")),
            }
            alarms.append(alarm_data)

    # Sort by time
    alarms.sort(key=lambda x: x["time"])
    return [AlarmResponse(**alarm) for alarm in alarms]


@router.post("/alarms", response_model=AlarmResponse, status_code=status.HTTP_201_CREATED)
async def create_alarm(alarm_data: AlarmCreate, current_user=Depends(get_current_user)):
    """Create a new alarm."""
    alarm_id = locusgraph_service.new_id()
    context_id = AlarmEventDefinition.get_context_id(alarm_id)

    # Validate time format (HH:MM)
    try:
        datetime.strptime(alarm_data.time, "%H:%M")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time format. Use HH:MM (24-hour format)",
        )

    # Validate days_of_week
    valid_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    for day in alarm_data.days_of_week:
        if day.lower() not in valid_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid day: {day}. Use 3-letter lowercase format (mon, tue, wed, thu, fri, sat, sun)",
            )

    payload = AlarmEventDefinition.create_payload(
        type=alarm_data.type,
        title=alarm_data.title,
        message=alarm_data.message,
        time=alarm_data.time,
        days_of_week=[d.lower() for d in alarm_data.days_of_week],
        active=alarm_data.active,
        reference_id=alarm_data.reference_id,
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.ALARM_CREATE,
        context_id=context_id,
        payload=payload,
    )

    now = datetime.now(timezone.utc)
    return AlarmResponse(
        id=alarm_id,
        user_id=str(current_user.id),
        type=alarm_data.type,
        title=alarm_data.title,
        message=alarm_data.message,
        time=alarm_data.time,
        days_of_week=alarm_data.days_of_week,
        active=alarm_data.active,
        reference_id=alarm_data.reference_id,
        created_at=now,
        updated_at=now,
    )


@router.get("/alarms/{alarm_id}", response_model=AlarmResponse)
async def get_alarm(alarm_id: str, current_user=Depends(get_current_user)):
    """Retrieve a specific alarm."""
    context_id = AlarmEventDefinition.get_context_id(alarm_id)
    memories = await locusgraph_service.retrieve_context(
        query=f"alarm {alarm_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alarm not found",
        )

    memory = memories[0]
    payload = memory.get("payload", {})

    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return AlarmResponse(
        id=alarm_id,
        user_id=payload.get("user_id", ""),
        type=payload.get("type", "medication"),
        title=payload.get("title", ""),
        message=payload.get("message"),
        time=payload.get("time", "09:00"),
        days_of_week=payload.get("days_of_week", []),
        active=payload.get("active", True),
        reference_id=payload.get("reference_id"),
        created_at=datetime.fromisoformat(memory.get("timestamp", "")),
        updated_at=datetime.fromisoformat(memory.get("timestamp", "")),
    )


@router.put("/alarms/{alarm_id}", response_model=AlarmResponse)
async def update_alarm(
    alarm_id: str,
    alarm_data: AlarmUpdate,
    current_user=Depends(get_current_user),
):
    """Update an existing alarm."""
    context_id = AlarmEventDefinition.get_context_id(alarm_id)

    # Verify alarm exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"alarm {alarm_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alarm not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Validate time format if provided
    if alarm_data.time:
        try:
            datetime.strptime(alarm_data.time, "%H:%M")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid time format. Use HH:MM (24-hour format)",
            )

    # Validate days_of_week if provided
    if alarm_data.days_of_week:
        valid_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for day in alarm_data.days_of_week:
            if day.lower() not in valid_days:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid day: {day}. Use 3-letter lowercase format (mon, tue, wed, thu, fri, sat, sun)",
                )

    # Merge existing data with updates
    updated_payload = AlarmEventDefinition.create_payload(
        type=alarm_data.type or payload.get("type") or "medication",
        title=alarm_data.title or payload.get("title") or "Alarm",
        message=alarm_data.message if alarm_data.message is not None else payload.get("message"),
        time=alarm_data.time or payload.get("time") or "09:00",
        days_of_week=(
            [d.lower() for d in alarm_data.days_of_week]
            if alarm_data.days_of_week
            else payload.get("days_of_week", [])
        ),
        active=alarm_data.active if alarm_data.active is not None else payload.get("active", True),
        reference_id=(
            alarm_data.reference_id
            if alarm_data.reference_id is not None
            else payload.get("reference_id")
        ),
        user_id=str(current_user.id),
    )

    stored = await locusgraph_service.store_event(
        event_kind=EventKind.ALARM_UPDATE,
        context_id=context_id,
        payload=updated_payload,
    )

    return AlarmResponse(
        id=alarm_id,
        user_id=str(current_user.id),
        type=updated_payload["type"],
        title=updated_payload["title"],
        message=updated_payload.get("message"),
        time=updated_payload["time"],
        days_of_week=updated_payload["days_of_week"],
        active=updated_payload["active"],
        reference_id=updated_payload.get("reference_id"),
        created_at=datetime.fromisoformat(memories[0].get("timestamp", "")),
        updated_at=datetime.now(timezone.utc),
    )


@router.delete("/alarms/{alarm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alarm(alarm_id: str, current_user=Depends(get_current_user)):
    """Delete an alarm."""
    context_id = AlarmEventDefinition.get_context_id(alarm_id)

    # Verify alarm exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"alarm {alarm_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alarm not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Store deletion event
    await locusgraph_service.store_event(
        event_kind=EventKind.ALARM_DELETE,
        context_id=context_id,
        payload={
            "deleted": True,
            "alarm_id": alarm_id,
            "user_id": str(current_user.id),
        },
    )

    return None


# ==================== Notification Endpoints ====================


@router.get("/notifications", response_model=list[NotificationResponse])
async def get_notifications(
    unread_only: bool = Query(False, description="Filter to only unread notifications"),
    limit: int = Query(20, ge=1, le=100, description="Number of notifications to return"),
    current_user=Depends(get_current_user),
):
    """List notifications for the current user."""
    query = f"notifications user {current_user.id}"
    memories = await locusgraph_service.retrieve_context(query=query, limit=limit)

    notifications = []
    for memory in memories:
        payload = memory.get("payload", {})
        if payload.get("user_id") == str(current_user.id):
            # Filter by read status if requested
            if unread_only and payload.get("read", False):
                continue

            notification_data = {
                "id": memory.get("event_id", ""),
                "user_id": payload.get("user_id", ""),
                "alarm_id": payload.get("alarm_id", ""),
                "title": payload.get("title", ""),
                "message": payload.get("message", ""),
                "type": payload.get("type", "medication"),
                "read": payload.get("read", False),
                "created_at": datetime.fromisoformat(memory.get("timestamp", "")),
            }
            notifications.append(notification_data)

    # Sort by created_at (newest first)
    notifications.sort(key=lambda x: x["created_at"], reverse=True)
    return [NotificationResponse(**notif) for notif in notifications[:limit]]


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str, current_user=Depends(get_current_user)
):
    """Mark a notification as read."""
    context_id = NotificationEventDefinition.get_context_id(notification_id)

    # Verify notification exists and belongs to user
    memories = await locusgraph_service.retrieve_context(
        query=f"notification {notification_id}",
        context_ids=[context_id],
        limit=1,
    )

    if not memories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    payload = memories[0].get("payload", {})
    if payload.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Update payload to mark as read
    updated_payload = NotificationEventDefinition.create_payload(
        alarm_id=payload.get("alarm_id", ""),
        title=payload.get("title", ""),
        message=payload.get("message", ""),
        type=payload.get("type", "medication"),
        user_id=str(current_user.id),
    )
    updated_payload["read"] = True
    updated_payload["created_at"] = payload.get("created_at", datetime.now().isoformat())

    await locusgraph_service.store_event(
        event_kind=EventKind.NOTIFICATION_READ,
        context_id=context_id,
        payload=updated_payload,
    )

    return NotificationResponse(
        id=notification_id,
        user_id=str(current_user.id),
        alarm_id=payload.get("alarm_id", ""),
        title=payload.get("title", ""),
        message=payload.get("message", ""),
        type=payload.get("type", "medication"),
        read=True,
        created_at=datetime.fromisoformat(payload.get("created_at", "")),
    )
