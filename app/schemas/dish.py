# schemas/dish.py
from pydantic import BaseModel
from typing import Optional

class DishCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    restaurant_id: int  # Чтобы связать блюдо с рестораном

class DishUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    restaurant_id: Optional[int] = None  # Возможность изменять ресторан для блюда

class DishRead(DishCreate):
    id: int

    class Config:
        orm_mode = True
