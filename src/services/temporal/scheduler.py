"""LocusGraph temporal utilities for time-based queries and scheduling.

This module provides utilities for working with temporal data in LocusGraph,
including metadata enrichment, time-range queries, and temporal context management.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from src.schemas.events import EventKind
from src.services.locusgraph.service import locusgraph_service


class TemporalContext:
    """Utilities for enriching contexts with temporal metadata."""

    TEMPORAL_METADATA_KEY = "temporal"

    @staticmethod
    def enrich_payload(
        payload: dict, temporal_type: str, timestamp: Optional[datetime] = None
    ) -> dict:
        """Enrich a payload with temporal metadata.

        Args:
            payload: Original payload
            temporal_type: Type of temporal event ('scheduled', 'upcoming', 'past', 'due')
            timestamp: Timestamp to use (defaults to now)

        Returns:
            Enriched payload with temporal metadata
        """
        ts = timestamp or datetime.now(timezone.utc)

        temporal_metadata = {
            "type": temporal_type,
            "timestamp": ts.isoformat(),
            "timezone": "UTC",
            "year": ts.year,
            "month": ts.month,
            "day": ts.day,
            "hour": ts.hour,
            "day_of_week": ts.strftime("%a").lower(),
            "is_today": (ts.date() == datetime.now(timezone.utc).date()),
        }

        enriched = payload.copy()
        if "metadata" not in enriched:
            enriched["metadata"] = {}
        enriched["metadata"][TemporalContext.TEMPORAL_METADATA_KEY] = temporal_metadata

        return enriched

    @staticmethod
    def get_temporal_query(
        temporal_type: str, user_id: str, time_window: Optional[timedelta] = None
    ) -> str:
        """Generate a temporal-aware query for LocusGraph.

        Args:
            temporal_type: Type of temporal event ('upcoming', 'past', 'due', 'today')
            user_id: User ID to filter for
            time_window: Optional time window for query (e.g., 7 days)

        Returns:
            Semantic query string for LocusGraph
        """
        base_query = f"{temporal_type} items user {user_id}"

        if time_window:
            if time_window.days > 0:
                base_query += f" next {time_window.days} days"
            elif time_window.seconds > 3600:
                hours = time_window.seconds // 3600
                base_query += f" next {hours} hours"

        return base_query

    @staticmethod
    def is_upcoming(
        timestamp: datetime, reference_time: Optional[datetime] = None
    ) -> bool:
        """Check if a timestamp is in the future relative to reference time.

        Args:
            timestamp: Timestamp to check
            reference_time: Reference time (defaults to now)

        Returns:
            True if timestamp is in the future
        """
        ref = reference_time or datetime.now(timezone.utc)
        return timestamp > ref

    @staticmethod
    def is_past(timestamp: datetime, reference_time: Optional[datetime] = None) -> bool:
        """Check if a timestamp is in the past relative to reference time.

        Args:
            timestamp: Timestamp to check
            reference_time: Reference time (defaults to now)

        Returns:
            True if timestamp is in the past
        """
        ref = reference_time or datetime.now(timezone.utc)
        return timestamp < ref

    @staticmethod
    def is_today(timestamp: datetime) -> bool:
        """Check if a timestamp is today.

        Args:
            timestamp: Timestamp to check

        Returns:
            True if timestamp is today
        """
        return timestamp.date() == datetime.now(timezone.utc).date()

    @staticmethod
    def get_time_range_for_type(
        temporal_type: str, reference_time: Optional[datetime] = None
    ) -> tuple[datetime, datetime]:
        """Get the start and end of a time range for a temporal type.

        Args:
            temporal_type: 'today', 'this_week', 'this_month', 'this_year'
            reference_time: Reference time (defaults to now)

        Returns:
            Tuple of (start_time, end_time)
        """
        ref = reference_time or datetime.now(timezone.utc)

        if temporal_type == "today":
            start = ref.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)

        elif temporal_type == "this_week":
            days_since_monday = ref.weekday()  # 0 = Monday
            start = ref.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
                days=days_since_monday
            )
            end = start + timedelta(days=7)

        elif temporal_type == "this_month":
            start = ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if ref.month == 12:
                end = ref.replace(
                    year=ref.year + 1,
                    month=1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
            else:
                end = ref.replace(
                    month=ref.month + 1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )

        elif temporal_type == "this_year":
            start = ref.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end = ref.replace(
                year=ref.year + 1,
                month=1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

        else:
            # Default to today
            start = ref.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)

        return start, end


class TemporalScheduler:
    """Utilities for scheduling and managing time-based events in LocusGraph."""

    REMINDER_CONTEXT_PREFIX = "reminder_scheduled"
    SCHEDULED_EVENT_KIND = "reminder.scheduled"

    @staticmethod
    async def schedule_reminder(
        target_entity_type: str,
        target_entity_id: str,
        trigger_at: datetime,
        reminder_minutes_before: int,
        user_id: str,
        title: str,
        message: Optional[str] = None,
    ) -> str:
        """Schedule a reminder for an entity (appointment, meditation, etc.).

        Args:
            target_entity_type: Type of entity ('appointment', 'meditation', etc.)
            target_entity_id: ID of the entity to remind about
            trigger_at: When the original event occurs
            reminder_minutes_before: Minutes before the event to trigger reminder
            user_id: User ID to notify
            title: Title of the reminder
            message: Optional custom message

        Returns:
            Reminder context ID
        """
        reminder_time = trigger_at - timedelta(minutes=reminder_minutes_before)

        # Enrich payload with temporal metadata
        payload = {
            "target_entity_type": target_entity_type,
            "target_entity_id": target_entity_id,
            "original_event_time": trigger_at.isoformat(),
            "trigger_at": reminder_time.isoformat(),
            "reminder_minutes_before": reminder_minutes_before,
            "user_id": user_id,
            "title": title,
            "message": message,
        }

        # Add temporal metadata
        payload = TemporalContext.enrich_payload(payload, "due", reminder_time)

        # Link to the target entity context
        related_to = [f"{target_entity_type}:{target_entity_id}"]

        # Store as reminder event
        reminder_id = locusgraph_service.new_id()
        reminder_context = f"{TemporalScheduler.REMINDER_CONTEXT_PREFIX}:{reminder_id}"

        await locusgraph_service.store_event(
            event_kind=TemporalScheduler.SCHEDULED_EVENT_KIND,
            context_id=reminder_context,
            payload=payload,
            related_to=related_to,
            source="system",
        )

        return reminder_context

    @staticmethod
    async def get_due_reminders(limit: int = 100) -> list[dict]:
        """Retrieve reminders that are due now.

        Args:
            limit: Maximum number of reminders to retrieve

        Returns:
            List of due reminder memories
        """
        now = datetime.now(timezone.utc)
        query = f"reminders due now before {now.isoformat()}"

        memories = await locusgraph_service.retrieve_context(
            query=query,
            limit=limit,
            context_types={TemporalScheduler.SCHEDULED_EVENT_KIND: ["due"]},
        )

        # Filter to only actually due reminders
        due_reminders = []
        for memory in memories:
            payload = memory.get("payload", {})
            trigger_at = payload.get("trigger_at")
            if trigger_at:
                if isinstance(trigger_at, str):
                    trigger_at = datetime.fromisoformat(trigger_at)
                if trigger_at <= now:
                    due_reminders.append(memory)

        return due_reminders

    @staticmethod
    async def mark_reminder_sent(reminder_context_id: str) -> None:
        """Mark a reminder as sent.

        Args:
            reminder_context_id: Context ID of the reminder to mark
        """
        await locusgraph_service.store_event(
            event_kind="reminder.sent",
            context_id=reminder_context_id,
            payload={
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "status": "sent",
            },
            extends=[reminder_context_id],
            source="system",
        )

    @staticmethod
    async def cancel_reminder(reminder_context_id: str) -> None:
        """Cancel a scheduled reminder.

        Args:
            reminder_context_id: Context ID of the reminder to cancel
        """
        await locusgraph_service.store_event(
            event_kind="reminder.cancelled",
            context_id=reminder_context_id,
            payload={
                "cancelled_at": datetime.now(timezone.utc).isoformat(),
                "status": "cancelled",
            },
            extends=[reminder_context_id],
            source="system",
        )


async def get_temporal_contexts(
    user_id: str,
    temporal_type: str,
    time_range: Optional[tuple[datetime, datetime]] = None,
    limit: int = 50,
) -> list[dict]:
    """Generic function to retrieve contexts with temporal filtering.

    Args:
        user_id: User ID to filter for
        temporal_type: Type of temporal query ('upcoming', 'past', 'today', 'due')
        time_range: Optional tuple of (start, end) for custom time range
        limit: Maximum number of results

    Returns:
        List of filtered memories
    """
    query = TemporalContext.get_temporal_query(temporal_type, user_id)

    memories = await locusgraph_service.retrieve_context(
        query=query,
        limit=limit,
    )

    # Apply temporal filtering
    filtered = []
    now = datetime.now(timezone.utc)

    for memory in memories:
        payload = memory.get("payload", {})
        scheduled_at = (
            payload.get("scheduled_at")
            or payload.get("trigger_at")
            or payload.get("timestamp")
        )

        if isinstance(scheduled_at, str):
            scheduled_at = datetime.fromisoformat(scheduled_at)

        # Apply temporal type filter
        include = False
        if temporal_type == "upcoming":
            include = TemporalContext.is_upcoming(scheduled_at, now)
        elif temporal_type == "past":
            include = TemporalContext.is_past(scheduled_at, now)
        elif temporal_type == "today":
            include = TemporalContext.is_today(scheduled_at)
        elif temporal_type == "due":
            include = scheduled_at <= now

        # Apply custom time range if provided
        if include and time_range:
            start, end = time_range
            include = start <= scheduled_at <= end

        if include:
            filtered.append(memory)

    return filtered
