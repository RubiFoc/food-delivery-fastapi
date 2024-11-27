from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from geopy.distance import geodesic

from auth.database import get_async_session
from dependencies import get_current_courier
from models.delivery import Courier, Order, OrderStatus
from schemas.delivery import OrderStatusSchema

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


@courier_router.put("/{order_id}/take", response_model=OrderStatusSchema)
async def take_order(
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

    # Проверяем, что заказ еще не был взят курьером
    if order.courier_id is not None:
        raise HTTPException(status_code=400, detail="Order is already taken by another courier")

    # Получаем клиента по его customer_id
    customer_result = await session.execute(
        select(Courier).where(Courier.id == order.customer_id)
    )
    customer = customer_result.scalar_one_or_none()

    # Если клиент не найден, выбрасываем ошибку
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Получаем координаты курьера
    if current_courier.location:
        courier_location = current_courier.location.split(', ')  # Курьерская локация в формате "lat, lon"
        courier_lat, courier_lon = float(courier_location[0]), float(courier_location[1])
    else:
        # Если у курьера нет локации, назначаем значения по умолчанию
        courier_lat, courier_lon = 0.0, 0.0

    # Получаем координаты клиента (из заказа)
    if customer.location:
        customer_location = customer.location.split(', ')  # Клиентская локация в формате "lat, lon"
        customer_lat, customer_lon = float(customer_location[0]), float(customer_location[1])
    else:
        # Если у клиента нет локации, назначаем значения по умолчанию
        customer_lat, customer_lon = 0.0, 0.0

    # Рассчитываем расстояние между курьером и клиентом
    distance_km = geodesic((courier_lat, courier_lon), (customer_lat, customer_lon)).km

    # Примерное время на маршрут: 5 км в час (передвижение на машине)
    speed_kmh = 50  # Средняя скорость 50 км/ч
    travel_time_hours = distance_km / speed_kmh
    travel_time = timedelta(hours=travel_time_hours)

    # Находим самое долгое время приготовления из всех блюд в заказе
    max_preparation_time = max(dish.dish.time_of_preparing for dish in order.dishes)

    # Время ожидания = время на приготовление самого долгого блюда + время на маршрут
    waiting_time = timedelta(minutes=max_preparation_time) + travel_time

    # Устанавливаем ID курьера для этого заказа
    order.courier_id = current_courier.id
    order.time_of_delivery = datetime.now() + waiting_time  # Ожидаемое время доставки

    # Сохраняем изменения в базе данных
    await session.commit()

    # Возвращаем обновленный статус заказа
    return OrderStatusSchema(
        order_id=order.id,
        is_prepared=order.status.is_prepared,
        is_delivered=order.status.is_delivered
    )




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
