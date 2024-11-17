from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime, time


class RestaurantSchema(BaseModel):
    id: int
    name: str
    location: str
    rating: Optional[float] = None
    number_of_marks: int = Field(default=0)

    class Config:
        orm_mode = True
        from_attributes = True


class DishCategorySchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        from_attributes = True


class DishSchema(BaseModel):
    id: int
    name: str
    price: float
    weight: float
    category_id: Union[int, DishCategorySchema]
    rating: Optional[float] = None
    number_of_marks: int = Field(default=0)
    profit: float
    time_of_preparing: float

    class Config:
        orm_mode = True
        from_attributes = True


class OrderDishAssociationSchema(BaseModel):
    order_id: int
    dish_id: int
    quantity: int

    class Config:
        orm_mode = True
        from_attributes = True


class OrderSchema(BaseModel):
    id: int
    price: float
    weight: float
    time_of_creation: datetime
    time_of_delivery: Optional[datetime] = None
    restaurant_id: int
    location: str
    courier_id: Optional[int] = None  # Сделано необязательным
    kitchen_worker_id: Optional[int] = None  # Сделано необязательным
    customer_id: Optional[int] = None  # Сделано необязательным

    class Config:
        orm_mode = True
        from_attributes = True


class OrderStatusSchema(BaseModel):
    order_id: Union[int, OrderSchema]
    is_prepared: bool = Field(default=False)
    is_delivered: bool = Field(default=False)

    class Config:
        orm_mode = True
        from_attributes = True


class CartDishSchema(BaseModel):
    dish_id: int
    quantity: int

    class Config:
        orm_mode = True
        from_attributes = True


# Схема корзины
class CartSchema(BaseModel):
    id: int
    customer_id: int
    dishes: List[CartDishSchema] = []

    class Config:
        orm_mode = True
        from_attributes = True
