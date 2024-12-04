import pytest
from httpx import AsyncClient
from main import app
from auth.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.delivery import Courier, Order, OrderStatus

@pytest.fixture
async def override_get_async_session():
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    # Создаем тестовую базу данных (SQLite in-memory)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        # Подключаем модели и создаем таблицы
        from models.delivery import Base
        await conn.run_sync(Base.metadata.create_all)

    async def get_test_session() -> AsyncSession:
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_async_session] = get_test_session
    yield
    app.dependency_overrides.pop(get_async_session)


@pytest.fixture
async def test_client(override_get_async_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def create_test_data(override_get_async_session):
    # Создаем тестовые данные
    session: AsyncSession = await override_get_async_session.__anext__()
    courier = Courier(id=1, rating=5.0, rate=100.0, location="50.4501,30.5234")
    order = Order(id=1, courier_id=None, location="50.4547,30.5238")
    order_status = OrderStatus(order_id=1, is_prepared=True, is_delivered=False)

    session.add_all([courier, order, order_status])
    await session.commit()


# Тест на получение недоставленных заказов
@pytest.mark.asyncio
async def test_get_not_delivered_orders(test_client, create_test_data):
    response = await test_client.get("/courier/orders/not_delivered")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["order_id"] == 1
    assert data[0]["is_prepared"] is True
    assert data[0]["is_delivered"] is False


# Тест на взятие заказа
@pytest.mark.asyncio
async def test_take_order(test_client, create_test_data):
    response = await test_client.put("/courier/1/take")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 1
    assert data["is_prepared"] is True
    assert data["is_delivered"] is False


# Тест на доставку заказа
@pytest.mark.asyncio
async def test_deliver_order(test_client, create_test_data):
    # Сначала курьер берет заказ
    await test_client.put("/courier/1/take")
    # Теперь доставляем заказ
    response = await test_client.put("/courier/1/deliver")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 1
    assert data["is_prepared"] is True
    assert data["is_delivered"] is True
