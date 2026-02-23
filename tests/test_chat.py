import pytest
import pytest_asyncio
from httpx import AsyncClient
from src.models import User


@pytest.mark.asyncio
async def test_chat_food_tracking(client: AsyncClient, test_user: User):
    """Test chat endpoint with food tracking intent."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "I ate roti and chawal for lunch"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    assert data["intent"] == "food_tracking"


@pytest.mark.asyncio
async def test_chat_medication(client: AsyncClient, test_user: User):
    """Test chat endpoint with medication intent."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "I took my medicine today"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["intent"] == "medication"


@pytest.mark.asyncio
async def test_chat_health_query(client: AsyncClient, test_user: User):
    """Test chat endpoint with health query intent."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "What is my blood pressure?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["intent"] == "health_query"


@pytest.mark.asyncio
async def test_chat_recommendation(client: AsyncClient, test_user: User):
    """Test chat endpoint with recommendation intent."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "What should I eat for breakfast?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["intent"] == "recommendation"


@pytest.mark.asyncio
async def test_chat_general(client: AsyncClient, test_user: User):
    """Test chat endpoint with general chat intent."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Hello, how are you?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["intent"] == "general_chat"


@pytest.mark.asyncio
async def test_chat_hindi_locale(client: AsyncClient, test_user: User):
    """Test chat endpoint with Hindi locale."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Maine aaj khana khaya", "locale": "hi-IN"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["locale"] == "hi-IN"


@pytest.mark.asyncio
async def test_chat_voice_channel(client: AsyncClient, test_user: User):
    """Test chat endpoint with voice channel."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "I had breakfast", "channel": "voice"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data


@pytest.mark.asyncio
async def test_chat_empty_message(client: AsyncClient, test_user: User):
    """Test chat endpoint with empty message (should fail validation)."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": ""},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_chat_history(client: AsyncClient, test_user: User):
    """Test chat history endpoint."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # First, send a few messages to create history
    await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "I ate lunch"},
    )

    await client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "I feel good"},
    )

    # Get history
    response = await client.get(
        "/api/chat/history",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert "total_count" in data
    assert isinstance(data["conversations"], list)
