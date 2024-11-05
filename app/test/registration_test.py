# app/test/registration_test.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://localhost") as client:
        user_data = {
            "email": "test@example.com",
            "password": "testpassword",
            "username": "testuser",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "role_id": 1
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        assert response.json()["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_register_user_with_existing_email():
    async with AsyncClient(app=app, base_url="http://localhost") as client:
        user_data = {
            "email": "test@example.com",
            "password": "testpassword",
            "username": "testuser",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "role_id": 1
        }
        # Первый запрос - успешная регистрация
        await client.post("/auth/register", json=user_data)

        # Повторная регистрация с тем же email
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_register_user_with_invalid_data():
    async with AsyncClient(app=app, base_url="http://localhost") as client:
        user_data = {
            "email": "invalid_email",  # Неверный email
            "password": "testpassword",
            "username": "testuser",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "role_id": 1
        }
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 422  # Ошибка валидации
