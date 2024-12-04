from datetime import datetime

from psycopg import Time
from sqlalchemy import (
    Column, Integer, Float, String, ForeignKey, DateTime, Boolean, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    permissions = Column(JSON)
    users = relationship("User", back_populates="role")
    couriers = relationship("Courier", back_populates="role")
    customers = relationship("Customer", back_populates="role")
    kitchen_workers = relationship("KitchenWorker", back_populates="role")
    admins = relationship("Admin", back_populates="role")


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    registration_date = Column(DateTime, nullable=False, default=datetime.now)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = relationship("Role", back_populates="users")
    courier = relationship("Courier", back_populates="user", uselist=False)
    customer = relationship("Customer", back_populates="user", uselist=False)
    kitchen_worker = relationship("KitchenWorker", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)


class Courier(Base):
    __tablename__ = 'courier'
    id = Column(Integer, ForeignKey('user.id'), unique=True, primary_key=True)
    rating = Column(Float, nullable=True)
    number_of_marks = Column(Integer, default=0, nullable=False)
    rate = Column(Float, default=0.1, nullable=False)
    location = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), default=2)

    user = relationship("User", back_populates="courier")
    role = relationship("Role", back_populates="couriers")
    orders = relationship("Order", back_populates="courier")

    def update_rating(self, new_rating):
        if self.rating is None:
            self.rating = new_rating
        else:
            total_marks = self.number_of_marks + 1
            self.rating = ((self.rating * self.number_of_marks) + new_rating) / total_marks
        self.number_of_marks += 1


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    balance = Column(Float, default=0, nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), default=1)
    user = relationship("User", back_populates="customer")
    role = relationship("Role", back_populates="customers")
    cart = relationship("Cart", back_populates="customer")
    location = Column(String, nullable=True)


class KitchenWorker(Base):
    __tablename__ = 'kitchen_worker'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey("role.id"), default=3)
    user = relationship("User", back_populates="kitchen_worker")
    role = relationship("Role", back_populates="kitchen_workers")
    orders = relationship("Order", back_populates="kitchen_worker")


class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)  # ForeignKey links to user table
    role_id = Column(Integer, ForeignKey("role.id"), default=4)
    user = relationship("User", back_populates="admin")
    role = relationship("Role", back_populates="admins")


class Restaurant(Base):
    __tablename__ = 'restaurant'
    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(50), nullable=False)
    location = Column(String, nullable=False)
    rating = Column(Float, nullable=True)
    number_of_marks = Column(Integer, default=0, nullable=False)
    dishes = relationship("Dish", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")


class DishCategory(Base):
    __tablename__ = 'dish_category'
    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(50), nullable=False)
    dishes = relationship("Dish", back_populates="category")


class Dish(Base):
    __tablename__ = 'dish'
    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('dish_category.id'), nullable=False)
    rating = Column(Float, nullable=True)
    number_of_marks = Column(Integer, default=0, nullable=False)
    profit = Column(Float, nullable=False)
    time_of_preparing = Column(Float, nullable=False)
    image_path = Column(String, nullable=True)  # Новое поле для хранения пути к картинке

    category = relationship("DishCategory", back_populates="dishes")
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    restaurant = relationship("Restaurant", back_populates="dishes")
    orders = relationship("OrderDishAssociation", back_populates="dish")
    cart_associations = relationship("CartDishAssociation", back_populates="dish")

    def update_rating(self, new_rating):
        if self.rating is None:
            self.rating = new_rating
        else:
            total_marks = self.number_of_marks + 1
            self.rating = ((self.rating * self.number_of_marks) + new_rating) / total_marks
        self.number_of_marks += 1


class OrderDishAssociation(Base):
    __tablename__ = 'order_dish_association'
    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    dish_id = Column(Integer, ForeignKey('dish.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="dishes")
    dish = relationship("Dish", back_populates="orders")


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, unique=True, primary_key=True)
    price = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    time_of_creation = Column(DateTime, nullable=False)
    time_of_delivery = Column(DateTime, nullable=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    location = Column(String, nullable=False)
    courier_id = Column(Integer, ForeignKey('courier.id'), nullable=True)
    kitchen_worker_id = Column(Integer, ForeignKey('kitchen_worker.id'), nullable=True)
    time_of_delivery = Column(DateTime, default=None, nullable=True)
    expected_time_of_delivery = Column(DateTime, default=None, nullable=True)

    dishes = relationship("OrderDishAssociation", back_populates="order")
    restaurant = relationship("Restaurant", back_populates="orders")
    courier = relationship("Courier", back_populates="orders")
    kitchen_worker = relationship("KitchenWorker", back_populates="orders")
    customer_id = Column(Integer, ForeignKey("customer.id"))
    status = relationship("OrderStatus", back_populates="order", uselist=False)


class OrderStatus(Base):
    __tablename__ = 'order_status'
    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    is_prepared = Column(Boolean, default=False, nullable=False)
    is_delivered = Column(Boolean, default=False, nullable=False)

    order = relationship("Order", back_populates="status")


class CartDishAssociation(Base):
    __tablename__ = 'cart_dish_association'
    cart_id = Column(Integer, ForeignKey('cart.id'), primary_key=True)
    dish_id = Column(Integer, ForeignKey('dish.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)

    cart = relationship("Cart", back_populates="dishes")
    dish = relationship("Dish", back_populates="cart_associations")


class Cart(Base):
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    customer = relationship("Customer", back_populates="cart")
    dishes = relationship("CartDishAssociation", back_populates="cart")
