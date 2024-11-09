from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models.delivery import User, Courier, KitchenWorker, Admin
from schemas.user import UserCreate


async def register_role_user(user_data: UserCreate, role: str, session: AsyncSession):
    # Проверка существующего пользователя
    existing_user = await session.execute(select(User).where(User.email == user_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Создание пользователя в зависимости от роли
    if role == "courier":
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=user_data.hashed_password,  # хэшируйте пароль перед сохранением
            role_id=2  # роль курьера
        )
        courier = Courier(id=new_user.id, location=user_data.location)
        session.add(courier)
    elif role == "kitchen_worker":
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=user_data.hashed_password,
            role_id=3  # роль кухонного работника
        )
        worker = KitchenWorker(id=new_user.id)
        session.add(worker)
    elif role == "admin":
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=user_data.hashed_password,
            role_id=4  # роль администратора
        )
        admin = Admin(id=new_user.id)
        session.add(admin)

    session.add(new_user)
    await session.commit()

    return user_data