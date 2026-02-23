"""LocusGraph schema migration tracking system.

This module provides utilities for tracking schema migrations and changes
within LocusGraph, enabling rollback and audit capabilities.
"""

from datetime import datetime, timezone
from typing import Optional

from src.services.locusgraph.service import locusgraph_service


class SchemaMigrationManager:
    """Manages schema migrations in LocusGraph."""

    MIGRATION_CONTEXT_PREFIX = "schema_migration"
    MIGRATION_EVENT_KIND = "migration.run"

    @staticmethod
    def _get_migration_context(migration_id: str) -> str:
        """Generate context ID for a migration.

        Args:
            migration_id: Migration identifier

        Returns:
            Context ID
        """
        return f"{SchemaMigrationManager.MIGRATION_CONTEXT_PREFIX}:{migration_id}"

    @staticmethod
    async def start_migration(
        migration_id: str,
        from_version: str,
        to_version: str,
        description: str,
        estimated_entities: Optional[int] = None,
    ) -> str:
        """Start a schema migration.

        Args:
            migration_id: Unique identifier for this migration
            from_version: Current schema version
            to_version: Target schema version
            description: Human-readable description
            estimated_entities: Estimated number of entities to migrate

        Returns:
            Migration context ID
        """
        context_id = SchemaMigrationManager._get_migration_context(migration_id)

        payload = {
            "migration_id": migration_id,
            "from_version": from_version,
            "to_version": to_version,
            "description": description,
            "estimated_entities": estimated_entities,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "in_progress",
            "entities_migrated": 0,
            "entities_failed": 0,
        }

        await locusgraph_service.store_event(
            event_kind=SchemaMigrationManager.MIGRATION_EVENT_KIND,
            context_id=context_id,
            payload=payload,
            source="system",
        )

        return context_id

    @staticmethod
    async def record_migration_step(
        migration_id: str,
        entity_type: str,
        entity_id: str,
        success: bool,
        old_data: Optional[dict] = None,
        new_data: Optional[dict] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Record a single migration step.

        Args:
            migration_id: Migration identifier
            entity_type: Type of entity being migrated
            entity_id: ID of the entity
            success: Whether the migration step succeeded
            old_data: Original data before migration
            new_data: New data after migration
            error_message: Error message if step failed
        """
        migration_context = SchemaMigrationManager._get_migration_context(migration_id)
        step_context = f"{migration_context}:step:{entity_id}"

        payload = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "success": success,
            "old_data": old_data,
            "new_data": new_data,
            "error_message": error_message,
            "migrated_at": datetime.now(timezone.utc).isoformat(),
        }

        await locusgraph_service.store_event(
            event_kind="migration.step",
            context_id=step_context,
            payload=payload,
            related_to=[migration_context],
            source="system",
        )

    @staticmethod
    async def complete_migration(
        migration_id: str,
        entities_migrated: int,
        entities_failed: int,
        notes: Optional[str] = None,
    ) -> None:
        """Mark a migration as completed.

        Args:
            migration_id: Migration identifier
            entities_migrated: Number of successfully migrated entities
            entities_failed: Number of entities that failed migration
            notes: Optional notes about the migration
        """
        migration_context = SchemaMigrationManager._get_migration_context(migration_id)

        payload = {
            "migration_id": migration_id,
            "entities_migrated": entities_migrated,
            "entities_failed": entities_failed,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
            "notes": notes,
        }

        await locusgraph_service.store_event(
            event_kind="migration.completed",
            context_id=f"{migration_context}:completed",
            payload=payload,
            extends=[migration_context],
            source="system",
        )

    @staticmethod
    async def fail_migration(
        migration_id: str,
        error_message: str,
        entities_migrated: Optional[int] = None,
    ) -> None:
        """Mark a migration as failed.

        Args:
            migration_id: Migration identifier
            error_message: Error explaining the failure
            entities_migrated: Number of entities migrated before failure
        """
        migration_context = SchemaMigrationManager._get_migration_context(migration_id)

        payload = {
            "migration_id": migration_id,
            "error_message": error_message,
            "entities_migrated": entities_migrated or 0,
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "status": "failed",
        }

        await locusgraph_service.store_event(
            event_kind="migration.failed",
            context_id=f"{migration_context}:failed",
            payload=payload,
            extends=[migration_context],
            source="system",
        )

    @staticmethod
    async def get_migration_status(migration_id: str) -> dict:
        """Get the status of a migration.

        Args:
            migration_id: Migration identifier

        Returns:
            Dictionary with migration status
        """
        context_id = SchemaMigrationManager._get_migration_context(migration_id)

        memories = await locusgraph_service.retrieve_context(
            query=f"migration {migration_id}",
            context_ids=[context_id],
            limit=100,
        )

        if not memories:
            return {
                "status": "not_found",
                "migration_id": migration_id,
            }

        # Find the main migration record
        main_migration = None
        steps = []

        for memory in memories:
            event_kind = memory.get("event_kind", "")
            if event_kind == SchemaMigrationManager.MIGRATION_EVENT_KIND:
                main_migration = memory.get("payload", {})
            elif event_kind == "migration.step":
                steps.append(memory.get("payload", {}))

        if not main_migration:
            return {
                "status": "unknown",
                "migration_id": migration_id,
            }

        return {
            "migration_id": migration_id,
            "status": main_migration.get("status", "unknown"),
            "from_version": main_migration.get("from_version"),
            "to_version": main_migration.get("to_version"),
            "description": main_migration.get("description"),
            "started_at": main_migration.get("started_at"),
            "completed_at": main_migration.get("completed_at"),
            "entities_migrated": main_migration.get("entities_migrated", 0),
            "entities_failed": main_migration.get("entities_failed", 0),
            "steps_recorded": len(steps),
        }

    @staticmethod
    async def list_migrations(
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """List migrations, optionally filtered by status.

        Args:
            status: Optional status filter ('in_progress', 'completed', 'failed')
            limit: Maximum number of migrations to return

        Returns:
            List of migration summaries
        """
        query = "schema migrations"
        if status:
            query += f" status {status}"

        memories = await locusgraph_service.retrieve_context(
            query=query,
            limit=limit,
        )

        migrations = []
        seen_migration_ids = set()

        for memory in memories:
            payload = memory.get("payload", {})
            migration_id = payload.get("migration_id")

            # Skip if we've already seen this migration
            if migration_id and migration_id in seen_migration_ids:
                continue

            if migration_id:
                seen_migration_ids.add(migration_id)
                migrations.append(
                    {
                        "migration_id": migration_id,
                        "status": payload.get("status", "unknown"),
                        "from_version": payload.get("from_version"),
                        "to_version": payload.get("to_version"),
                        "description": payload.get("description"),
                        "started_at": payload.get("started_at"),
                        "entities_migrated": payload.get("entities_migrated", 0),
                    }
                )

        # Sort by started_at descending (most recent first)
        migrations.sort(
            key=lambda m: m.get("started_at", ""),
            reverse=True,
        )

        return migrations

    @staticmethod
    async def get_rollback_data(migration_id: str) -> list[dict]:
        """Get data needed to rollback a migration.

        Args:
            migration_id: Migration identifier

        Returns:
            List of steps with old_data for rollback
        """
        context_id = SchemaMigrationManager._get_migration_context(migration_id)

        memories = await locusgraph_service.retrieve_context(
            query=f"migration steps {migration_id}",
            context_ids=[context_id],
            limit=1000,
        )

        rollback_data = []
        for memory in memories:
            payload = memory.get("payload", {})

            # Only include successful steps with old_data
            if payload.get("success") and payload.get("old_data"):
                rollback_data.append(
                    {
                        "entity_type": payload.get("entity_type"),
                        "entity_id": payload.get("entity_id"),
                        "old_data": payload.get("old_data"),
                        "new_data": payload.get("new_data"),
                    }
                )

        return rollback_data

    @staticmethod
    async def execute_rollback(migration_id: str, notes: Optional[str] = None) -> str:
        """Rollback a migration.

        Args:
            migration_id: Migration identifier to rollback
            notes: Optional notes about the rollback

        Returns:
            Rollback migration ID
        """
        # Get rollback data
        rollback_steps = await SchemaMigrationManager.get_rollback_data(migration_id)

        # Get original migration info
        migration_status = await SchemaMigrationManager.get_migration_status(
            migration_id
        )

        rollback_migration_id = (
            f"rollback_{migration_id}_{int(datetime.now().timestamp())}"
        )

        # Start rollback migration
        await SchemaMigrationManager.start_migration(
            migration_id=rollback_migration_id,
            from_version=migration_status.get("to_version"),
            to_version=migration_status.get("from_version"),
            description=f"Rollback of migration {migration_id}",
            estimated_entities=len(rollback_steps),
        )

        # Execute rollback steps
        entities_rolled_back = 0
        entities_failed = 0

        for step in rollback_steps:
            try:
                # Record rollback step
                await SchemaMigrationManager.record_migration_step(
                    migration_id=rollback_migration_id,
                    entity_type=step["entity_type"],
                    entity_id=step["entity_id"],
                    success=True,
                    old_data=step.get("new_data"),
                    new_data=step["old_data"],
                )
                entities_rolled_back += 1

            except Exception as e:
                await SchemaMigrationManager.record_migration_step(
                    migration_id=rollback_migration_id,
                    entity_type=step["entity_type"],
                    entity_id=step["entity_id"],
                    success=False,
                    error_message=str(e),
                )
                entities_failed += 1

        # Complete rollback migration
        await SchemaMigrationManager.complete_migration(
            migration_id=rollback_migration_id,
            entities_migrated=entities_rolled_back,
            entities_failed=entities_failed,
            notes=notes,
        )

        return rollback_migration_id


# Phase 4 schema migration definitions
PHASE4_MIGRATIONS = {
    "v4.0.0": {
        "version": "4.0.0",
        "description": "Initial Phase 4 schema - Meditation, Appointments, Emergency Contacts",
        "changes": [
            "Add meditation_session context pattern",
            "Add meditation_log context pattern",
            "Add appointment context pattern",
            "Add emergency_contact context pattern",
            "Add temporal metadata support",
            "Add validation failure tracking",
            "Add cache context patterns",
        ],
    },
}


async def ensure_schema_version(target_version: str = "4.0.0") -> dict:
    """Ensure the LocusGraph schema is at the target version.

    Args:
        target_version: Target schema version

    Returns:
        Dictionary with migration status
    """
    # List completed migrations
    completed_migrations = await SchemaMigrationManager.list_migrations(
        status="completed",
        limit=100,
    )

    # Extract versions from completed migrations
    completed_versions = {
        m.get("to_version")
        for m in completed_migrations
        if m.get("status") == "completed"
    }

    # Check if we need to run migrations
    if target_version in completed_versions:
        return {
            "status": "already_at_version",
            "current_version": target_version,
            "target_version": target_version,
        }

    # Find migrations to run
    # In a real implementation, you'd determine the full migration path
    # For now, we'll just run the target migration if not present

    migration_info = PHASE4_MIGRATIONS.get(target_version)
    if not migration_info:
        return {
            "status": "unknown_version",
            "target_version": target_version,
            "message": f"No migration defined for version {target_version}",
        }

    # Run migration
    migration_id = f"v{target_version.replace('.', '_')}"

    await SchemaMigrationManager.start_migration(
        migration_id=migration_id,
        from_version="3.0.0",  # Assuming Phase 1-3 was v3.0.0
        to_version=target_version,
        description=migration_info["description"],
        estimated_entities=0,  # Schema-only migration
    )

    # For schema-only migrations, we don't need to migrate individual entities
    await SchemaMigrationManager.complete_migration(
        migration_id=migration_id,
        entities_migrated=0,
        entities_failed=0,
        notes="Schema-only migration - no entities migrated",
    )

    return {
        "status": "migrated",
        "from_version": "3.0.0",
        "to_version": target_version,
        "migration_id": migration_id,
    }
