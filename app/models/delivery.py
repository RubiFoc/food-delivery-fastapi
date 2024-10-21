from datetime import datetime

from sqlalchemy import (
    Column, Integer, Float, String, ForeignKey, Time, DateTime, Boolean, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    permissions = Column(JSON)

    # Связь с пользователями
    users = relationship("User", back_populates="role")


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

    # Связь с ролью
    role = relationship("Role", back_populates="users")

    # Связь с курьером, клиентом и кухонным работником
    courier = relationship("Courier", back_populates="user", uselist=False)
    customer = relationship("Customer", back_populates="user", uselist=False)
    kitchen_worker = relationship("KitchenWorker", back_populates="user", uselist=False)


class Courier(Base):
    __tablename__ = 'courier'

    id = Column(Integer, ForeignKey('user.id'), unique=True, primary_key=True)
    rating = Column(Float, nullable=True)
    number_of_marks = Column(Integer, default=0, nullable=False)
    rate = Column(Float, default=0.1, nullable=False)
    location = Column(String, nullable=False)

    # Связь с пользователем
    user = relationship("User", back_populates="courier")


class Customer(Base):
    __tablename__ = 'customer'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    balance = Column(Float, default=0, nullable=False)

    # Связь с пользователем
    user = relationship("User", back_populates="customer")


class KitchenWorker(Base):
    __tablename__ = 'kitchen_worker'

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    # Связь с пользователем
    user = relationship("User", back_populates="kitchen_worker")


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(50), nullable=False)
    location = Column(String, nullable=False)
    rating = Column(Float, nullable=True)
    number_of_marks = Column(Integer, default=0, nullable=False)

    # Связь с блюдами и заказами
    dishes = relationship("Dish", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")


class DishCategory(Base):
    __tablename__ = 'dish_category'

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(50), nullable=False)

    # Связь с блюдами
    dishes = relationship("Dish", back_populates="category")


class Dish(Base):
    __tablename__ = 'dish'

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('dish_category.id'),
                         nullable=False)  # Убедитесь, что название поля корректно
    rating = Column(Float, nullable=True)
    number_of_marks = Column(Integer, default=0, nullable=False)
    profit = Column(Float, nullable=False)
    time_of_preparing = Column(Float, nullable=False)

    # Связь с категорией и рестораном
    category = relationship("DishCategory", back_populates="dishes")
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    restaurant = relationship("Restaurant", back_populates="dishes")

    # Связь с заказами
    orders = relationship("OrderDishAssociation", back_populates="dish")


class OrderDishAssociation(Base):
    __tablename__ = 'order_dish_association'

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    dish_id = Column(Integer, ForeignKey('dish.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)

    # Связь с заказом и блюдом
    order = relationship("Order", back_populates="dishes")
    dish = relationship("Dish", back_populates="orders")


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

    # Связь с блюдами и рестораном
    dishes = relationship("OrderDishAssociation", back_populates="order")
    restaurant = relationship("Restaurant", back_populates="orders")


class OrderStatus(Base):
    __tablename__ = 'order_status'

    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    is_prepared = Column(Boolean, default=False, nullable=False)
    is_ready_for_delivery = Column(Boolean, default=False, nullable=False)
