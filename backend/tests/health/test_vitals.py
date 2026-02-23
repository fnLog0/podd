"""Tests for Vitals CRUD operations."""

import pytest
from httpx import AsyncClient

from src.models.user import User


@pytest.mark.asyncio
async def test_create_vitals(client: AsyncClient, test_user: User):
    """Test creating a new vitals entry."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/vitals",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "heart_rate": 72,
            "blood_sugar": 95.0,
            "temperature": 36.6,
            "weight_kg": 70.0,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["blood_pressure_systolic"] == 120
    assert data["blood_pressure_diastolic"] == 80
    assert data["heart_rate"] == 72
    assert data["blood_sugar"] == 95.0
    assert data["temperature"] == 36.6
    assert data["weight_kg"] == 70.0
    assert "id" in data
    assert "user_id" in data
    assert "logged_at" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_vitals_partial(client: AsyncClient, test_user: User):
    """Test creating vitals with only some fields."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/vitals",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "heart_rate": 75,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["heart_rate"] == 75
    assert data["blood_pressure_systolic"] is None


@pytest.mark.asyncio
async def test_get_vitals(client: AsyncClient, test_user: User):
    """Test retrieving vitals entries."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    await client.post(
        "/api/vitals",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "blood_pressure_systolic": 118,
            "blood_pressure_diastolic": 78,
        },
    )

    response = await client.get(
        "/api/vitals",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_update_vitals(client: AsyncClient, test_user: User):
    """Test updating a vitals entry."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    create_response = await client.post(
        "/api/vitals",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "heart_rate": 70,
        },
    )
    vitals_id = create_response.json()["id"]

    response = await client.put(
        f"/api/vitals/{vitals_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "heart_rate": 75,
            "blood_pressure_systolic": 125,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["heart_rate"] == 75
    assert data["blood_pressure_systolic"] == 125


@pytest.mark.asyncio
async def test_delete_vitals(client: AsyncClient, test_user: User):
    """Test deleting a vitals entry."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    create_response = await client.post(
        "/api/vitals",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "heart_rate": 70,
        },
    )
    vitals_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/vitals/{vitals_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert response.text == ""


@pytest.mark.asyncio
async def test_vitals_without_token(client: AsyncClient):
    """Test accessing vitals without authentication."""
    response = await client.get("/api/vitals")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_vitals_invalid_heart_rate(client: AsyncClient, test_user: User):
    """Test creating vitals with invalid heart rate (out of range)."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/vitals",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "heart_rate": 250,  # Out of valid range (30-220)
        },
    )

    assert response.status_code == 422
