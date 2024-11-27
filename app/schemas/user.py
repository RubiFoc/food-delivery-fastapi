from datetime import datetime
from typing import Optional, List, Union

from fastapi_users import schemas
from pydantic import BaseModel


# Схема для создания и чтения пользователей
class UserRead(schemas.BaseUser[int]):
    username: str
    role_id: int


class UserCreate(schemas.BaseUserCreate):
    username: str
    role_id: int


class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[str] = None
    password: Optional[str] = None


class CourierSchema(BaseModel):
    id: int
    rating: Optional[float] = None
    number_of_marks: int
    rate: float
    location: str
    orders: Optional[List['OrderSchema']] = None  # Ссылаемся на OrderSchema, если она определена

    class Config:
        orm_mode = True


class CustomerSchema(BaseModel):
    id: int
    balance: float
    orders: Optional[List['OrderSchema']] = None  # Ссылаемся на OrderSchema, если она определена
    location: Optional[str] = None

    class Config:
        orm_mode = True


# Схема для ролей
class RoleSchema(BaseModel):
    id: int
    name: str
    permissions: Optional[dict] = None  # Словарь для хранения прав

    class Config:
        orm_mode = True


# Схема для всех пользователей
class BaseUser(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True


# Схема для полного пользователя, включая роль
class FullUserSchema(BaseUser):
    role: RoleSchema

    class Config:
        orm_mode = True


class AdminSchema(BaseModel):
    id: Union[int, UserCreate]
    role_id: Union[int, RoleSchema]

    class Config:
        orm_mode = True
        from_attributes = True
