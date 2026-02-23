"""Validation utilities for learning from failures and detecting duplicates."""

from .memory import ValidationMemory, URLValidator, PhoneValidator
from .duplicate import (
    DuplicateDetector,
    AppointmentDuplicateDetector,
    EmergencyContactDuplicateDetector,
    MeditationSessionDuplicateDetector,
)

__all__ = [
    "ValidationMemory",
    "URLValidator",
    "PhoneValidator",
    "DuplicateDetector",
    "AppointmentDuplicateDetector",
    "EmergencyContactDuplicateDetector",
    "MeditationSessionDuplicateDetector",
]
