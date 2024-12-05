from pydantic import BaseModel
from typing import Optional

from pydantic.v1 import Field


class CartCreate(BaseModel):
    user_id: int
    dish_id: int
    quantity: int

    class Config:
        orm_mode = True
        from_attributes = True


class CartUpdate(BaseModel):
    quantity: Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True


class CartRead(CartCreate):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
        from_attributes = True


class CartDishAddRequest(BaseModel):
    dish_id: int = Field(..., description="ID of the dish")
    quantity: int = Field(..., ge=1, description="Quantity of the dish, must be a positive integer")

    class Config:
        orm_mode = True
        from_attributes = True
