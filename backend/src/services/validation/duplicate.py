"""LocusGraph duplicate detection utilities.

This module provides utilities for detecting duplicate or similar entities
using LocusGraph's semantic search capabilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, TypeVar, Generic

from src.services.locusgraph.service import locusgraph_service

T = TypeVar("T")


class DuplicateDetector(Generic[T]):
    """Generic duplicate detector for entities."""

    @staticmethod
    async def detect_similar(
        entity_type: str,
        user_id: str,
        search_fields: dict,
        similarity_threshold: float = 0.7,
        time_window: Optional[timedelta] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Detect entities similar to the provided fields using semantic search.

        Args:
            entity_type: Type of entity ('appointment', 'meditation', etc.)
            user_id: User ID to search within
            search_fields: Dictionary of fields to search (e.g., {'title': 'Checkup', 'doctor': 'Dr Smith'})
            similarity_threshold: Minimum similarity score (0-1)
            time_window: Optional time window to search within
            limit: Maximum number of results

        Returns:
            List of potentially duplicate entities with similarity scores
        """
        # Build semantic query from search fields
        query_parts = []
        for key, value in search_fields.items():
            if value:
                query_parts.append(f"{key}:{value}")

        query = f"{entity_type} user {user_id} " + " ".join(query_parts)

        memories = await locusgraph_service.retrieve_context(
            query=query,
            limit=limit,
        )

        similar_entities = []
        now = datetime.now(timezone.utc)

        for memory in memories:
            payload = memory.get("payload", {})

            # Skip if not owned by user
            if payload.get("user_id") != str(user_id):
                continue

            # Apply time window filter if provided
            if time_window:
                scheduled_at = payload.get("scheduled_at") or payload.get("created_at")
                if scheduled_at:
                    if isinstance(scheduled_at, str):
                        scheduled_at = datetime.fromisoformat(scheduled_at)
                    if abs(now - scheduled_at) > time_window:
                        continue

            # Calculate similarity score
            similarity = DuplicateDetector._calculate_similarity(search_fields, payload)

            if similarity >= similarity_threshold:
                similar_entities.append(
                    {
                        "memory": memory,
                        "similarity": similarity,
                    }
                )

        # Sort by similarity descending
        similar_entities.sort(key=lambda x: x["similarity"], reverse=True)

        return similar_entities

    @staticmethod
    async def detect_exact_duplicate(
        entity_type: str,
        user_id: str,
        identifier_fields: dict,
    ) -> Optional[dict]:
        """Detect an exact duplicate based on identifier fields.

        Args:
            entity_type: Type of entity
            user_id: User ID to search within
            identifier_fields: Dictionary of fields that uniquely identify an entity

        Returns:
            Duplicate entity if found, None otherwise
        """
        # Build query from identifier fields
        query_parts = []
        for key, value in identifier_fields.items():
            if value:
                query_parts.append(f"{key}:{value}")

        query = f"{entity_type} user {user_id} " + " ".join(query_parts)

        memories = await locusgraph_service.retrieve_context(
            query=query,
            limit=10,
        )

        for memory in memories:
            payload = memory.get("payload", {})

            # Skip if not owned by user
            if payload.get("user_id") != str(user_id):
                continue

            # Check exact match on all identifier fields
            is_exact_match = True
            for key, expected_value in identifier_fields.items():
                actual_value = payload.get(key)
                if str(actual_value) != str(expected_value):
                    is_exact_match = False
                    break

            if is_exact_match:
                return memory

        return None

    @staticmethod
    def _calculate_similarity(search_fields: dict, payload: dict) -> float:
        """Calculate similarity score between search fields and payload.

        Args:
            search_fields: Fields we're searching for
            payload: Payload from memory to compare against

        Returns:
            Similarity score between 0 and 1
        """
        total_score = 0
        total_weight = 0

        # Weight different field types differently
        for key, search_value in search_fields.items():
            if not search_value:
                continue

            payload_value = payload.get(key)
            if not payload_value:
                continue

            # Convert to strings for comparison
            search_str = str(search_value).lower().strip()
            payload_str = str(payload_value).lower().strip()

            # Assign weights based on field importance
            weight = 1.0
            if key in ("title", "name", "doctor_name"):
                weight = 2.0
            elif key in ("scheduled_at", "time"):
                weight = 3.0
            elif key in ("location", "phone"):
                weight = 1.5

            # Calculate similarity based on field type
            if key in ("scheduled_at", "time", "created_at"):
                # Time-based similarity
                similarity = DuplicateDetector._time_similarity(search_str, payload_str)
            elif key in ("phone", "email"):
                # Exact match or very similar
                similarity = 1.0 if search_str == payload_str else 0.0
            else:
                # Text-based similarity (fuzzy matching)
                similarity = DuplicateDetector._text_similarity(search_str, payload_str)

            total_score += similarity * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return total_score / total_weight

    @staticmethod
    def _text_similarity(str1: str, str2: str) -> float:
        """Calculate text similarity using a simple algorithm.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score between 0 and 1
        """
        # Exact match
        if str1 == str2:
            return 1.0

        # Check if one contains the other
        if str1 in str2 or str2 in str1:
            return 0.8

        # Simple word overlap
        words1 = set(str1.split())
        words2 = set(str2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    @staticmethod
    def _time_similarity(str1: str, str2: str) -> float:
        """Calculate time similarity between two time strings.

        Args:
            str1: First time string (ISO format or similar)
            str2: Second time string (ISO format or similar)

        Returns:
            Similarity score between 0 and 1
        """
        try:
            dt1 = datetime.fromisoformat(str1) if isinstance(str1, str) else str1
            dt2 = datetime.fromisoformat(str2) if isinstance(str2, str) else str2
        except (ValueError, TypeError):
            return 0.0

        # Difference in minutes
        diff_minutes = abs((dt1 - dt2).total_seconds()) / 60

        # Similarity decreases with time difference
        if diff_minutes < 5:
            return 1.0
        elif diff_minutes < 15:
            return 0.9
        elif diff_minutes < 30:
            return 0.7
        elif diff_minutes < 60:
            return 0.5
        elif diff_minutes < 120:
            return 0.3
        elif diff_minutes < 1440:  # 24 hours
            return 0.1
        else:
            return 0.0


class AppointmentDuplicateDetector:
    """Specialized duplicate detector for appointments."""

    @staticmethod
    async def detect_duplicates(
        title: str,
        scheduled_at: datetime,
        doctor_name: Optional[str] = None,
        location: Optional[str] = None,
        user_id: str = None,
        time_window_minutes: int = 30,
    ) -> Optional[dict]:
        """Detect duplicate or very similar appointments.

        Args:
            title: Appointment title
            scheduled_at: Scheduled time
            doctor_name: Optional doctor name
            location: Optional location
            user_id: User ID
            time_window_minutes: Time window in minutes to check for duplicates

        Returns:
            Duplicate appointment if found, None otherwise
        """
        search_fields = {
            "title": title,
            "scheduled_at": scheduled_at.isoformat(),
        }

        if doctor_name:
            search_fields["doctor_name"] = doctor_name
        if location:
            search_fields["location"] = location

        similar = await DuplicateDetector.detect_similar(
            entity_type="appointment",
            user_id=user_id,
            search_fields=search_fields,
            similarity_threshold=0.8,
            time_window=timedelta(minutes=time_window_minutes),
            limit=10,
        )

        # Return the most similar if it's very similar (>0.9)
        if similar and similar[0]["similarity"] > 0.9:
            return similar[0]["memory"]

        return None


class EmergencyContactDuplicateDetector:
    """Specialized duplicate detector for emergency contacts."""

    @staticmethod
    async def detect_duplicate(
        phone: str,
        user_id: str,
        name: Optional[str] = None,
    ) -> Optional[dict]:
        """Detect duplicate emergency contact by phone number.

        Args:
            phone: Phone number
            user_id: User ID
            name: Optional name for additional matching

        Returns:
            Duplicate contact if found, None otherwise
        """
        # Exact match by phone is the primary identifier
        duplicate = await DuplicateDetector.detect_exact_duplicate(
            entity_type="emergency_contact",
            user_id=user_id,
            identifier_fields={"phone": phone},
        )

        if duplicate:
            return duplicate

        # Also check by name if provided
        if name:
            similar = await DuplicateDetector.detect_similar(
                entity_type="emergency_contact",
                user_id=user_id,
                search_fields={"name": name},
                similarity_threshold=0.9,
                limit=10,
            )

            if similar and similar[0]["similarity"] > 0.95:
                return similar[0]["memory"]

        return None

    @staticmethod
    async def check_primary_contact_exists(user_id: str) -> Optional[dict]:
        """Check if user already has a primary emergency contact.

        Args:
            user_id: User ID to check

        Returns:
            Primary contact if found, None otherwise
        """
        memories = await locusgraph_service.retrieve_context(
            query=f"emergency contact primary user {user_id}",
            limit=10,
        )

        for memory in memories:
            payload = memory.get("payload", {})
            if payload.get("user_id") == str(user_id) and payload.get("is_primary"):
                return memory

        return None


class MeditationSessionDuplicateDetector:
    """Specialized duplicate detector for meditation sessions."""

    @staticmethod
    async def detect_duplicate(
        title: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> Optional[dict]:
        """Detect duplicate meditation session by title and category.

        Args:
            title: Session title
            category: Optional category
            limit: Maximum results to check

        Returns:
            Duplicate session if found, None otherwise
        """
        search_fields = {"title": title}
        if category:
            search_fields["category"] = category

        similar = await DuplicateDetector.detect_similar(
            entity_type="meditation_session",
            user_id="system",  # Sessions are global, not user-specific
            search_fields=search_fields,
            similarity_threshold=0.95,
            limit=limit,
        )

        # Return exact or near-exact match
        if similar and similar[0]["similarity"] >= 0.95:
            return similar[0]["memory"]

        return None
