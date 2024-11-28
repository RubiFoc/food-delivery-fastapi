# schemas/restaurant.py
from pydantic import BaseModel
from typing import Optional

class RestaurantCreate(BaseModel):
    name: str
    location: str
    contact_number: Optional[str] = None
    description: Optional[str] = None

class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    contact_number: Optional[str] = None
    description: Optional[str] = None

class RestaurantRead(RestaurantCreate):
    id: int

    class Config:
        orm_mode = True
