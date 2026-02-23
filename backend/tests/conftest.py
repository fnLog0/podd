import pytest
import pytest_asyncio
import os
import uuid as uuid_lib
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from src.database import async_session, create_tables
from src.models import RefreshToken, User


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create database tables at the start of the test session."""
    await create_tables()
    yield


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ["JWT_SECRET"] = "test-secret-key-32-bytes-long-!"
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["LOCUSGRAPH_AGENT_SECRET"] = "test-agent-secret-for-testing"
    os.environ["LOCUSGRAPH_SERVER_URL"] = "http://localhost:8000"  # Dummy URL
    os.environ["LOCUSGRAPH_GRAPH_ID"] = "test-graph-id"
    yield
    del os.environ["JWT_SECRET"]
    del os.environ["LOCUSGRAPH_AGENT_SECRET"]
    del os.environ["LOCUSGRAPH_SERVER_URL"]
    del os.environ["LOCUSGRAPH_GRAPH_ID"]


@pytest.fixture(scope="session")
def app():
    from src.main import app

    return app


@pytest_asyncio.fixture(scope="function")
async def clean_db():
    async with async_session() as session:
        await session.execute(delete(RefreshToken))
        await session.execute(delete(User))
        await session.commit()
    yield
    async with async_session() as session:
        await session.execute(delete(RefreshToken))
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture(scope="function")
def mock_locusgraph_service():
    """Mock LocusGraph service methods."""
    # Storage to track events created during test
    event_storage = []
    id_counter = 0

    # Create a mock object
    mock_service = Mock()

    # Mock store_event to track events in memory
    async def mock_store_event(*args, **kwargs):
        nonlocal id_counter
        id_counter += 1
        event_id = kwargs.get("context_id") or (
            args[1].get("context_id") if len(args) > 1 else None
        )

        # Generate context_id if not provided
        if event_id is None:
            context_id = f"food:test-{id_counter}"
        else:
            context_id = event_id

        event_kind = kwargs.get("event_kind") or (args[0] if args else "observation")
        payload = kwargs.get("payload") or {}

        stored_event = {
            "event_id": context_id,
            "status": "recorded",
            "relevance": "medium",
            "context_id": context_id,
            "event_kind": event_kind,
            "payload": payload,
            "timestamp": "2025-01-01T00:00:00Z",
            "id": context_id,
        }
        event_storage.append(stored_event)
        return stored_event

    # Mock retrieve_context to return stored events
    async def mock_retrieve_context(*args, **kwargs):
        query = kwargs.get("query", "").lower()
        context_ids = kwargs.get("context_ids")
        limit = kwargs.get("limit", 10)

        if context_ids:
            # Return specific event by context_id
            for event in event_storage:
                if event.get("context_id") in context_ids:
                    return [event]
            return []

        # Filter by query
        filtered_events = []
        for event in event_storage:
            payload = event.get("payload", {})
            # Check if query matches user_id or other criteria
            user_id = str(payload.get("user_id", ""))
            if user_id in query or query in str(payload.values()).lower():
                filtered_events.append(event)
                if len(filtered_events) >= limit:
                    break

        return filtered_events

    # Mock methods
    mock_service.store_event = mock_store_event
    mock_service.retrieve_context = mock_retrieve_context

    mock_service.generate_insights = AsyncMock(
        return_value={
            "insight": "test insight",
            "recommendation": "test recommendation",
            "confidence": "high",
        }
    )

    # Mock static methods
    mock_service.new_id = lambda: f"test-{id_counter + 1}"
    mock_service.now = lambda: "2025-01-01T00:00:00Z"

    # Patch the service in routes that import it at module level
    with (
        patch("src.routes.health.food_log.locusgraph_service", mock_service),
        patch("src.routes.health.vitals.locusgraph_service", mock_service),
        patch("src.routes.medication.medication.locusgraph_service", mock_service),
        patch(
            "src.routes.medication.medication_schedule.locusgraph_service", mock_service
        ),
        patch("src.routes.profile.profile.locusgraph_service", mock_service),
        patch("src.routes.health.health.locusgraph_service", mock_service),
    ):
        yield mock_service


@pytest_asyncio.fixture(scope="function")
async def client(clean_db, mock_locusgraph_service, app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session():
    """Database session fixture for creating test data."""
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user for authentication tests."""
    import bcrypt

    password_hash = bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode("utf-8")
    user = User(
        id=str(uuid_lib.uuid4()),
        email="test@example.com",
        password_hash=password_hash,
        name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
