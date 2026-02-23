"""Profile API tests: GET, PUT, POST, DELETE profile."""

import pytest
from httpx import AsyncClient

from src.models.user import User


@pytest.mark.asyncio
async def test_get_profile_no_data(client: AsyncClient, test_user: User):
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user.id)
    assert data["date_of_birth"] is None
    assert data["gender"] is None
    assert data["height_cm"] is None
    assert data["weight_kg"] is None
    assert data["blood_type"] is None
    assert data["allergies"] == []
    assert data["medical_conditions"] == []
    assert data["dietary_preferences"] == []


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, test_user: User):
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "date_of_birth": "1990-01-15",
            "gender": "male",
            "height_cm": 175.5,
            "weight_kg": 70.2,
            "blood_type": "A+",
            "allergies": ["peanuts", "shellfish"],
            "medical_conditions": ["hypertension"],
            "dietary_preferences": ["vegetarian"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user.id)
    assert data["date_of_birth"] == "1990-01-15"
    assert data["gender"] == "male"
    assert data["height_cm"] == 175.5
    assert data["weight_kg"] == 70.2
    assert data["blood_type"] == "A+"
    assert data["allergies"] == ["peanuts", "shellfish"]
    assert data["medical_conditions"] == ["hypertension"]
    assert data["dietary_preferences"] == ["vegetarian"]
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_update_profile_partial(client: AsyncClient, test_user: User):
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "gender": "female",
            "height_cm": 160.0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user.id)
    assert data["gender"] == "female"
    assert data["height_cm"] == 160.0
    assert data["weight_kg"] is None


@pytest.mark.asyncio
async def test_update_and_get_profile(client: AsyncClient, test_user: User):
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    update_data = {
        "date_of_birth": "1985-06-20",
        "gender": "male",
        "height_cm": 180.0,
        "weight_kg": 75.0,
        "blood_type": "O+",
    }

    await client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json=update_data,
    )

    response = await client.get(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["date_of_birth"] == update_data["date_of_birth"]
    assert data["gender"] == update_data["gender"]
    assert data["height_cm"] == update_data["height_cm"]
    assert data["weight_kg"] == update_data["weight_kg"]
    assert data["blood_type"] == update_data["blood_type"]


@pytest.mark.asyncio
async def test_update_profile_invalid_blood_type(client: AsyncClient, test_user: User):
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "blood_type": "XZ",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_profile_negative_height(client: AsyncClient, test_user: User):
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "height_cm": -10.0,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_profile_without_token(client: AsyncClient):
    response = await client.get("/api/profile")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_without_token(client: AsyncClient):
    response = await client.put(
        "/api/profile",
        json={"gender": "male"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_profile(client: AsyncClient, test_user: User):
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "date_of_birth": "1995-03-10",
            "gender": "female",
            "height_cm": 165.0,
            "weight_kg": 60.0,
            "blood_type": "B+",
            "allergies": ["dust"],
            "medical_conditions": ["asthma"],
            "dietary_preferences": ["gluten-free"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user.id)
    assert data["date_of_birth"] == "1995-03-10"
    assert data["gender"] == "female"
    assert data["height_cm"] == 165.0
    assert data["weight_kg"] == 60.0
    assert data["blood_type"] == "B+"
    assert data["allergies"] == ["dust"]
    assert data["medical_conditions"] == ["asthma"]
    assert data["dietary_preferences"] == ["gluten-free"]
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_profile_already_exists(client: AsyncClient, test_user: User):
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    await client.post(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "date_of_birth": "1995-03-10",
            "gender": "female",
        },
    )

    response = await client.post(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "date_of_birth": "1996-04-11",
            "gender": "male",
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_profile(client: AsyncClient, test_user: User):
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    await client.post(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "date_of_birth": "1995-03-10",
            "gender": "female",
        },
    )

    response = await client.delete(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
    assert response.text == ""


@pytest.mark.asyncio
async def test_delete_profile_without_token(client: AsyncClient):
    response = await client.delete("/api/profile")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_profile_without_token(client: AsyncClient):
    response = await client.post(
        "/api/profile",
        json={"gender": "male"},
    )
    assert response.status_code == 401
