"""Tests for FoodLog CRUD operations."""

import pytest
from datetime import datetime, timezone
from httpx import AsyncClient

from src.models.user import User


@pytest.mark.asyncio
async def test_create_food_log(client: AsyncClient, test_user: User):
    """Test creating a new food log entry."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/food-logs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "description": "Chicken Salad",
            "calories": 350.0,
            "protein_g": 30.0,
            "carbs_g": 15.0,
            "fat_g": 20.0,
            "meal_type": "lunch",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Chicken Salad"
    assert data["calories"] == 350.0
    assert data["protein_g"] == 30.0
    assert data["carbs_g"] == 15.0
    assert data["fat_g"] == 20.0
    assert data["meal_type"] == "lunch"
    assert "id" in data
    assert "user_id" in data
    assert "logged_at" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_food_logs(client: AsyncClient, test_user: User):
    """Test retrieving food logs."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create a food log first
    await client.post(
        "/api/food-logs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "description": "Oatmeal",
            "calories": 200.0,
            "meal_type": "breakfast",
        },
    )

    # Get food logs
    response = await client.get(
        "/api/food-logs",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(log["description"] == "Oatmeal" for log in data)


@pytest.mark.asyncio
async def test_get_food_logs_filter_by_meal_type(client: AsyncClient, test_user: User):
    """Test retrieving food logs filtered by meal type."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create food logs for different meals
    await client.post(
        "/api/food-logs",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "Breakfast", "meal_type": "breakfast"},
    )
    await client.post(
        "/api/food-logs",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "Lunch", "meal_type": "lunch"},
    )

    # Get only breakfast logs
    response = await client.get(
        "/api/food-logs?meal_type=breakfast",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert all(log["meal_type"] == "breakfast" for log in data)


@pytest.mark.asyncio
async def test_update_food_log(client: AsyncClient, test_user: User):
    """Test updating a food log entry."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create a food log
    create_response = await client.post(
        "/api/food-logs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "description": "Sandwich",
            "calories": 400.0,
            "meal_type": "lunch",
        },
    )
    food_log_id = create_response.json()["id"]

    # Update the food log
    response = await client.put(
        f"/api/food-logs/{food_log_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "description": "Chicken Sandwich",
            "calories": 450.0,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Chicken Sandwich"
    assert data["calories"] == 450.0


@pytest.mark.asyncio
async def test_delete_food_log(client: AsyncClient, test_user: User):
    """Test deleting a food log entry."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    # Create a food log
    create_response = await client.post(
        "/api/food-logs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "description": "To delete",
            "meal_type": "snack",
        },
    )
    food_log_id = create_response.json()["id"]

    # Delete the food log
    response = await client.delete(
        f"/api/food-logs/{food_log_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert response.text == ""


@pytest.mark.asyncio
async def test_food_log_without_token(client: AsyncClient):
    """Test accessing food logs without authentication."""
    response = await client.get("/api/food-logs")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_food_log_invalid_meal_type(client: AsyncClient, test_user: User):
    """Test creating a food log with invalid meal type."""
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/food-logs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "description": "Test",
            "meal_type": "invalid_meal",
        },
    )

    # This should fail validation
    assert response.status_code == 422
