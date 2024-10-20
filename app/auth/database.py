from datetime import datetime
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer, DateTime, Column, ForeignKey, String, Boolean
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, DeclarativeMeta

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME, DOCKER_PORT
from models.delivery import Role

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@DB:{DOCKER_PORT}/{DB_NAME}"
# DATABASE_URL = f"postgresql+asyncpg://postgres:postgres@localhost:5434/kurs_db"


Base: DeclarativeMeta = declarative_base()


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, unique=True, primary_key=True)
    email = Column(String(length=320), nullable=False, unique=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    registration_date = Column(DateTime, nullable=False, default=datetime.now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
