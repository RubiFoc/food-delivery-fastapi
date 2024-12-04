from datetime import datetime, timedelta
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import text, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from auth.database import get_async_session
from config import YANDEX_API_KEY
from dependencies import get_current_user
from models.delivery import DishCategory, Dish, Customer, Cart, CartDishAssociation, OrderDishAssociation, Order, \
    OrderStatus, User
from schemas.cart import CartDishAddRequest
from schemas.delivery import DishSchema, DishCategorySchema, CartSchema, OrderSchema


router = APIRouter(prefix="/api", tags=["api"])


@router.get("/dish-categories")
async def get_all_dish_categories(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DishCategory))
    categories = result.scalars().all()

    if not categories:
        raise HTTPException(status_code=404, detail="No dish categories found")

    return [DishCategorySchema.from_orm(c) for c in categories]


@router.post("/dish-categories", response_model=DishCategorySchema)
async def create_dish_category(
        name: str,
        session: AsyncSession = Depends(get_async_session)
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


@router.delete("/dish-categories")
async def delete_dish_category(name: str, session: AsyncSession = Depends(get_async_session)):
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


@router.patch("/dish-categories", response_model=DishCategorySchema)
async def update_dish_category_by_name(
        old_name: str,
        new_name: str,
        session: AsyncSession = Depends(get_async_session)
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


@router.get("/dishes")
async def get_all_dishes(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Dish))
    dishes = result.scalars().all()

    if not dishes:
        raise HTTPException(status_code=404, detail="No dishes found")

    return [DishSchema.from_orm(d) for d in dishes]


@router.post("/dishes", response_model=DishSchema)
async def add_dish(
        name: str,
        price: float,
        weight: float,
        category_id: int,
        profit: float,
        time_of_preparing: int,
        image: UploadFile = File(...),
        session: AsyncSession = Depends(get_async_session)
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


@router.get("/dishes/category/{category_name}")
async def get_dishes_by_category(category_name: str, session: AsyncSession = Depends(get_async_session)):
    result_category = await session.execute(select(DishCategory).where(DishCategory.name == category_name))
    category = result_category.scalars().first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    result_dishes = await session.execute(
        select(Dish).where(Dish.category_id == category.id).options(joinedload(Dish.category))
    )
    dishes = result_dishes.scalars().all()

    if not dishes:
        raise HTTPException(status_code=404, detail="No dishes found in this category")

    return [DishSchema.from_orm(d) for d in dishes]


@router.delete("/dishes")
async def delete_dish(id: int, session: AsyncSession = Depends(get_async_session)):
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


@router.patch("/dishes/{dish_id}", response_model=DishSchema)
async def update_dish(
        dish_id: int,
        new_dish: DishSchema,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Dish).where(Dish.id == dish_id)
    result = await session.execute(query)
    dish = result.scalar_one_or_none()

    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    update_data = new_dish.dict(exclude_unset=True, exclude={"id"})
    for field, value in update_data.items():
        setattr(dish, field, value)

    await session.commit()
    await session.refresh(dish)

    return dish


@router.get("/dishes/{dish_id}", response_model=DishSchema)
async def get_dish_by_id(dish_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Dish).where(Dish.id == dish_id))
    dish = result.scalars().first()

    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    return DishSchema.from_orm(dish)


@router.get("/cart", response_model=CartSchema)
async def get_cart(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    cart_query = await session.execute(
        select(Cart)
        .where(Cart.customer_id == current_user.id)
        .options(joinedload(Cart.dishes).joinedload(CartDishAssociation.dish))
    )
    cart = cart_query.scalars().first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    return CartSchema.from_orm(cart)


@router.post("/cart/add-dish", response_model=CartSchema)
async def add_dish_to_cart(
        request: CartDishAddRequest,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=404, detail="Customer not found")

    dish = await session.get(Dish, request.dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    cart_query = await session.execute(select(Cart).where(Cart.customer_id == current_user.id))
    cart = cart_query.scalars().first()

    if not cart:
        cart = Cart(customer_id=current_user.id)
        session.add(cart)
        await session.flush()

    association_query = await session.execute(
        select(CartDishAssociation)
        .where(CartDishAssociation.cart_id == cart.id, CartDishAssociation.dish_id == request.dish_id)
    )
    association = association_query.scalars().first()

    if association:
        association.quantity += request.quantity
    else:
        new_association = CartDishAssociation(cart_id=cart.id, dish_id=request.dish_id, quantity=request.quantity)
        session.add(new_association)

    await session.commit()
    await session.refresh(cart, ["dishes"])

    return CartSchema.from_orm(cart)


@router.post("/cart/create-order", response_model=OrderSchema)
async def create_order_from_cart(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    cart_query = await session.execute(
        select(Cart)
        .where(Cart.customer_id == current_user.id)
        .options(joinedload(Cart.dishes).joinedload(CartDishAssociation.dish))
    )
    cart = cart_query.scalars().first()

    if not cart or not cart.dishes:
        raise HTTPException(status_code=404, detail="Cart is empty or not found")

    total_price = sum(dish.quantity * dish.dish.price for dish in cart.dishes)
    total_weight = sum(dish.quantity * dish.dish.weight for dish in cart.dishes)

    customer_query = await session.execute(select(Customer).filter(Customer.id == current_user.id))
    customer = customer_query.scalars().first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if customer.balance < total_price:
        raise HTTPException(status_code=400, detail="Insufficient balance to complete the order")

    customer.balance -= total_price
    session.add(customer)

    location = customer.location
    if not location:
        raise HTTPException(status_code=404, detail="Customer location not found")

    new_order = Order(
        price=total_price,
        weight=total_weight,
        time_of_creation=datetime.now(),
        customer_id=current_user.id,
        location=location,
        restaurant_id=1
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

    order_status = OrderStatus(order_id=new_order.id)
    session.add(order_status)

    for cart_dish in cart.dishes:
        await session.delete(cart_dish)

    await session.commit()
    await session.refresh(new_order)

    return OrderSchema.from_orm(new_order)


@router.post("/customer/update_location", summary="Обновить местоположение пользователя")
async def update_customer_location(
        address: str,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    address = "Минск, " + address
    base_url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": YANDEX_API_KEY,
        "geocode": address,
        "format": "json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе к Яндекс.Картам")

    data = response.json()
    try:
        geo_objects = data["response"]["GeoObjectCollection"]["featureMember"]
        if not geo_objects:
            raise HTTPException(status_code=404, detail="Не найдено местоположение для указанного адреса")

        for geo_object in geo_objects:
            coordinates_str = geo_object["GeoObject"]["Point"]["pos"]

        geo_object = geo_objects[0]["GeoObject"]
        coordinates_str = geo_object["Point"]["pos"]
        longitude, latitude = map(float, coordinates_str.split(" "))

        result = await session.execute(select(Customer).filter(Customer.id == current_user.id))
        customer = result.scalar_one_or_none()

        if not customer:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        customer.location = f"{latitude}, {longitude}"

        await session.commit()
        return {"customer_id": current_user.id, "location": customer.location}

    except (IndexError, KeyError):
        raise HTTPException(status_code=404, detail="Не удалось найти координаты для указанного адреса")
