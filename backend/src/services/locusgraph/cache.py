"""LocusGraph caching layer using LocusGraph contexts as cache storage.

This module provides a caching mechanism that stores cache entries within
LocusGraph itself, eliminating the need for external cache servers.
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Optional, TypeVar
import hashlib
import json

from .service import locusgraph_service

T = TypeVar("T")


class LocusGraphCache:
    """Cache implementation using LocusGraph as the cache backend."""

    CACHE_CONTEXT_PREFIX = "cache_entry"
    CACHE_EVENT_KIND = "cache.set"
    DEFAULT_TTL_SECONDS = 3600  # 1 hour default

    @staticmethod
    def _generate_cache_key(
        key: str,
        key_params: Optional[dict] = None,
    ) -> str:
        """Generate a cache key from a base key and optional parameters.

        Args:
            key: Base cache key
            key_params: Optional parameters to include in the key

        Returns:
            Generated cache key string
        """
        if not key_params:
            return f"cache:{key}"

        # Sort parameters for consistency
        sorted_params = json.dumps(key_params, sort_keys=True)
        params_hash = hashlib.md5(sorted_params.encode()).hexdigest()[:8]

        return f"cache:{key}:{params_hash}"

    @staticmethod
    def _get_cache_context(cache_key: str) -> str:
        """Generate a context ID for a cache entry.

        Args:
            cache_key: Cache key

        Returns:
            Context ID
        """
        key_hash = hashlib.md5(cache_key.encode()).hexdigest()[:12]
        return f"{LocusGraphCache.CACHE_CONTEXT_PREFIX}:{key_hash}"

    @staticmethod
    async def get(
        key: str,
        key_params: Optional[dict] = None,
    ) -> Optional[Any]:
        """Retrieve a value from cache if it exists and is not expired.

        Args:
            key: Cache key
            key_params: Optional parameters that were used when setting the cache

        Returns:
            Cached value if found and valid, None otherwise
        """
        cache_key = LocusGraphCache._generate_cache_key(key, key_params)
        context_id = LocusGraphCache._get_cache_context(cache_key)

        memories = await locusgraph_service.retrieve_context(
            query=cache_key,
            context_ids=[context_id],
            limit=1,
        )

        if not memories:
            return None

        memory = memories[0]
        payload = memory.get("payload", {})

        # Check if cache has expired
        expires_at = payload.get("expires_at")
        if expires_at:
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)

            if datetime.now(timezone.utc) > expires_at:
                # Cache has expired
                await LocusGraphCache._mark_expired(context_id)
                return None

        # Return cached value
        return payload.get("value")

    @staticmethod
    async def set(
        key: str,
        value: Any,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        key_params: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Store a value in cache with a TTL.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl_seconds: Time to live in seconds
            key_params: Optional parameters to include in cache key
            metadata: Optional metadata to store with the cache entry

        Returns:
            Context ID of the cache entry
        """
        cache_key = LocusGraphCache._generate_cache_key(key, key_params)
        context_id = LocusGraphCache._get_cache_context(cache_key)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

        payload = {
            "cache_key": cache_key,
            "value": value,
            "expires_at": expires_at.isoformat(),
            "ttl_seconds": ttl_seconds,
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

        await locusgraph_service.store_event(
            event_kind=LocusGraphCache.CACHE_EVENT_KIND,
            context_id=context_id,
            payload=payload,
            source="cache",
        )

        return context_id

    @staticmethod
    async def invalidate(
        key: str,
        key_params: Optional[dict] = None,
    ) -> None:
        """Invalidate a cache entry.

        Args:
            key: Cache key
            key_params: Optional parameters
        """
        cache_key = LocusGraphCache._generate_cache_key(key, key_params)
        context_id = LocusGraphCache._get_cache_context(cache_key)

        await LocusGraphCache._mark_expired(context_id)

    @staticmethod
    async def invalidate_pattern(
        key_pattern: str,
    ) -> int:
        """Invalidate all cache entries matching a pattern.

        Args:
            key_pattern: Pattern to match (e.g., "meditation_sessions:*")

        Returns:
            Number of cache entries invalidated
        """
        memories = await locusgraph_service.retrieve_context(
            query=f"cache entries {key_pattern}",
            limit=100,
        )

        invalidated_count = 0
        for memory in memories:
            context_id = memory.get("context_id", "")
            if context_id.startswith(LocusGraphCache.CACHE_CONTEXT_PREFIX):
                await LocusGraphCache._mark_expired(context_id)
                invalidated_count += 1

        return invalidated_count

    @staticmethod
    async def _mark_expired(context_id: str) -> None:
        """Mark a cache entry as expired.

        Args:
            context_id: Context ID of the cache entry
        """
        await locusgraph_service.store_event(
            event_kind="cache.expired",
            context_id=f"{context_id}:expired",
            payload={
                "expired_at": datetime.now(timezone.utc).isoformat(),
                "status": "expired",
            },
            extends=[context_id],
            source="cache",
        )

    @staticmethod
    async def get_or_set(
        key: str,
        fetch_func: callable,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        key_params: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> Any:
        """Get a value from cache, or fetch and cache if not present.

        Args:
            key: Cache key
            fetch_func: Function to call to fetch the value if not in cache
            ttl_seconds: Time to live in seconds
            key_params: Optional parameters for cache key
            metadata: Optional metadata to store with cache entry

        Returns:
            Cached or fetched value
        """
        # Try to get from cache
        cached = await LocusGraphCache.get(key, key_params)

        if cached is not None:
            return cached

        # Not in cache, fetch value
        value = await fetch_func()

        # Store in cache
        await LocusGraphCache.set(
            key=key,
            value=value,
            ttl_seconds=ttl_seconds,
            key_params=key_params,
            metadata=metadata,
        )

        return value

    @staticmethod
    async def clear_expired() -> int:
        """Clear all expired cache entries.

        Returns:
            Number of expired entries cleared
        """
        # This is a maintenance operation - in production you'd want a cron job
        memories = await locusgraph_service.retrieve_context(
            query="expired cache entries",
            limit=1000,
        )

        # In a real implementation, you might archive or truly delete these
        # For now, we'll just count them
        return len(memories)


class MeditationSessionCache:
    """Cache for meditation sessions (static content)."""

    CACHE_KEY = "meditation_sessions"
    DEFAULT_TTL = 86400  # 24 hours - sessions rarely change

    @staticmethod
    async def get_sessions(category: Optional[str] = None) -> Optional[list]:
        """Get cached meditation sessions.

        Args:
            category: Optional category filter

        Returns:
            Cached sessions or None
        """
        key_params = {"category": category} if category else None
        return await LocusGraphCache.get(
            key=MeditationSessionCache.CACHE_KEY,
            key_params=key_params,
        )

    @staticmethod
    async def set_sessions(sessions: list, category: Optional[str] = None) -> None:
        """Cache meditation sessions.

        Args:
            sessions: List of session data
            category: Optional category filter
        """
        key_params = {"category": category} if category else None

        await LocusGraphCache.set(
            key=MeditationSessionCache.CACHE_KEY,
            value=sessions,
            ttl_seconds=MeditationSessionCache.DEFAULT_TTL,
            key_params=key_params,
            metadata={"category": category, "count": len(sessions)},
        )

    @staticmethod
    async def invalidate_sessions(category: Optional[str] = None) -> None:
        """Invalidate cached meditation sessions.

        Args:
            category: Optional category to invalidate (None = all)
        """
        if category:
            key_params = {"category": category}
            await LocusGraphCache.invalidate(
                key=MeditationSessionCache.CACHE_KEY,
                key_params=key_params,
            )
        else:
            await LocusGraphCache.invalidate_pattern(
                key_pattern=f"{MeditationSessionCache.CACHE_KEY}:*",
            )


class AppointmentCache:
    """Cache for user appointments (user-specific)."""

    CACHE_KEY = "user_appointments"
    DEFAULT_TTL = 3600  # 1 hour

    @staticmethod
    async def get_appointments(
        user_id: str,
        query_type: Optional[str] = None,
    ) -> Optional[list]:
        """Get cached appointments for a user.

        Args:
            user_id: User ID
            query_type: Optional query type ('upcoming', 'past')

        Returns:
            Cached appointments or None
        """
        key_params = {"user_id": user_id, "query_type": query_type}
        return await LocusGraphCache.get(
            key=AppointmentCache.CACHE_KEY,
            key_params=key_params,
        )

    @staticmethod
    async def set_appointments(
        user_id: str,
        appointments: list,
        query_type: Optional[str] = None,
    ) -> None:
        """Cache appointments for a user.

        Args:
            user_id: User ID
            appointments: List of appointment data
            query_type: Optional query type
        """
        key_params = {"user_id": user_id, "query_type": query_type}

        await LocusGraphCache.set(
            key=AppointmentCache.CACHE_KEY,
            value=appointments,
            ttl_seconds=AppointmentCache.DEFAULT_TTL,
            key_params=key_params,
            metadata={
                "user_id": user_id,
                "query_type": query_type,
                "count": len(appointments),
            },
        )

    @staticmethod
    async def invalidate_user_appointments(user_id: str) -> None:
        """Invalidate all cached appointments for a user.

        Args:
            user_id: User ID
        """
        await LocusGraphCache.invalidate_pattern(
            key_pattern=f"{AppointmentCache.CACHE_KEY}:user_{user_id}:*",
        )


class EmergencyContactCache:
    """Cache for emergency contacts (user-specific)."""

    CACHE_KEY = "user_emergency_contacts"
    DEFAULT_TTL = 3600  # 1 hour

    @staticmethod
    async def get_contacts(user_id: str) -> Optional[list]:
        """Get cached emergency contacts for a user.

        Args:
            user_id: User ID

        Returns:
            Cached contacts or None
        """
        key_params = {"user_id": user_id}
        return await LocusGraphCache.get(
            key=EmergencyContactCache.CACHE_KEY,
            key_params=key_params,
        )

    @staticmethod
    async def set_contacts(
        user_id: str,
        contacts: list,
    ) -> None:
        """Cache emergency contacts for a user.

        Args:
            user_id: User ID
            contacts: List of contact data
        """
        key_params = {"user_id": user_id}

        await LocusGraphCache.set(
            key=EmergencyContactCache.CACHE_KEY,
            value=contacts,
            ttl_seconds=EmergencyContactCache.DEFAULT_TTL,
            key_params=key_params,
            metadata={"user_id": user_id, "count": len(contacts)},
        )

    @staticmethod
    async def invalidate_user_contacts(user_id: str) -> None:
        """Invalidate cached emergency contacts for a user.

        Args:
            user_id: User ID
        """
        await LocusGraphCache.invalidate_pattern(
            key_pattern=f"{EmergencyContactCache.CACHE_KEY}:user_{user_id}:*",
        )
