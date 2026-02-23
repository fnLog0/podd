"""Mock LocusGraphClient for development when USE_LOCUSGRAPH_MOCK is enabled."""


class LocusGraphClient:
    """Mock LocusGraph client for development/testing."""

    def __init__(self, server_url: str, agent_secret: str, graph_id: str):
        self.server_url = server_url
        self.agent_secret = agent_secret
        self.graph_id = graph_id

    def store_event(self, request: dict) -> dict:
        """Mock store_event method."""
        import uuid

        event_id = str(uuid.uuid4())
        return {
            "event_id": event_id,
            "status": "stored",
            "relevance": None,
            "error_message": None,
        }

    def retrieve_context(self, params: dict) -> list:
        """Mock retrieve_context method."""
        return []

    def generate_insights(self, params: dict) -> dict:
        """Mock generate_insights method."""
        return {
            "insights": [],
            "summary": "Mock insights generated",
        }
