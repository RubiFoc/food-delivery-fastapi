from datetime import datetime

from sqlalchemy import (
    Column, Integer, Float, String, ForeignKey, Time, DateTime, Boolean, JSON
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    permissions = Column(JSON)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, unique=True, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    registration_date = Column(DateTime, nullable=False, default=datetime.now)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)


class Courier(Base):
    __tablename__ = 'courier'

    id = Column(Integer, ForeignKey('user.id'), unique=True, primary_key=True)
    rating = Column(Float, nullable=True)
    number_of_marks = Column(Integer, default=0, nullable=False)
    rate = Column(Float, default=0.1, nullable=False)
    location = Column(String, nullable=False)


class Customer(Base):
    __tablename__ = 'customer'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    balance = Column(Float, default=0, nullable=False)


class KitchenWorker(Base):
    __tablename__ = 'kitchen_worker'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(50), nullable=False)
    location = Column(String, nullable=False)
    rating = Column(Float, nullable=True)
    number_of_marks = Column(Integer, default=0, nullable=False)


class DishCategory(Base):
    __tablename__ = 'dish_category'

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(50), nullable=False)


class Dish(Base):
    __tablename__ = 'dish'

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    category = Column(Integer, ForeignKey('dish_category.id'), nullable=False)
    rating = Column(Float, nullable=True)
    number_of_marks = Column(Integer, default=0, nullable=False)
    profit = Column(Float, nullable=False)
    time_of_preparing = Column(Time, nullable=False)


class OrderDishAssociation(Base):
    __tablename__ = 'order_dish_association'

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    dish_id = Column(Integer, ForeignKey('dish.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, unique=True, primary_key=True)
    price = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    promo = Column(String, nullable=False)
    promo_discount = Column(Float, nullable=False)
    time_of_creation = Column(DateTime, nullable=False)
    time_of_delivery = Column(DateTime, nullable=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    location = Column(String, nullable=False)
    courier_id = Column(Integer, ForeignKey('courier.id'), nullable=False)
    kitchen_worker_id = Column(Integer, ForeignKey('kitchen_worker.id'), nullable=False)


class OrderStatus(Base):
    __tablename__ = 'order_status'

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    is_prepared = Column(Boolean, default=False, nullable=False)
    is_ready_for_delivery = Column(Boolean, default=False, nullable=False)
