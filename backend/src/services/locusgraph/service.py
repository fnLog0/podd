import asyncio
import json
import uuid
from datetime import datetime, timezone
from functools import partial

# Import LocusGraphClient with fallback to mock
try:
    from locusgraph_client import LocusGraphClient
except ImportError:
    # Fallback to mock if client is not installed
    from src.services.locusgraph_client_mock import LocusGraphClient

    print("⚠️  WARNING: locusgraph_client not found, using mock implementation")

from src.config import settings


class LocusGraphService:
    def __init__(self):
        self.use_mock = settings.USE_LOCUSGRAPH_MOCK

        if self.use_mock:
            print("🧪 Using MOCK LocusGraph service (development mode)")
            # In-memory storage for mock mode
            self._mock_events = []
            return

        if not settings.LOCUSGRAPH_AGENT_SECRET:
            # For development/testing, allow empty but warn
            print("⚠️  WARNING: LOCUSGRAPH_AGENT_SECRET is not set!")
            print("   Set it in .env file or environment variables")

        self.client = LocusGraphClient(
            server_url=settings.LOCUSGRAPH_SERVER_URL,
            agent_secret=settings.LOCUSGRAPH_AGENT_SECRET or "dev_secret_key",
            graph_id=settings.LOCUSGRAPH_GRAPH_ID,
        )
        self.graph_id = settings.LOCUSGRAPH_GRAPH_ID

    async def store_event(
        self,
        event_kind: str,
        payload: dict,
        context_id: str | None = None,
        source: str = "agent",
        related_to: list[str] | None = None,
        extends: list[str] | None = None,
        reinforces: list[str] | None = None,
        contradicts: list[str] | None = None,
        timestamp: str | None = None,
    ) -> dict:
        if self.use_mock:
            event_id = self.new_id()
            event = {
                "event_id": event_id,
                "event_kind": event_kind,
                "payload": payload,
                "context_id": context_id,
                "source": source,
                "related_to": related_to,
                "extends": extends,
                "reinforces": reinforces,
                "contradicts": contradicts,
                "timestamp": timestamp or self.now(),
                "status": "stored",
                "relevance": None,
                "error_message": None,
            }
            self._mock_events.append(event)
            print(
                f"DEBUG MOCK: Stored event with event_id={event_id}, event_kind={event_kind}, context_id={context_id}"
            )
            print(f"DEBUG MOCK: Total events in storage: {len(self._mock_events)}")
            return {
                "event_id": event_id,
                "status": "stored",
                "relevance": None,
                "error_message": None,
            }

        request = {
            "graph_id": self.graph_id,
            "event_kind": event_kind,
            "payload": payload,
            "source": source,
        }
        if context_id:
            request["context_id"] = context_id
        if related_to:
            request["related_to"] = related_to
        if extends:
            request["extends"] = extends
        if reinforces:
            request["reinforces"] = reinforces
        if contradicts:
            request["contradicts"] = contradicts
        if timestamp:
            request["timestamp"] = timestamp

        # Run synchronous SDK call in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self.client.store_event, request)

        return {
            "event_id": response.event_id,
            "status": response.status,
            "relevance": response.relevance,
            "error_message": response.error_message,
        }

    async def retrieve_context(
        self,
        query: str,
        limit: int = 5,
        context_ids: list[str] | None = None,
        context_types: dict | None = None,
    ) -> list:
        if self.use_mock:
            # Filter mock events based on query parameters
            results = self._mock_events
            print(f"DEBUG MOCK: Total events in storage: {len(self._mock_events)}")
            print(f"DEBUG MOCK: Query: '{query}', Context IDs: {context_ids}")

            if context_ids:
                results = [e for e in results if e.get("context_id") in context_ids]

            if context_types:
                for key, value in context_types.items():
                    results = [e for e in results if e.get("event_kind") == key]

            # Enhanced query matching
            if query and query != "*":
                before_filter = len(results)
                query_lower = query.lower()
                # Split query into tokens and match if ANY token is found
                query_tokens = [
                    token.strip() for token in query_lower.split() if token.strip()
                ]
                results = [
                    e
                    for e in results
                    if any(
                        token in str(e.get("event_kind", "")).lower()
                        or token in str(e.get("context_id", "")).lower()
                        or token in str(e.get("payload", {})).lower()
                        for token in query_tokens
                    )
                ]
                print(
                    f"DEBUG MOCK: After query filter: {len(results)} events (from {before_filter})"
                )

            print(f"DEBUG MOCK: Returning {len(results[:limit])} events")
            return results[:limit]

        # Run synchronous SDK call in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            partial(
                self.client.retrieve_memories,
                query=query,
                graph_id=self.graph_id,
                limit=limit,
                context_ids=context_ids,
                context_types=context_types,
            ),
        )

        # Try to parse the memories string as JSON
        try:
            memories = json.loads(result.memories)
            if isinstance(memories, list):
                return memories
            elif isinstance(memories, dict):
                return [memories]
        except (json.JSONDecodeError, TypeError):
            pass

        # If JSON parsing fails, return a list with the raw string
        return [{"memories": result.memories, "items_found": result.items_found}]

    async def generate_insights(
        self,
        task: str,
        locus_query: str | None = None,
        limit: int = 5,
        context_ids: list[str] | None = None,
        context_types: dict | None = None,
    ) -> dict:
        if self.use_mock:
            return {
                "insight": f"Mock insight for: {task}",
                "recommendation": "Mock recommendation based on analysis",
                "confidence": 0.75,
            }

        # Run synchronous SDK call in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            partial(
                self.client.generate_insights,
                task=task,
                graph_id=self.graph_id,
                locus_query=locus_query,
                limit=limit,
                context_ids=context_ids,
                context_types=context_types,
            ),
        )

        return {
            "insight": result.insight,
            "recommendation": result.recommendation,
            "confidence": result.confidence,
        }

    @staticmethod
    def new_id() -> str:
        return uuid.uuid4().hex[:12]

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()


locusgraph_service = LocusGraphService()
