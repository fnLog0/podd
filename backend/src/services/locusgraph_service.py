import uuid
from datetime import datetime, timezone

from locusgraph import LocusGraph

from src.config import settings


class LocusGraphService:
    def __init__(self):
        self.client = LocusGraph(api_key=settings.LOCUSGRAPH_API_KEY)
        self.graph_id = settings.LOCUSGRAPH_GRAPH_ID

    def store_event(
        self,
        event_kind: str,
        payload: dict,
        context_id: str | None = None,
        related_to: list[str] | None = None,
        extends: list[str] | None = None,
        reinforces: list[str] | None = None,
        contradicts: list[str] | None = None,
    ) -> dict:
        return self.client.store_event(
            event_kind=event_kind,
            payload=payload,
            context_id=context_id,
            related_to=related_to or [],
            extends=extends or [],
            reinforces=reinforces or [],
            contradicts=contradicts or [],
        )

    def retrieve_context(
        self,
        query: str,
        limit: int = 5,
        context_types: dict | None = None,
        context_ids: list[str] | None = None,
    ) -> list:
        return self.client.retrieve_context(
            query=query,
            limit=limit,
            context_types=context_types,
            context_ids=context_ids,
        )

    def generate_insights(
        self,
        task: str,
        locus_query: str | None = None,
        limit: int = 5,
    ) -> dict:
        return self.client.generate_insights(
            task=task,
            locus_query=locus_query,
            limit=limit,
        )

    @staticmethod
    def new_id() -> str:
        return uuid.uuid4().hex[:12]

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()


locusgraph_service = LocusGraphService()
