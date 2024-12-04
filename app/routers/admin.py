from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi_users import FastAPIUsers
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from auth.database import get_async_session
from dependencies import get_current_superuser
from models.delivery import User, Role, Restaurant, Dish, Order, Cart, DishCategory
from schemas.cart import CartCreate, CartUpdate
from schemas.delivery import DishSchema, DishCategorySchema
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


# +
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


# +
@admin_router.get("/users")
async def get_users(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    result = await session.execute(select(User).options(joinedload(User.role)))
    users = result.scalars().all()
    return users


# +
@admin_router.get("/user/{user_id}")
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    result = await session.execute(select(User).filter(User.id == user_id).options(joinedload(User.role)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


# ---
@admin_router.put("/user/{user_id}")
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
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
    user_to_delete = await session.get(User, user_id)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    await session.delete(user_to_delete)
    await session.commit()

    return {"message": "Пользователь успешно удален"}


@admin_router.get("/restaurants")
async def get_restaurants(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
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
    result = await session.execute(select(Restaurant).filter(Restaurant.id == restaurant_id))
    restaurant = result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found.")
    await session.delete(restaurant)
    await session.commit()
    return {"message": f"Restaurant {restaurant.name} deleted successfully."}


@admin_router.get("/dishes")
async def get_dishes(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    result = await session.execute(select(Dish))
    dishes = result.scalars().all()
    return dishes


@admin_router.post("/dishes", response_model=DishSchema)
async def add_dish(
        name: str,
        price: float,
        weight: float,
        category_id: int,
        profit: float,
        time_of_preparing: int,
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    from utils.dish import save_image
    image_path = await save_image(image)

    category_query = await session.execute(select(DishCategory).where(DishCategory.id == category_id))
    category = category_query.scalars().first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    new_dish = Dish(
        name=name,
        price=price,
        weight=weight,
        category_id=category_id,
        rating=0,
        number_of_marks=0,
        profit=profit,
        time_of_preparing=time_of_preparing,
        restaurant_id=1,
        image_path=image_path
    )

    session.add(new_dish)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Dish with this ID already exists")

    await session.refresh(new_dish)

    return new_dish


@admin_router.patch("/dishes/{dish_id}", response_model=DishSchema)
async def update_dish(
        dish_id: int,
        name: str = Form(None),
        price: float = Form(None),
        weight: float = Form(None),
        category_id: int = Form(None),
        profit: float = Form(None),
        time_of_preparing: int = Form(None),
        image: UploadFile = File(None),  # Теперь image необязателен
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    from utils.dish import save_image

    query = select(Dish).where(Dish.id == dish_id)
    result = await session.execute(query)
    dish = result.scalar_one_or_none()

    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    if category_id is not None:
        category_query = await session.execute(select(DishCategory).where(DishCategory.id == category_id))
        category = category_query.scalars().first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        dish.category_id = category_id

    if name is not None:
        dish.name = name
    if price is not None:
        dish.price = price
    if weight is not None:
        dish.weight = weight
    if profit is not None:
        dish.profit = profit
    if time_of_preparing is not None:
        dish.time_of_preparing = time_of_preparing

    if image is not None:
        image_path = await save_image(image)
        dish.image_path = image_path

    try:
        await session.commit()
        await session.refresh(dish)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Error updating dish")

    return dish



@admin_router.put("/dish/{dish_id}")
async def update_dish(
        dish_id: int,
        dish_update: DishUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    result = await session.execute(select(Dish).filter(Dish.id == dish_id))
    dish = result.scalars().first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found.")

    for field, value in dish_update.dict(exclude_unset=True).items():
        setattr(dish, field, value)

    await session.commit()
    return {"message": f"Dish {dish.name} updated successfully."}


@admin_router.delete("/dishes")
async def delete_dish(
        id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    existing_dish = await session.execute(
        select(Dish).where(Dish.id == id)
    )
    existing_dish = existing_dish.scalars().first()

    if not existing_dish:
        raise HTTPException(status_code=400, detail="Dish with this id doesn't exist")

    try:
        await session.delete(existing_dish)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error deleting dish")
    return {"Dish category was deleted": DishCategorySchema.from_orm(existing_dish)}


@admin_router.get("/orders")
async def get_orders(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
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
    result = await session.execute(select(Order).filter(Order.id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    await session.delete(order)
    await session.commit()
    return {"message": f"Order {order.id} deleted successfully."}


@admin_router.get("/carts")
async def get_carts(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
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
    result = await session.execute(select(Cart).filter(Cart.id == cart_id))
    cart_item = result.scalars().first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found.")
    await session.delete(cart_item)
    await session.commit()
    return {"message": f"Cart item {cart_item.id} deleted successfully."}


@admin_router.delete("/dish-categories")
async def delete_dish_category(
        name: str,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    existing_category = await session.execute(
        select(DishCategory).where(DishCategory.name == name)
    )
    existing_category = existing_category.scalars().first()

    if not existing_category:
        raise HTTPException(status_code=400, detail="Dish category with this name doesn't exist")

    try:
        await session.delete(existing_category)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error deleting dish category")
    return {"Dish category was deleted": DishCategorySchema.from_orm(existing_category)}


@admin_router.post("/dish-categories", response_model=DishCategorySchema)
async def create_dish_category(
        name: str,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    existing_category = await session.execute(
        select(DishCategory).where(DishCategory.name == name)
    )
    existing_category = existing_category.scalars().first()

    if existing_category:
        raise HTTPException(
            status_code=400, detail="Dish category with this name already exists"
        )

    new_category = DishCategory(name=name)

    try:
        session.add(new_category)
        await session.commit()
        await session.refresh(new_category)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error adding dish category")

    return DishCategorySchema.from_orm(new_category)


@admin_router.patch("/dish-categories", response_model=DishCategorySchema)
async def update_dish_category_by_name(
        old_name: str,
        new_name: str,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    result = await session.execute(select(DishCategory).where(DishCategory.name == old_name))
    category = result.scalars().first()

    if not category:
        raise HTTPException(status_code=404, detail="Dish category not found")

    existing_category = await session.execute(select(DishCategory).where(DishCategory.name == new_name))
    existing_category = existing_category.scalars().first()

    if existing_category:
        raise HTTPException(status_code=400, detail="Dish category with this name already exists")

    category.name = new_name

    try:
        await session.commit()
        await session.refresh(category)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error patching dish category")

    return DishCategorySchema.from_orm(category)
