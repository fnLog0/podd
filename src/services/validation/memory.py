"""LocusGraph validation memory system for learning from validation failures.

This module provides utilities for storing and retrieving validation patterns,
allowing the system to remember and prevent recurring errors.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from src.schemas.events import EventKind
from src.services.locusgraph.service import locusgraph_service


class ValidationMemory:
    """Manages validation failures and learned patterns in LocusGraph."""

    VALIDATION_FAILED_EVENT_KIND = "validation.failed"
    VALIDATION_PASSED_EVENT_KIND = "validation.passed"
    PATTERN_CONTEXT_PREFIX = "validation_pattern"

    @staticmethod
    async def remember_failure(
        error_type: str,
        value: str,
        error_message: str,
        user_id: Optional[str] = None,
        additional_context: Optional[dict] = None,
    ) -> str:
        """Store a validation failure for future reference.

        Args:
            error_type: Type of error (e.g., 'invalid_url', 'duplicate_value', 'format_error')
            value: The value that failed validation
            error_message: Human-readable error message
            user_id: Optional user ID (None means this is a global failure)
            additional_context: Additional context about the failure

        Returns:
            Context ID of the stored failure
        """
        # Extract pattern from value
        pattern = ValidationMemory._extract_pattern(value, error_type)

        payload = {
            "error_type": error_type,
            "value": value,
            "pattern": pattern,
            "error_message": error_message,
            "user_id": user_id,
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "additional_context": additional_context or {},
        }

        # Store with pattern-based context ID
        pattern_context = (
            f"{ValidationMemory.PATTERN_CONTEXT_PREFIX}:{error_type}:{pattern}"
        )

        # Check if this pattern already failed recently
        existing = await locusgraph_service.retrieve_context(
            query=f"validation failed pattern {pattern}",
            context_ids=[pattern_context],
            limit=1,
        )

        if existing:
            # Extend existing context instead of creating new one
            await locusgraph_service.store_event(
                event_kind=ValidationMemory.VALIDATION_FAILED_EVENT_KIND,
                context_id=pattern_context,
                payload=payload,
                reinforces=[pattern_context],
                source="validator",
            )
        else:
            # New pattern failure
            await locusgraph_service.store_event(
                event_kind=ValidationMemory.VALIDATION_FAILED_EVENT_KIND,
                context_id=pattern_context,
                payload=payload,
                source="validator",
            )

        return pattern_context

    @staticmethod
    async def remember_success(
        error_type: str,
        value: str,
        user_id: Optional[str] = None,
        additional_context: Optional[dict] = None,
    ) -> str:
        """Store a validation success to potentially override learned failures.

        Args:
            error_type: Type of validation (e.g., 'url', 'phone', 'email')
            value: The value that passed validation
            user_id: Optional user ID
            additional_context: Additional context about the success

        Returns:
            Context ID of the stored success
        """
        pattern = ValidationMemory._extract_pattern(value, error_type)

        payload = {
            "validation_type": error_type,
            "value": value,
            "pattern": pattern,
            "user_id": user_id,
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "additional_context": additional_context or {},
        }

        pattern_context = (
            f"{ValidationMemory.PATTERN_CONTEXT_PREFIX}:{error_type}:{pattern}"
        )

        await locusgraph_service.store_event(
            event_kind=ValidationMemory.VALIDATION_PASSED_EVENT_KIND,
            context_id=pattern_context,
            payload=payload,
            contradicts=[
                f"{ValidationMemory.VALIDATION_FAILED_EVENT_KIND}:{pattern_context}"
            ],
            source="validator",
        )

        return pattern_context

    @staticmethod
    async def check_known_failures(
        value: str,
        error_type: str,
        user_id: Optional[str] = None,
        tolerance_window_hours: int = 24,
    ) -> Optional[dict]:
        """Check if a value matches a known failure pattern.

        Args:
            value: Value to check
            error_type: Type of validation to check
            user_id: Optional user ID for user-specific failures
            tolerance_window_hours: How recent the failure must be (default: 24 hours)

        Returns:
            Failure context if found, None otherwise
        """
        pattern = ValidationMemory._extract_pattern(value, error_type)
        pattern_context = (
            f"{ValidationMemory.PATTERN_CONTEXT_PREFIX}:{error_type}:{pattern}"
        )

        query = f"validation failed {error_type} pattern {pattern}"
        if user_id:
            query += f" user {user_id}"

        memories = await locusgraph_service.retrieve_context(
            query=query,
            context_ids=[pattern_context],
            limit=5,
        )

        # Filter by recency
        now = datetime.now(timezone.utc)
        window = timedelta(hours=tolerance_window_hours)

        for memory in memories:
            payload = memory.get("payload", {})
            failed_at = payload.get("failed_at")

            if failed_at:
                if isinstance(failed_at, str):
                    failed_at = datetime.fromisoformat(failed_at)

                # Check if within tolerance window
                if now - failed_at <= window:
                    return memory

        return None

    @staticmethod
    async def get_failure_stats(
        error_type: Optional[str] = None, days: int = 7
    ) -> dict:
        """Get statistics about validation failures.

        Args:
            error_type: Optional error type to filter by
            days: Number of days to look back (default: 7)

        Returns:
            Dictionary with failure statistics
        """
        query = "validation failures"
        if error_type:
            query += f" {error_type}"

        memories = await locusgraph_service.retrieve_context(
            query=query,
            limit=100,
        )

        now = datetime.now(timezone.utc)
        window = timedelta(days=days)

        stats = {
            "total_failures": 0,
            "by_error_type": {},
            "by_pattern": {},
            "recent_failures": 0,
            "most_common_patterns": {},
        }

        for memory in memories:
            payload = memory.get("payload", {})
            failed_at = payload.get("failed_at")

            if failed_at:
                if isinstance(failed_at, str):
                    failed_at = datetime.fromisoformat(failed_at)

                # Filter by time window
                if now - failed_at <= window:
                    stats["total_failures"] += 1
                    stats["recent_failures"] += 1

                    # Group by error type
                    et = payload.get("error_type", "unknown")
                    stats["by_error_type"][et] = stats["by_error_type"].get(et, 0) + 1

                    # Group by pattern
                    pattern = payload.get("pattern", "unknown")
                    stats["by_pattern"][pattern] = (
                        stats["by_pattern"].get(pattern, 0) + 1
                    )

        # Find most common patterns
        sorted_patterns = sorted(
            stats["by_pattern"].items(), key=lambda x: x[1], reverse=True
        )
        stats["most_common_patterns"] = dict(sorted_patterns[:10])

        return stats

    @staticmethod
    def _extract_pattern(value: str, error_type: str) -> str:
        """Extract a pattern from a value for pattern matching.

        Args:
            value: Value to extract pattern from
            error_type: Type of error (helps determine pattern extraction strategy)

        Returns:
            Pattern string
        """
        if not value:
            return "empty"

        value_lower = value.lower().strip()

        # URL patterns
        if "url" in error_type:
            # Extract domain
            if "://" in value_lower:
                domain = value_lower.split("://")[1].split("/")[0]
                return f"domain:{domain}"
            else:
                return f"no_protocol:{value_lower[:50]}"

        # Phone patterns
        if "phone" in error_type:
            # Extract country code and format
            cleaned = re.sub(r"[^0-9+]", "", value)
            if cleaned.startswith("+"):
                return f"international:{cleaned[:4]}"
            else:
                return f"domestic:{cleaned[:3]}"

        # Email patterns
        if "email" in error_type:
            if "@" in value_lower:
                domain = value_lower.split("@")[1]
                return f"domain:{domain}"
            return "no_at_symbol"

        # Duplicate patterns
        if "duplicate" in error_type:
            # Hash the value for consistent pattern
            import hashlib

            return hashlib.md5(value.encode()).hexdigest()[:8]

        # Default: first 50 chars
        return value_lower[:50]


class URLValidator:
    """Specialized validator for URLs that learns from failures."""

    @staticmethod
    async def validate(
        url: str, user_id: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """Validate a URL, checking against known failure patterns.

        Args:
            url: URL to validate
            user_id: Optional user ID for user-specific patterns

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check against known failures
        failure = await ValidationMemory.check_known_failures(
            url, "invalid_url", user_id
        )

        if failure:
            payload = failure.get("payload", {})
            return False, payload.get(
                "error_message", "This URL is known to be invalid"
            )

        # Basic URL validation
        if not url or not isinstance(url, str):
            error = await ValidationMemory.remember_failure(
                error_type="invalid_url",
                value=str(url) if url else "",
                error_message="URL cannot be empty",
                user_id=user_id,
            )
            return False, "URL cannot be empty"

        if not url.startswith(("http://", "https://")):
            error = await ValidationMemory.remember_failure(
                error_type="invalid_url",
                value=url,
                error_message="URL must start with http:// or https://",
                user_id=user_id,
            )
            return False, "URL must start with http:// or https://"

        # In a real implementation, you would make a HEAD request here
        # For now, we'll assume the URL is valid if it has correct format
        return True, None

    @staticmethod
    async def mark_failure(url: str, error_message: str, user_id: Optional[str] = None):
        """Mark a URL as failed (e.g., connection error).

        Args:
            url: URL that failed
            error_message: Error message
            user_id: Optional user ID
        """
        await ValidationMemory.remember_failure(
            error_type="invalid_url",
            value=url,
            error_message=error_message,
            user_id=user_id,
        )

    @staticmethod
    async def mark_success(url: str, user_id: Optional[str] = None):
        """Mark a URL as successfully validated.

        Args:
            url: URL that passed validation
            user_id: Optional user ID
        """
        await ValidationMemory.remember_success(
            error_type="url",
            value=url,
            user_id=user_id,
        )


