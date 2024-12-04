from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import FastAPIUsers
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from auth.database import get_async_session
from dependencies import get_current_superuser
from models.delivery import User, Role, Restaurant, Dish, Order, Cart
from schemas.cart import CartCreate, CartUpdate
from schemas.dish import DishUpdate, DishCreate
from schemas.order import OrderCreate, OrderUpdate
from schemas.user import UserCreate, UserRead, UserUpdate
from schemas.restaurant import RestaurantCreate, RestaurantUpdate
from auth.auth import auth_backend
from auth.manager import get_admin_manager, AdminManager

admin_router = APIRouter(prefix="/admin", tags=["admin"])

fastapi_users_admin = FastAPIUsers(
    get_admin_manager,
    [auth_backend],
)

admin_router.include_router(
    fastapi_users_admin.get_register_router(UserRead, UserCreate),
    prefix="/register",
)


@admin_router.post("/register")
async def register_admin(
        user_create: UserCreate,
        request: Request,
        admin_manager: AdminManager = Depends(get_admin_manager),
        current_user: User = Depends(get_current_superuser),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an existing admin can create another admin.")
    user = await admin_manager.create(user_create, request=request)
    return user


@admin_router.get("/users")
async def get_users(
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(User).options(joinedload(User.role)))
    users = result.scalars().all()
    return users


@admin_router.get("/user/{user_id}")
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(User).filter(User.id == user_id).options(joinedload(User.role)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@admin_router.put("/user/{user_id}")
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can update users.")
    result = await session.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    await session.commit()
    return {"message": f"User {user.username} updated successfully."}


@admin_router.delete("/user/{user_id}")
async def delete_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can delete users.")
    result = await session.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    await session.delete(user)
    await session.commit()
    return {"message": f"User {user.username} deleted successfully."}


@admin_router.get("/restaurants")
async def get_restaurants(
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Restaurant))
    restaurants = result.scalars().all()
    return restaurants


@admin_router.post("/restaurant")
async def create_restaurant(
        restaurant_create: RestaurantCreate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can create a restaurant.")
    restaurant = Restaurant(**restaurant_create.dict())
    session.add(restaurant)
    await session.commit()
    return {"message": "Restaurant created successfully."}


@admin_router.put("/restaurant/{restaurant_id}")
async def update_restaurant(
        restaurant_id: int,
        restaurant_update: RestaurantUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can update a restaurant.")
    result = await session.execute(select(Restaurant).filter(Restaurant.id == restaurant_id))
    restaurant = result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found.")

    for field, value in restaurant_update.dict(exclude_unset=True).items():
        setattr(restaurant, field, value)

    await session.commit()
    return {"message": f"Restaurant {restaurant.name} updated successfully."}


@admin_router.delete("/restaurant/{restaurant_id}")
async def delete_restaurant(
        restaurant_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can delete a restaurant.")
    result = await session.execute(select(Restaurant).filter(Restaurant.id == restaurant_id))
    restaurant = result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found.")
    await session.delete(restaurant)
    await session.commit()
    return {"message": f"Restaurant {restaurant.name} deleted successfully."}


@admin_router.get("/dishes")
async def get_dishes(
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Dish))
    dishes = result.scalars().all()
    return dishes


@admin_router.post("/dish")
async def create_dish(
        dish_create: DishCreate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can create a dish.")
    dish = Dish(**dish_create.dict())
    session.add(dish)
    await session.commit()
    return {"message": "Dish created successfully."}


@admin_router.put("/dish/{dish_id}")
async def update_dish(
        dish_id: int,
        dish_update: DishUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can update a dish.")
    result = await session.execute(select(Dish).filter(Dish.id == dish_id))
    dish = result.scalars().first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found.")

    for field, value in dish_update.dict(exclude_unset=True).items():
        setattr(dish, field, value)

    await session.commit()
    return {"message": f"Dish {dish.name} updated successfully."}


@admin_router.delete("/dish/{dish_id}")
async def delete_dish(
        dish_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can delete a dish.")
    result = await session.execute(select(Dish).filter(Dish.id == dish_id))
    dish = result.scalars().first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found.")
    await session.delete(dish)
    await session.commit()
    return {"message": f"Dish {dish.name} deleted successfully."}


@admin_router.get("/orders")
async def get_orders(
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Order).options(joinedload(Order.restaurant), joinedload(Order.user)))
    orders = result.scalars().all()
    return orders


@admin_router.post("/order")
async def create_order(
        order_create: OrderCreate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can create an order.")
    order = Order(**order_create.dict())
    session.add(order)
    await session.commit()
    return {"message": "Order created successfully."}


@admin_router.put("/order/{order_id}")
async def update_order(
        order_id: int,
        order_update: OrderUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can update an order.")
    result = await session.execute(select(Order).filter(Order.id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    for field, value in order_update.dict(exclude_unset=True).items():
        setattr(order, field, value)

    await session.commit()
    return {"message": f"Order {order.id} updated successfully."}


@admin_router.delete("/order/{order_id}")
async def delete_order(
        order_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can delete an order.")
    result = await session.execute(select(Order).filter(Order.id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    await session.delete(order)
    await session.commit()
    return {"message": f"Order {order.id} deleted successfully."}


@admin_router.get("/carts")
async def get_carts(
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Cart).options(joinedload(Cart.dish), joinedload(Cart.user)))
    carts = result.scalars().all()
    return carts


@admin_router.post("/cart")
async def create_cart(
        cart_create: CartCreate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can create a cart item.")
    cart_item = Cart(**cart_create.dict())
    session.add(cart_item)
    await session.commit()
    return {"message": "Cart item created successfully."}


@admin_router.put("/cart/{cart_id}")
async def update_cart(
        cart_id: int,
        cart_update: CartUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can update a cart item.")
    result = await session.execute(select(Cart).filter(Cart.id == cart_id))
    cart_item = result.scalars().first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found.")

    for field, value in cart_update.dict(exclude_unset=True).items():
        setattr(cart_item, field, value)

    await session.commit()
    return {"message": f"Cart item {cart_item.id} updated successfully."}


@admin_router.delete("/cart/{cart_id}")
async def delete_cart(
        cart_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can delete a cart item.")
    result = await session.execute(select(Cart).filter(Cart.id == cart_id))
    cart_item = result.scalars().first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found.")
    await session.delete(cart_item)
    await session.commit()
    return {"message": f"Cart item {cart_item.id} deleted successfully."}
