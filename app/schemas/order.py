from pydantic import BaseModel
from typing import List, Optional

class OrderCreate(BaseModel):
    user_id: int
    restaurant_id: int
    dish_ids: List[int]
    total_price: float

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    total_price: Optional[float] = None

class OrderRead(OrderCreate):
    id: int
    status: str
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
