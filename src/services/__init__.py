"""Services module for LocusGraph-centric functionality.

This module provides core services for working with LocusGraph,
including temporal utilities, validation, caching, batch operations,
and schema migrations.
"""

from .locusgraph import (
    LocusGraphService,
    locusgraph_service,
    LocusGraphCache,
    MeditationSessionCache,
    AppointmentCache,
    EmergencyContactCache,
)
from .temporal import (
    TemporalContext,
    TemporalScheduler,
    get_temporal_contexts,
)
from .validation import (
    ValidationMemory,
    URLValidator,
    PhoneValidator,
    DuplicateDetector,
    AppointmentDuplicateDetector,
    EmergencyContactDuplicateDetector,
    MeditationSessionDuplicateDetector,
)
from .batch import (
    BatchOperation,
    BatchAppointmentCreator,
    BatchEmergencyContactCreator,
    BatchMeditationSessionCreator,
)
from .migration import (
    SchemaMigrationManager,
    ensure_schema_version,
)

__all__ = [
    # LocusGraph
    "LocusGraphService",
    "locusgraph_service",
    "LocusGraphCache",
    "MeditationSessionCache",
    "AppointmentCache",
    "EmergencyContactCache",
    # Temporal
    "TemporalContext",
    "TemporalScheduler",
    "get_temporal_contexts",
    # Validation
    "ValidationMemory",
    "URLValidator",
    "PhoneValidator",
    "DuplicateDetector",
    "AppointmentDuplicateDetector",
    "EmergencyContactDuplicateDetector",
    "MeditationSessionDuplicateDetector",
    # Batch
    "BatchOperation",
    "BatchAppointmentCreator",
    "BatchEmergencyContactCreator",
    "BatchMeditationSessionCreator",
    # Migration
    "SchemaMigrationManager",
    "ensure_schema_version",
]
