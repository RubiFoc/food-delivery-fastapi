from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from geopy.distance import geodesic

from auth.database import get_async_session
from config import YANDEX_API_KEY
from dependencies import get_current_courier
from models.delivery import Courier, Order, OrderStatus
from schemas.delivery import OrderStatusSchema
from schemas.order import OrderInfoSchema

courier_router = APIRouter(prefix="/courier", tags=["couriers"])


# Маршрут для получения заказов, которые не доставлены и не назначен курьер
@courier_router.get("/orders/not_delivered", response_model=list[OrderStatusSchema])
async def get_not_delivered_orders(
        session: AsyncSession = Depends(get_async_session),
        current_courier: Courier = Depends(get_current_courier)
):
    # Получаем все заказы, которые еще не доставлены и не имеют назначенного курьера
    result = await session.execute(
        select(Order, OrderStatus)
        .join(OrderStatus)
        .where(OrderStatus.is_delivered == False, Order.courier_id == None)
        .options(selectinload(Order.status))
    )

    # Извлекаем все заказы
    orders = result.scalars().all()

    # Если заказы не найдены, выбрасываем ошибку
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found that are not delivered")

    # Преобразуем данные в список схем OrderStatusSchema
    order_status_list = [
        OrderStatusSchema(
            order_id=order.id,  # Здесь используем id заказа
            is_prepared=order.status.is_prepared,
            is_delivered=order.status.is_delivered
        )
        for order in orders
    ]

    return order_status_list


async def get_coordinates(location: str) -> tuple:
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_API_KEY}&geocode={"Минск, " + location}&format=json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch coordinates from Yandex API")
        geo_data = response.json()
        coordinates = geo_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        lon, lat = map(float, coordinates.split())
        return lat, lon


@courier_router.post("/orders/{order_id}/take")
async def take_order(
        order_id: int,
        courier_location: str,
        session: AsyncSession = Depends(get_async_session),
        current_courier: Courier = Depends(get_current_courier)
):
    # Получаем заказ с предзагрузкой связанных блюд и статуса
    result = await session.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.dishes), selectinload(Order.status))
    )
    order: Order = result.scalars().first()

    # Проверка существования и статуса заказа
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status.is_delivered:
        raise HTTPException(status_code=400, detail="Order already delivered")
    if order.courier_id:
        raise HTTPException(status_code=400, detail="Order already taken by another courier")
    if not order.status.is_prepared:
        raise HTTPException(status_code=400, detail="Order is not prepared yet")

    # Получаем координаты курьера и заказчика
    courier_coords = await get_coordinates(courier_location)
    customer_coords = tuple(map(float, order.location.split(",")))

    # Расчет расстояния и времени на доставку
    distance_km = geodesic(courier_coords, customer_coords).kilometers
    delivery_time_minutes = distance_km * 0.86  # Допустимая скорость — 70 км/ч (~0.86 мин/км)

    # Проверяем, что блюда в заказе существуют и есть время на приготовление
    if not order.dishes:
        raise HTTPException(status_code=400, detail="No dishes in the order")

    # Получаем максимальное время приготовления блюда
    max_preparing_time = 20
    # Общее расчетное время доставки
    expected_time_of_delivery = (
            order.time_of_creation +
            timedelta(minutes=max_preparing_time) +
            timedelta(minutes=delivery_time_minutes)
    )

    # Обновляем курьера с его локацией
    current_courier.location = courier_location  # Обновляем локацию курьера
    order.courier_id = current_courier.id  # Назначаем курьера на заказ
    order.expected_time_of_delivery = expected_time_of_delivery  # Сохраняем время ожидания доставки

    # Сохраняем изменения
    session.add(current_courier)
    session.add(order)
    await session.commit()

    return {"message": "Order taken successfully", "expected_time_of_delivery": expected_time_of_delivery}


# Маршрут для уведомления о доставке заказа курьером
@courier_router.put("/{order_id}/deliver", response_model=OrderStatusSchema)
async def deliver_order(
        order_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_courier: Courier = Depends(get_current_courier)
):
    # Получаем заказ по ID
    result = await session.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.status))
    )
    order = result.scalar_one_or_none()

    # Если заказ не найден, выбрасываем ошибку
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Проверяем, что заказ был взят курьером
    if order.courier_id != current_courier.id:
        raise HTTPException(status_code=400, detail="You are not the assigned courier for this order")

    # Обновляем статус заказа на доставленный
    order_status_record = await session.execute(
        select(OrderStatus).where(OrderStatus.order_id == order_id)
    )
    order_status_record = order_status_record.scalar_one_or_none()

    if order_status_record:
        order_status_record.is_delivered = True  # Устанавливаем статус доставки на True
        order.time_of_delivery = datetime.now()  # Заполняем время доставки
    else:
        # Если статус заказа не существует, создаем новый
        order_status_record = OrderStatus(
            order_id=order_id,
            is_prepared=True,  # Предположим, что заказ уже был подготовлен
            is_delivered=True  # Устанавливаем статус доставки на True
        )
        session.add(order_status_record)
        order.time_of_delivery = datetime.now()  # Заполняем время доставки

    # Сохраняем изменения в базе данных
    await session.commit()

    # Возвращаем обновленный статус заказа
    return OrderStatusSchema(
        order_id=order.id,
        is_prepared=order_status_record.is_prepared,
        is_delivered=order_status_record.is_delivered
    )


@courier_router.get("/orders/assigned", response_model=list[OrderStatusSchema])
async def get_assigned_orders(
        session: AsyncSession = Depends(get_async_session),
        current_courier: Courier = Depends(get_current_courier)
):
    # Получаем заказы, назначенные текущему курьеру, которые еще не доставлены
    result = await session.execute(
        select(Order)
        .where(Order.courier_id == current_courier.id)
        .options(selectinload(Order.status))
    )

    orders = result.scalars().all()

    if not orders:
        raise HTTPException(status_code=404, detail="No assigned orders found")

    # Формируем список схем
    order_status_list = [
        OrderStatusSchema(
            order_id=order.id,
            is_prepared=order.status.is_prepared,
            is_delivered=order.status.is_delivered
        )
        for order in orders
    ]

    return order_status_list


@courier_router.get("/orders/{order_id}/info", response_model=OrderInfoSchema)
async def get_order_info(
        order_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_courier: Courier = Depends(get_current_courier)
):
    # Получаем заказ по ID
    result = await session.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    # Если заказ не найден, выбрасываем ошибку
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Возвращаем информацию о заказе
    return OrderInfoSchema(
        cost=order.price,
        creation_date=order.time_of_creation,
        weight=order.weight,
        location=order.location
    )
