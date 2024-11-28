from pydantic import BaseModel
from typing import Optional

class CartCreate(BaseModel):
    user_id: int
    dish_id: int
    quantity: int

class CartUpdate(BaseModel):
    quantity: Optional[int] = None

class CartRead(CartCreate):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
