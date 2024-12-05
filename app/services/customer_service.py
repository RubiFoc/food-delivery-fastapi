from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from sqlalchemy.orm import joinedload

from models.delivery import Customer, Cart, CartDishAssociation, OrderStatus, OrderDishAssociation, Order, Dish
from schemas.cart import CartDishAddRequest


async def validate_current_user(current_user):
    if not current_user:
        raise HTTPException(status_code=404, detail="Customer not found")


async def get_dish_by_id(dish_id: int, session: AsyncSession):
    dish = await session.get(Dish, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


async def get_or_create_cart(customer_id: int, session: AsyncSession):
    cart_query = await session.execute(select(Cart).where(Cart.customer_id == customer_id))
    cart = cart_query.scalars().first()

    if not cart:
        cart = Cart(customer_id=customer_id)
        session.add(cart)
        await session.flush()

    return cart


async def add_or_update_cart_dish(cart_id: int, dish_id: int, quantity: int, session: AsyncSession):
    association_query = await session.execute(
        select(CartDishAssociation)
        .where(CartDishAssociation.cart_id == cart_id, CartDishAssociation.dish_id == dish_id)
    )
    association = association_query.scalars().first()

    if association:
        association.quantity += quantity
    else:
        new_association = CartDishAssociation(cart_id=cart_id, dish_id=dish_id, quantity=quantity)
        session.add(new_association)


def validate_request_data(request: CartDishAddRequest):
    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")


async def get_cart_with_dishes(current_user, session: AsyncSession):
    cart_query = await session.execute(
        select(Cart)
        .where(Cart.customer_id == current_user.id)
        .options(joinedload(Cart.dishes).joinedload(CartDishAssociation.dish))
    )
    cart = cart_query.scalars().first()

    if not cart or not cart.dishes:
        raise HTTPException(status_code=404, detail="Cart is empty or not found")

    return cart


async def get_customer_with_balance_check(current_user, total_price, session: AsyncSession):
    customer_query = await session.execute(select(Customer).filter(Customer.id == current_user.id))
    customer = customer_query.scalars().first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if customer.balance < total_price:
        raise HTTPException(status_code=400, detail="Insufficient balance to complete the order")

    return customer


async def update_customer_balance(customer, amount, session: AsyncSession):
    customer.balance -= amount
    session.add(customer)


def calculate_order_details(cart):
    if not cart.dishes:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_price = 0
    total_weight = 0

    for cart_dish in cart.dishes:
        if cart_dish.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"Invalid quantity for dish {cart_dish.dish_id}")
        total_price += cart_dish.quantity * cart_dish.dish.price
        total_weight += cart_dish.quantity * cart_dish.dish.weight

    return total_price, total_weight


async def create_new_order(customer, cart, total_price, total_weight, session: AsyncSession):
    if not customer.location:
        raise HTTPException(status_code=404, detail="Customer location not found")

    new_order = Order(
        price=total_price,
        weight=total_weight,
        time_of_creation=datetime.now(),
        customer_id=customer.id,
        location=customer.location,
        restaurant_id=1  # можно параметризовать
    )
    session.add(new_order)
    await session.flush()

    for cart_dish in cart.dishes:
        order_dish = OrderDishAssociation(
            order_id=new_order.id,
            dish_id=cart_dish.dish_id,
            quantity=cart_dish.quantity
        )
        session.add(order_dish)

    session.add(OrderStatus(order_id=new_order.id))
    return new_order


async def update_customer_location_service(current_user, latitude: float, longitude: float, session: AsyncSession):
    if not isinstance(latitude, (float, int)) or not isinstance(longitude, (float, int)):
        raise HTTPException(status_code=400, detail="Latitude and longitude must be numbers")

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid geographic coordinates")

    result = await session.execute(select(Customer).filter(Customer.id == current_user.id))
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.location = f"{latitude}, {longitude}"
    await session.commit()

    return customer.location