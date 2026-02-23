"""LocusGraph batch operations utilities.

This module provides utilities for performing bulk operations efficiently
using LocusGraph's context linking capabilities.
"""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar, Callable, Optional

from src.schemas.events import EventKind
from src.services.locusgraph.service import locusgraph_service

T = TypeVar("T")


class BatchOperation:
    """Manages batch operations with context linking for tracking."""

    BATCH_CONTEXT_PREFIX = "batch_operation"
    BATCH_EVENT_KIND = "batch.create"

    @staticmethod
    async def create(
        user_id: str,
        entity_type: str,
        operation_type: str,  # 'create', 'update', 'delete'
        description: Optional[str] = None,
    ) -> str:
        """Create a new batch operation context.

        Args:
            user_id: User ID performing the batch operation
            entity_type: Type of entities ('appointment', 'emergency_contact', etc.)
            operation_type: Type of operation
            description: Optional description of the batch operation

        Returns:
            Batch context ID
        """
        batch_id = locusgraph_service.new_id()
        batch_context = (
            f"{BatchOperation.BATCH_CONTEXT_PREFIX}:{user_id}:{entity_type}:{batch_id}"
        )

        payload = {
            "batch_id": batch_id,
            "entity_type": entity_type,
            "operation_type": operation_type,
            "user_id": user_id,
            "description": description,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "entity_ids": [],
            "status": "in_progress",
            "total_items": 0,
            "successful_items": 0,
            "failed_items": 0,
        }

        await locusgraph_service.store_event(
            event_kind=BatchOperation.BATCH_EVENT_KIND,
            context_id=batch_context,
            payload=payload,
            source="system",
        )

        return batch_context

    @staticmethod
    async def add_entity(
        batch_context: str,
        entity_id: str,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """Add an entity to the batch operation.

        Args:
            batch_context: Batch context ID
            entity_id: ID of the entity being added
            success: Whether the operation succeeded
            error_message: Error message if operation failed
        """
        await locusgraph_service.store_event(
            event_kind="batch.item_added",
            context_id=f"{batch_context}:item:{entity_id}",
            payload={
                "entity_id": entity_id,
                "success": success,
                "error_message": error_message,
                "added_at": datetime.now(timezone.utc).isoformat(),
            },
            related_to=[batch_context],
            source="system",
        )

    @staticmethod
    async def complete(
        batch_context: str,
        total_items: int,
        successful_items: int,
        failed_items: int,
        entity_ids: list[str],
    ) -> None:
        """Mark a batch operation as complete.

        Args:
            batch_context: Batch context ID
            total_items: Total number of items in the batch
            successful_items: Number of successful items
            failed_items: Number of failed items
            entity_ids: List of entity IDs
        """
        await locusgraph_service.store_event(
            event_kind="batch.completed",
            context_id=f"{batch_context}:completed",
            payload={
                "total_items": total_items,
                "successful_items": successful_items,
                "failed_items": failed_items,
                "entity_ids": entity_ids,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "status": "completed",
            },
            extends=[batch_context],
            source="system",
        )

    @staticmethod
    async def fail(
        batch_context: str,
        error_message: str,
        partial_entity_ids: Optional[list[str]] = None,
    ) -> None:
        """Mark a batch operation as failed.

        Args:
            batch_context: Batch context ID
            error_message: Error message explaining the failure
            partial_entity_ids: List of entity IDs that were created before failure
        """
        await locusgraph_service.store_event(
            event_kind="batch.failed",
            context_id=f"{batch_context}:failed",
            payload={
                "error_message": error_message,
                "partial_entity_ids": partial_entity_ids or [],
                "failed_at": datetime.now(timezone.utc).isoformat(),
                "status": "failed",
            },
            extends=[batch_context],
            source="system",
        )

    @staticmethod
    async def get_batch_status(batch_context: str) -> dict:
        """Get the status of a batch operation.

        Args:
            batch_context: Batch context ID

        Returns:
            Dictionary with batch status information
        """
        memories = await locusgraph_service.retrieve_context(
            query=f"batch operation {batch_context}",
            context_ids=[batch_context],
            limit=1,
        )

        if not memories:
            return {
                "status": "not_found",
                "batch_context": batch_context,
            }

        # Get all related events (items added, completion, etc.)
        all_events = await locusgraph_service.retrieve_context(
            query=f"batch operation {batch_context}",
            limit=100,
        )

        return {
            "batch_context": batch_context,
            "status": memories[0].get("payload", {}).get("status", "unknown"),
            "total_events": len(all_events),
            "created_at": memories[0].get("timestamp"),
        }


class BatchAppointmentCreator:
    """Batch creator for appointments."""

    @staticmethod
    async def create_appointments(
        appointments: list[dict],
        user_id: str,
        schedule_reminders: bool = True,
    ) -> dict:
        """Create multiple appointments in a batch.

        Args:
            appointments: List of appointment data dictionaries
            user_id: User ID creating the appointments
            schedule_reminders: Whether to schedule reminders for each appointment

        Returns:
            Dictionary with batch results
        """
        from src.schemas.appointments import AppointmentEventDefinition
        from src.services.temporal.scheduler import TemporalScheduler

        batch_context = await BatchOperation.create(
            user_id=user_id,
            entity_type="appointment",
            operation_type="create",
            description=f"Create {len(appointments)} appointments",
        )

        created_ids = []
        successful_count = 0
        failed_count = 0

        for apt_data in appointments:
            try:
                appointment_id = locusgraph_service.new_id()
                context_id = AppointmentEventDefinition.get_context_id(appointment_id)

                payload = AppointmentEventDefinition.create_payload(
                    title=apt_data.get("title"),
                    doctor_name=apt_data.get("doctor_name"),
                    location=apt_data.get("location"),
                    scheduled_at=datetime.fromisoformat(apt_data["scheduled_at"]),
                    notes=apt_data.get("notes"),
                    reminder_minutes_before=apt_data.get("reminder_minutes_before"),
                    user_id=user_id,
                )

                await locusgraph_service.store_event(
                    event_kind=EventKind.APPOINTMENT_CREATE,
                    context_id=context_id,
                    payload=payload,
                    related_to=[batch_context],
                )

                created_ids.append(appointment_id)

                # Schedule reminder if requested
                if schedule_reminders and apt_data.get("reminder_minutes_before"):
                    scheduled_at = datetime.fromisoformat(apt_data["scheduled_at"])
                    await TemporalScheduler.schedule_reminder(
                        target_entity_type="appointment",
                        target_entity_id=appointment_id,
                        trigger_at=scheduled_at,
                        reminder_minutes_before=apt_data["reminder_minutes_before"],
                        user_id=user_id,
                        title=f"Appointment: {apt_data.get('title')}",
                    )

                await BatchOperation.add_entity(
                    batch_context, appointment_id, success=True
                )
                successful_count += 1

            except Exception as e:
                await BatchOperation.add_entity(
                    batch_context,
                    appointment_id if "appointment_id" in locals() else "unknown",
                    success=False,
                    error_message=str(e),
                )
                failed_count += 1

        # Complete the batch
        await BatchOperation.complete(
            batch_context=batch_context,
            total_items=len(appointments),
            successful_items=successful_count,
            failed_items=failed_count,
            entity_ids=created_ids,
        )

        return {
            "batch_context": batch_context,
            "total_items": len(appointments),
            "successful_items": successful_count,
            "failed_items": failed_count,
            "entity_ids": created_ids,
        }

    @staticmethod
    async def get_batch_appointments(batch_context: str) -> list[dict]:
        """Retrieve all appointments from a batch operation.

        Args:
            batch_context: Batch context ID

        Returns:
            List of appointment memories
        """
        # Get all memories related to the batch context
        memories = await locusgraph_service.retrieve_context(
            query=f"batch operation {batch_context}",
            limit=100,
        )

        appointments = []
        for memory in memories:
            context_id = memory.get("context_id", "")
            # Filter to only appointment contexts
            if context_id.startswith("appointment:"):
                appointments.append(memory)

        return appointments


class BatchEmergencyContactCreator:
    """Batch creator for emergency contacts."""

    @staticmethod
    async def create_emergency_contacts(
        contacts: list[dict],
        user_id: str,
        ensure_one_primary: bool = True,
    ) -> dict:
        """Create multiple emergency contacts in a batch.

        Args:
            contacts: List of contact data dictionaries
            user_id: User ID creating the contacts
            ensure_one_primary: Whether to ensure only one primary contact

        Returns:
            Dictionary with batch results
        """
        from src.schemas.emergency import EmergencyContactEventDefinition

        batch_context = await BatchOperation.create(
            user_id=user_id,
            entity_type="emergency_contact",
            operation_type="create",
            description=f"Create {len(contacts)} emergency contacts",
        )

        created_ids = []
        successful_count = 0
        failed_count = 0
        primary_count = 0

        for contact_data in contacts:
            try:
                contact_id = locusgraph_service.new_id()
                context_id = EmergencyContactEventDefinition.get_context_id(contact_id)

                # Check primary constraint
                is_primary = contact_data.get("is_primary", False)
                if ensure_one_primary and is_primary:
                    if primary_count > 0:
                        # Make this one primary, others not
                        is_primary = False
                        contact_data["is_primary"] = False

                payload = EmergencyContactEventDefinition.create_payload(
                    name=contact_data.get("name"),
                    relationship=contact_data.get("relationship"),
                    phone=contact_data.get("phone"),
                    is_primary=is_primary,
                    user_id=user_id,
                )

                await locusgraph_service.store_event(
                    event_kind=EventKind.EMERGENCY_CONTACT_CREATE,
                    context_id=context_id,
                    payload=payload,
                    related_to=[batch_context],
                )

                created_ids.append(contact_id)

                if is_primary:
                    primary_count += 1

                await BatchOperation.add_entity(batch_context, contact_id, success=True)
                successful_count += 1

            except Exception as e:
                await BatchOperation.add_entity(
                    batch_context,
                    contact_id if "contact_id" in locals() else "unknown",
                    success=False,
                    error_message=str(e),
                )
                failed_count += 1

        # Complete the batch
        await BatchOperation.complete(
            batch_context=batch_context,
            total_items=len(contacts),
            successful_items=successful_count,
            failed_items=failed_count,
            entity_ids=created_ids,
        )

        return {
            "batch_context": batch_context,
            "total_items": len(contacts),
            "successful_items": successful_count,
            "failed_items": failed_count,
            "entity_ids": created_ids,
            "primary_contacts": primary_count,
        }


class BatchMeditationSessionCreator:
    """Batch creator for meditation sessions."""

    @staticmethod
    async def create_sessions(
        sessions: list[dict],
    ) -> dict:
        """Create multiple meditation sessions in a batch.

        Args:
            sessions: List of session data dictionaries

        Returns:
            Dictionary with batch results
        """
        from src.schemas.meditation import MeditationSessionEventDefinition

        batch_context = await BatchOperation.create(
            user_id="system",
            entity_type="meditation_session",
            operation_type="create",
            description=f"Create {len(sessions)} meditation sessions",
        )

        created_ids = []
        successful_count = 0
        failed_count = 0

        for session_data in sessions:
            try:
                session_id = locusgraph_service.new_id()
                context_id = MeditationSessionEventDefinition.get_context_id(session_id)

                payload = MeditationSessionEventDefinition.create_payload(
                    title=session_data.get("title"),
                    description=session_data.get("description"),
                    audio_url=session_data.get("audio_url"),
                    duration_minutes=session_data.get("duration_minutes"),
                    category=session_data.get("category"),
                )

                await locusgraph_service.store_event(
                    event_kind=EventKind.MEDITATION_SESSION_CREATE,
                    context_id=context_id,
                    payload=payload,
                    related_to=[batch_context],
                )

                created_ids.append(session_id)

                await BatchOperation.add_entity(batch_context, session_id, success=True)
                successful_count += 1

            except Exception as e:
                await BatchOperation.add_entity(
                    batch_context,
                    session_id if "session_id" in locals() else "unknown",
                    success=False,
                    error_message=str(e),
                )
                failed_count += 1

        # Complete the batch
        await BatchOperation.complete(
            batch_context=batch_context,
            total_items=len(sessions),
            successful_items=successful_count,
            failed_items=failed_count,
            entity_ids=created_ids,
        )

        return {
            "batch_context": batch_context,
            "total_items": len(sessions),
            "successful_items": successful_count,
            "failed_items": failed_count,
            "entity_ids": created_ids,
        }
