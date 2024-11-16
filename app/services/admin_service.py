from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from starlette import status
from fastapi_users import fastapi_users

from models.delivery import User, Courier, KitchenWorker, Admin
from schemas.user import UserCreate, AdminSchema

# Инициализация контекста для хеширования пароля (например, bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def register_role_user(user_data: UserCreate, role: str, session: AsyncSession):
    existing_user = await session.execute(select(User).where(User.email == user_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    hashed_password = pwd_context.hash(user_data.password)
    if role == "courier":
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            role_id=2  # Роль курьера
        )
        session.add(new_user)

        courier = Courier(id=new_user.id, location=user_data.location)
        session.add(courier)
    elif role == "kitchen_worker":
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            role_id=3  # Роль кухонного работника
        )
        session.add(new_user)

        worker = KitchenWorker(id=new_user.id)
        session.add(worker)
    elif role == "admin":
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,  # Используем захешированный пароль
            role_id=4
        )
        # Необходимо создать нового администратора, привязав его к пользователю
        session.add(new_user)

        admin = Admin(id=new_user.id, role_id=4)  # Здесь используем id пользователя
        session.add(admin)
    await session.commit()
    return user_data
