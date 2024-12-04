from pydantic import BaseModel
from typing import Optional


class DishCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    restaurant_id: int


class DishUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    restaurant_id: Optional[int] = None


class DishRead(DishCreate):
    id: int

    class Config:
        orm_mode = True


class AddDishSchema(BaseModel):
    name: str
    price: float
    weight: float
    category_id: int
    profit: float
    time_of_preparing: int

    class Config:
        orm_mode = True