class PhoneValidator:
    """Specialized validator for phone numbers."""

    @staticmethod
    async def validate(
        phone: str, user_id: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """Validate a phone number, checking against known failure patterns.

        Args:
            phone: Phone number to validate
            user_id: Optional user ID for user-specific patterns

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check against known failures
        failure = await ValidationMemory.check_known_failures(
            phone, "invalid_phone", user_id
        )

        if failure:
            payload = failure.get("payload", {})
            return False, payload.get(
                "error_message", "This phone number format is invalid"
            )

        # Basic phone validation
        if not phone or not isinstance(phone, str):
            error = await ValidationMemory.remember_failure(
                error_type="invalid_phone",
                value=str(phone) if phone else "",
                error_message="Phone number cannot be empty",
                user_id=user_id,
            )
            return False, "Phone number cannot be empty"

        # Remove common formatting
        cleaned = re.sub(r"[^0-9+]", "", phone)

        if len(cleaned) < 10:
            error = await ValidationMemory.remember_failure(
                error_type="invalid_phone",
                value=phone,
                error_message="Phone number must have at least 10 digits",
                user_id=user_id,
            )
            return False, "Phone number must have at least 10 digits"

        return True, None

    @staticmethod
    async def mark_failure(
        phone: str, error_message: str, user_id: Optional[str] = None
    ):
        """Mark a phone number as failed validation.

        Args:
            phone: Phone number that failed
            error_message: Error message
            user_id: Optional user ID
        """
        await ValidationMemory.remember_failure(
            error_type="invalid_phone",
            value=phone,
            error_message=error_message,
            user_id=user_id,
        )

    @staticmethod
    async def mark_success(phone: str, user_id: Optional[str] = None):
        """Mark a phone number as successfully validated.

        Args:
            phone: Phone number that passed validation
            user_id: Optional user ID
        """
        await ValidationMemory.remember_success(
            error_type="phone",
            value=phone,
            user_id=user_id,
        )
