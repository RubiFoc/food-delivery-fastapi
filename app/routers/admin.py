from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.database import get_async_session
from dependencies import get_current_superuser
from models.delivery import User
from schemas.user import UserCreate
from services.admin_service import register_role_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/register_courier", response_model=UserCreate)
async def register_courier(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_async_session),
        admin_user=Depends(get_current_superuser)
):
    return await register_role_user(user_data, role="courier", session=session)


@router.post("/register_kitchen_worker", response_model=UserCreate)
async def register_kitchen_worker(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_async_session),
        admin_user=Depends(get_current_superuser)
):
    return await register_role_user(user_data, role="kitchen_worker", session=session)


@router.post("/register_admin", response_model=UserCreate)
async def register_admin(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_async_session),
        admin_user=Depends(get_current_superuser)
):
    return await register_role_user(user_data, role="admin", session=session)


@router.post("/register_first_admin", response_model=UserCreate)
async def register_first_admin(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_async_session)
):
    # Проверка на существование первого администратора
    existing_admin = await session.execute(select(User).where(User.role_id == 4))
    if existing_admin.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin user already exists. Only the first admin can be created here."
        )

    # Создание первого администратора
    return await register_role_user(user_data, role="admin", session=session)
