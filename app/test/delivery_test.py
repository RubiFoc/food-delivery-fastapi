import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app  # Импортируйте ваше FastAPI приложение
from models.delivery import Dish, Cart, Customer, Role  # Импортируйте модели
from schemas.delivery import DishSchema, CartSchema  # Убедитесь, что схемы существуют

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://localhost") as client:
        yield client

@pytest.fixture
async def test_db(session: AsyncSession):
    # Создание роли для пользователя
    role = Role(name="customer")
    await session.add(role)
    await session.commit()
    await session.refresh(role)

    # Создание тестового клиента
    customer = Customer(user=User(username="testuser", email="test@example.com", hashed_password="hashedpassword", role=role))
    await session.add(customer)
    await session.commit()
    await session.refresh(customer)

    # Создание тестового блюда
    dish = Dish(
        name="Test Dish",
        price=100,
        weight=200,
        category_id=1,  # Укажите корректный category_id
        rating=0,
        number_of_marks=0,
        profit=100,
        time_of_preparing=10,
        restaurant_id=1
    )
    await session.add(dish)
    await session.commit()
    await session.refresh(dish)

    # Создание корзины для клиента
    cart = Cart(customer_id=customer.id)
    await session.add(cart)
    await session.commit()
    await session.refresh(cart)

    return customer, dish, cart

@pytest.mark.asyncio
async def test_create_dish(client: AsyncClient, test_db):
    customer, dish, cart = test_db

    # Проверка создания блюда
    response = await client.post("/api/dishes", json={
        "name": "New Dish",
        "price": 150,
        "weight": 300,
        "category_id": 1,  # Укажите корректный category_id
        "profit": 150,
        "time_of_preparing": 15
    })

    assert response.status_code == 200
    dish_response = response.json()
    assert dish_response["name"] == "New Dish"
    assert dish_response["price"] == 150

@pytest.mark.asyncio
async def test_add_dish_to_cart(client: AsyncClient, test_db):
    customer, dish, cart = test_db

    # Добавление блюда в корзину
    response = await client.post(f"/api/cart/{cart.id}/add-dish", json={
        "dish_id": dish.id,
        "quantity": 2
    })

    assert response.status_code == 200
    cart_response = response.json()
    assert cart_response["customer_id"] == customer.id
    assert len(cart_response["dishes"]) == 1  # Проверяем, что в корзине одно блюдо
    assert cart_response["dishes"][0]["dish_id"] == dish.id
    assert cart_response["dishes"][0]["quantity"] == 2
