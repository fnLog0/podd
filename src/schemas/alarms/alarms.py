"""Pydantic schemas for Alarm API requests and responses."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


AlarmType = Literal["medication", "water", "meal", "meditation", "appointment"]


class AlarmBase(BaseModel):
    """Base Alarm schema with common fields."""

    type: AlarmType = Field(..., description="Type of alarm (medication, water, meal, meditation, appointment)")
    title: str = Field(..., description="Title of the alarm")
    message: Optional[str] = Field(None, description="Additional message for the alarm")
    time: str = Field(..., description="Time in HH:MM format (24-hour)")
    days_of_week: list[str] = Field(
        default_factory=lambda: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        description="Days of the week the alarm should fire (3-letter lowercase)",
    )
    active: bool = Field(True, description="Whether the alarm is currently active")
    reference_id: Optional[str] = Field(
        None, description="Reference ID to linked entity (e.g., medication_id, appointment_id)"
    )


class AlarmCreate(AlarmBase):
    """Schema for creating a new alarm."""

    pass


class AlarmUpdate(AlarmBase):
    """Schema for updating an existing alarm."""

    type: Optional[AlarmType] = None
    title: Optional[str] = None
    message: Optional[str] = None
    time: Optional[str] = None
    days_of_week: Optional[list[str]] = None
    active: Optional[bool] = None
    reference_id: Optional[str] = None


class AlarmResponse(AlarmBase):
    """Schema for alarm response."""

    id: str = Field(..., description="Alarm ID")
    user_id: str = Field(..., description="User ID who owns this alarm")
    created_at: datetime = Field(..., description="Timestamp when alarm was created")
    updated_at: datetime = Field(..., description="Timestamp when alarm was last updated")


# ==================== Notification Schemas ====================


class NotificationBase(BaseModel):
    """Base Notification schema with common fields."""

    alarm_id: str = Field(..., description="ID of the alarm that triggered this notification")
    title: str = Field(..., description="Title of the notification")
    message: str = Field(..., description="Message content of the notification")
    type: AlarmType = Field(..., description="Type of notification (matches alarm type)")
    read: bool = Field(False, description="Whether the notification has been read")


class NotificationResponse(NotificationBase):
    """Schema for notification response."""

    id: str = Field(..., description="Notification ID")
    user_id: str = Field(..., description="User ID who owns this notification")
    created_at: datetime = Field(..., description="Timestamp when notification was created")
