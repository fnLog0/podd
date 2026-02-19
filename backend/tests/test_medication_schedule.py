"""Tests for MedicationSchedule CRUD operations."""

import pytest
from httpx import AsyncClient

from src.models.user import User


@pytest.mark.asyncio
async def test_create_medication_schedule(client: AsyncClient, test_user: User):
    """Test creating a new medication schedule."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # First create a medication
    med_response = await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Vitamin D",
            "dosage": "1000 IU",
            "frequency": "once daily",
        },
    )
    medication_id = med_response.json()["id"]

    # Create a schedule for the medication
    response = await client.post(
        "/api/medication-schedules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medication_id": medication_id,
            "time_of_day": "08:00",
            "days_of_week": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["medication_id"] == medication_id
    assert data["time_of_day"] == "08:00"
    assert len(data["days_of_week"]) == 7
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_medication_schedules(client: AsyncClient, test_user: User):
    """Test retrieving medication schedules."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create a medication and schedule
    med_response = await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Med",
            "dosage": "10mg",
            "frequency": "once daily",
        },
    )
    medication_id = med_response.json()["id"]

    await client.post(
        "/api/medication-schedules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medication_id": medication_id,
            "time_of_day": "12:00",
            "days_of_week": ["mon", "wed", "fri"],
        },
    )

    # Get schedules
    response = await client.get(
        "/api/medication-schedules",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_medication_schedules_filter_by_medication(client: AsyncClient, test_user: User):
    """Test retrieving schedules filtered by medication ID."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create two medications
    med1_response = await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Medication 1",
            "dosage": "10mg",
            "frequency": "once daily",
        },
    )
    med1_id = med1_response.json()["id"]

    med2_response = await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Medication 2",
            "dosage": "5ml",
            "frequency": "twice daily",
        },
    )
    med2_id = med2_response.json()["id"]

    # Create schedules for both
    await client.post(
        "/api/medication-schedules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medication_id": med1_id,
            "time_of_day": "08:00",
            "days_of_week": ["mon"],
        },
    )
    await client.post(
        "/api/medication-schedules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medication_id": med2_id,
            "time_of_day": "12:00",
            "days_of_week": ["tue"],
        },
    )

    # Get schedules for first medication only
    response = await client.get(
        f"/api/medication-schedules?medication_id={med1_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert all(schedule["medication_id"] == med1_id for schedule in data)


@pytest.mark.asyncio
async def test_update_medication_schedule(client: AsyncClient, test_user: User):
    """Test updating a medication schedule."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create a medication and schedule
    med_response = await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Med",
            "dosage": "10mg",
            "frequency": "once daily",
        },
    )
    medication_id = med_response.json()["id"]

    create_response = await client.post(
        "/api/medication-schedules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medication_id": medication_id,
            "time_of_day": "08:00",
            "days_of_week": ["mon", "tue", "wed"],
        },
    )
    schedule_id = create_response.json()["id"]

    # Update the schedule
    response = await client.put(
        f"/api/medication-schedules/{schedule_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "time_of_day": "09:00",
            "days_of_week": ["mon", "tue", "wed", "thu", "fri"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["time_of_day"] == "09:00"
    assert len(data["days_of_week"]) == 5


@pytest.mark.asyncio
async def test_delete_medication_schedule(client: AsyncClient, test_user: User):
    """Test deleting a medication schedule."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create a medication and schedule
    med_response = await client.post(
        "/api/medication",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Med",
            "dosage": "10mg",
            "frequency": "once daily",
        },
    )
    medication_id = med_response.json()["id"]

    create_response = await client.post(
        "/api/medication-schedules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medication_id": medication_id,
            "time_of_day": "08:00",
            "days_of_week": ["mon"],
        },
    )
    schedule_id = create_response.json()["id"]

    # Delete the schedule
    response = await client.delete(
        f"/api/medication-schedules/{schedule_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert response.text == ""


@pytest.mark.asyncio
async def test_medication_schedule_without_token(client: AsyncClient):
    """Test accessing medication schedules without authentication."""
    response = await client.get("/api/medication-schedules")
    assert response.status_code == 401
