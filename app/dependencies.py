from fastapi import Depends, HTTPException
from fastapi_users import FastAPIUsers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import auth_backend
from auth.database import get_async_session
from auth.manager import get_user_manager
from models.delivery import User, KitchenWorker, Courier

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


def get_current_user(user: User = Depends(fastapi_users.current_user())):
    return user


def get_current_superuser(user: User = Depends(fastapi_users.current_user(active=True, superuser=True))):
    return user


async def get_current_kitchen_worker(
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
) -> KitchenWorker:
    result = await db.execute(select(KitchenWorker).filter(KitchenWorker.id == current_user.id))
    kitchen_worker = result.scalar_one_or_none()

    if not kitchen_worker:
        raise HTTPException(status_code=403, detail="Not a kitchen worker")

    return kitchen_worker


async def get_current_courier(
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
) -> Courier:
    result = await db.execute(
        select(Courier).filter(Courier.id == current_user.id, Courier.role_id == 2)
    )
    courier = result.scalar_one_or_none()

    if not courier:
        raise HTTPException(status_code=403, detail="Not a courier")

    return courier
