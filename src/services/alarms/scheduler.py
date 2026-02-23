"""Background scheduler for checking and triggering alarms.

This module uses APScheduler to periodically check for alarms that should fire
and create notifications when they trigger.
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.schemas.alarms import AlarmEventDefinition, NotificationEventDefinition, AlarmType
from src.schemas.events import EventKind
from src.services.locusgraph.service import locusgraph_service


class AlarmScheduler:
    """Scheduler for checking and triggering alarms."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.last_check_time = None

    async def check_alarms(self):
        """Check for alarms that should fire now and create notifications."""
        now = datetime.now(timezone.utc)
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%a").lower()  # 3-letter lowercase day

        print(f"[AlarmScheduler] Checking alarms at {current_time} on {current_day}")

        # Get all active alarms
        query = "alarms"
        memories = await locusgraph_service.retrieve_context(query=query, limit=500)

        for memory in memories:
            payload = memory.get("payload", {})
            alarm_id = memory.get("event_id", "")
            alarm_time = payload.get("time", "")
            days_of_week = payload.get("days_of_week", [])
            active = payload.get("active", True)

            # Skip if alarm is not active
            if not active:
                continue

            # Skip if it's not the right day
            if current_day not in days_of_week:
                continue

            # Check if alarm should fire now (within the same minute)
            if alarm_time == current_time:
                # Check if we already sent a notification for this alarm today
                already_notified = await self._was_notified_today(alarm_id)
                if already_notified:
                    continue

                # Create notification
                await self._create_notification(payload, alarm_id)
                print(f"[AlarmScheduler] Triggered alarm {alarm_id}: {payload.get('title')}")

        self.last_check_time = now

    async def _was_notified_today(self, alarm_id: str) -> bool:
        """Check if a notification was already sent for this alarm today.

        Args:
            alarm_id: The alarm ID to check

        Returns:
            True if notification was sent today, False otherwise
        """
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)

        query = f"notification alarm {alarm_id}"
        memories = await locusgraph_service.retrieve_context(query=query, limit=10)

        for memory in memories:
            payload = memory.get("payload", {})
            created_at_str = payload.get("created_at", "")
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str)
                if created_at >= today_start:
                    return True

        return False

    async def _create_notification(self, alarm_payload: dict, alarm_id: str):
        """Create a notification for a triggered alarm.

        Args:
            alarm_payload: The alarm's payload data
            alarm_id: The alarm ID
        """
        alarm_type = alarm_payload.get("type", "medication")
        title = alarm_payload.get("title", "Reminder")
        message = alarm_payload.get("message", "")
        user_id = alarm_payload.get("user_id", "")

        # Generate message based on alarm type if not provided
        if not message:
            message = self._generate_message(alarm_type, title)

        notification_id = locusgraph_service.new_id()
        context_id = NotificationEventDefinition.get_context_id(notification_id)

        payload = NotificationEventDefinition.create_payload(
            alarm_id=alarm_id,
            title=title,
            message=message,
            type=alarm_type,
            user_id=user_id,
        )

        # Store notification event
        await locusgraph_service.store_event(
            event_kind=EventKind.NOTIFICATION_CREATE,
            context_id=context_id,
            payload=payload,
        )

        # TODO: Send to ESP32 device
        await self._send_to_esp32(user_id, title, message)

    def _generate_message(self, alarm_type: AlarmType, title: str) -> str:
        """Generate a notification message based on alarm type.

        Args:
            alarm_type: Type of alarm
            title: Title of the alarm

        Returns:
            Generated message
        """
        if alarm_type == "medication":
            return f"Time to take {title}"
        elif alarm_type == "water":
            return "Time to drink water"
        elif alarm_type == "meal":
            return f"Time for {title}"
        elif alarm_type == "meditation":
            return "Time for your meditation session"
        elif alarm_type == "appointment":
            return f"Upcoming appointment: {title}"
        else:
            return title

    async def _send_to_esp32(self, user_id: str, title: str, message: str):
        """Send notification to ESP32 device.

        This is a placeholder for ESP32 integration. In a real implementation,
        this would push the notification to the ESP32 device via WebSocket,
        MQTT, or HTTP endpoint.

        Args:
            user_id: User ID to send notification to
            title: Notification title
            message: Notification message
        """
        # TODO: Implement ESP32 integration
        # This could be:
        # - WebSocket push to connected ESP32 devices
        # - MQTT message to ESP32 topic
        # - HTTP webhook to ESP32 device
        print(f"[ESP32] Notification for user {user_id}: {title} - {message}")

    def start(self):
        """Start the alarm scheduler."""
        self.scheduler.add_job(
            self.check_alarms,
            trigger=IntervalTrigger(minutes=1),
            id="check_alarms",
            name="Check alarms every minute",
            replace_existing=True,
        )
        self.scheduler.start()
        print("[AlarmScheduler] Started - checking alarms every minute")

    def stop(self):
        """Stop the alarm scheduler."""
        self.scheduler.shutdown()
        print("[AlarmScheduler] Stopped")


# Global scheduler instance
alarm_scheduler = AlarmScheduler()
