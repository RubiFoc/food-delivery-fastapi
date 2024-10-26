from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from auth.database import get_async_session
from models.delivery import DishCategory, Dish, Customer, Cart, CartDishAssociation
from schemas.delivery import DishSchema, DishCategorySchema, CartSchema

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/healthcheck/db")
async def db_healthcheck(session: AsyncSession = Depends(get_async_session)):
    try:
        # Простой запрос для проверки соединения
        result = await session.execute(text("SELECT version();"))
        version = result.scalar()
        return {"status": "success", "postgres_version": version}
    except Exception as e:
        return {"status": "error", "details": str(e)}


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
async def add_dish(dish: DishSchema, session: AsyncSession = Depends(get_async_session)):
    category_query = await session.execute(select(DishCategory).where(DishCategory.id == dish.category_id))
    category = category_query.scalars().first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    new_dish = Dish(
        name=dish.name,
        price=dish.price,
        weight=dish.weight,
        category_id=dish.category_id,
        rating=0,
        number_of_marks=0,
        profit=dish.profit,
        time_of_preparing=dish.time_of_preparing,
        restaurant_id=1
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


@router.post("/cart/{customer_id}/add-dish", response_model=CartSchema)
async def add_dish_to_cart(
        customer_id: int,
        dish_id: int,
        quantity: int,
        session: AsyncSession = Depends(get_async_session)
):
    # Проверка существования клиента
    customer = await session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Проверка существования блюда
    dish = await session.get(Dish, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    # Поиск корзины или создание новой
    cart_query = await session.execute(select(Cart).where(Cart.customer_id == customer_id))
    cart = cart_query.scalars().first()

    if not cart:
        cart = Cart(customer_id=customer_id)
        session.add(cart)
        await session.flush()  # чтобы получить id для нового объекта cart

    # Добавление или обновление блюда в корзине
    association_query = await session.execute(
        select(CartDishAssociation)
        .where(CartDishAssociation.cart_id == cart.id, CartDishAssociation.dish_id == dish_id)
    )
    association = association_query.scalars().first()

    if association:
        association.quantity += quantity  # обновляем количество
    else:
        new_association = CartDishAssociation(cart_id=cart.id, dish_id=dish_id, quantity=quantity)
        session.add(new_association)

    # Сохранение изменений
    await session.commit()
    await session.refresh(cart, ["dishes"])  # Загружаем связанные данные для избежания ленивой загрузки

    return CartSchema.from_orm(cart)

