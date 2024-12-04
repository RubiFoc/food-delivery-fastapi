from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from auth.database import get_async_session
from dependencies import get_current_kitchen_worker
from models.delivery import KitchenWorker, Order, OrderStatus, OrderDishAssociation
from schemas.delivery import OrderStatusSchema
from schemas.order import OrderSchema

kitchen_worker_router = APIRouter(prefix="/kitchen_worker", tags=["kitchen_workers"])


@kitchen_worker_router.put("/{order_id}/prepare", response_model=OrderStatusSchema)
async def prepare_order(
        order_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_kitchen_worker: KitchenWorker = Depends(get_current_kitchen_worker)
):
    result = await session.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.status))
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_status_record = await session.execute(
        select(OrderStatus).where(OrderStatus.order_id == order_id)
    )
    order_status_record = order_status_record.scalar_one_or_none()

    if order_status_record:
        order_status_record.is_prepared = True
        order_status_record.is_delivered = False
    else:
        order_status_record = OrderStatus(
            order_id=order_id,
            is_prepared=True,
            is_delivered=False
        )
        session.add(order_status_record)

    order.kitchen_worker_id = current_kitchen_worker.id

    await session.commit()

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
    result = await session.execute(
        select(Order, OrderStatus)
        .join(OrderStatus)
        .where(OrderStatus.is_prepared == False)
        .options(selectinload(Order.status))
    )

    orders = result.scalars().all()

    if not orders:
        raise HTTPException(status_code=404, detail="No orders found that are not ready")

    order_status_list = [
        OrderStatusSchema(
            order_id=order.id,
            is_prepared=order.status.is_prepared,
            is_delivered=order.status.is_delivered
        )
        for order in orders
    ]

    return order_status_list


@kitchen_worker_router.get("/orders/{order_id}", response_model=OrderSchema)
async def get_order_details(
        order_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_kitchen_worker: KitchenWorker = Depends(get_current_kitchen_worker)
):
    result = await session.execute(
        select(Order)
        .options(selectinload(Order.dishes).selectinload(OrderDishAssociation.dish))
        .where(Order.id == order_id)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order
