from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from auth.database import get_async_session
from dependencies import get_current_kitchen_worker
from models.delivery import KitchenWorker, Order, OrderStatus
from schemas.delivery import OrderStatusSchema

kitchen_worker_router = APIRouter(prefix="/kitchen_worker", tags=["kitchen_workers"])


# Маршрут для обновления статуса приготовления заказа
@kitchen_worker_router.put("/{order_id}/prepare", response_model=OrderStatusSchema)
async def prepare_order(
        order_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_kitchen_worker: KitchenWorker = Depends(get_current_kitchen_worker)
):
    # Получаем заказ по ID
    result = await session.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.status))
    )
    order = result.scalar_one_or_none()

    # Если заказ не найден, выбрасываем ошибку
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Получаем статус заказа, если он уже существует, обновляем его
    order_status_record = await session.execute(
        select(OrderStatus).where(OrderStatus.order_id == order_id)
    )
    order_status_record = order_status_record.scalar_one_or_none()

    if order_status_record:
        order_status_record.is_prepared = True  # Устанавливаем статус готовности на True
        order_status_record.is_delivered = False  # Предположим, что заказ еще не доставлен
    else:
        # Если статус заказа не существует, создаем новый
        order_status_record = OrderStatus(
            order_id=order_id,
            is_prepared=True,  # Устанавливаем статус готовности на True
            is_delivered=False  # Предположим, что заказ еще не доставлен
        )
        session.add(order_status_record)

    # Устанавливаем ID работника кухни для этого заказа
    order.kitchen_worker_id = current_kitchen_worker.id

    # Сохраняем изменения в базе данных
    await session.commit()

    # Возвращаем обновленный статус заказа
    return OrderStatusSchema(
        order_id=order.id,
        is_prepared=order_status_record.is_prepared,
        is_delivered=order_status_record.is_delivered
    )


@kitchen_worker_router.get("/orders/not_ready", response_model=list[OrderStatusSchema])
async def get_not_ready_orders(
        session: AsyncSession = Depends(get_async_session),
        current_kitchen_worker: KitchenWorker = Depends(get_current_kitchen_worker)
):
    # Получаем все заказы, которые еще не готовы
    result = await session.execute(
        select(Order, OrderStatus)
        .join(OrderStatus)
        .where(OrderStatus.is_prepared == False)
        .options(selectinload(Order.status))
    )

    # Извлекаем все заказы
    orders = result.scalars().all()

    # Если заказы не найдены, выбрасываем ошибку
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found that are not ready")

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
