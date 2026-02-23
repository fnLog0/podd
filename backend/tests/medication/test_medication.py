"""Tests for Medication CRUD operations."""

import pytest
from httpx import AsyncClient

from src.models.user import User


@pytest.mark.asyncio
async def test_create_medication(client: AsyncClient, test_user: User):
    """Test creating a new medication."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Aspirin",
            "dosage": "100mg",
            "frequency": "once daily",
            "instructions": "Take with food",
            "active": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Aspirin"
    assert data["dosage"] == "100mg"
    assert data["frequency"] == "once daily"
    assert data["instructions"] == "Take with food"
    assert data["active"] is True
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_medications(client: AsyncClient, test_user: User):
    """Test retrieving all medications."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Medication 1",
            "dosage": "10mg",
            "frequency": "twice daily",
        },
    )
    await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Medication 2",
            "dosage": "5ml",
            "frequency": "once daily",
            "active": False,
        },
    )

    response = await client.get(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_medications_active_only(client: AsyncClient, test_user: User):
    """Test retrieving only active medications."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Active Med",
            "dosage": "10mg",
            "frequency": "once daily",
            "active": True,
        },
    )
    await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Inactive Med",
            "dosage": "5ml",
            "frequency": "once daily",
            "active": False,
        },
    )

    response = await client.get(
        "/api/medication?active_only=true",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert all(med["active"] is True for med in data)
    assert not any(med["name"] == "Inactive Med" for med in data)


@pytest.mark.asyncio
async def test_update_medication(client: AsyncClient, test_user: User):
    """Test updating a medication."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    create_response = await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Ibuprofen",
            "dosage": "200mg",
            "frequency": "twice daily",
        },
    )
    medication_id = create_response.json()["id"]

    response = await client.put(
        f"/api/medication/{medication_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "dosage": "400mg",
            "frequency": "once daily",
            "active": False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["dosage"] == "400mg"
    assert data["frequency"] == "once daily"
    assert data["active"] is False


@pytest.mark.asyncio
async def test_delete_medication(client: AsyncClient, test_user: User):
    """Test deleting a medication."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    create_response = await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "To delete",
            "dosage": "10mg",
            "frequency": "once daily",
        },
    )
    medication_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/medication/{medication_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert response.text == ""


@pytest.mark.asyncio
async def test_medication_without_token(client: AsyncClient):
    """Test accessing medications without authentication."""
    response = await client.get("/api/medication")
    assert response.status_code == 401
