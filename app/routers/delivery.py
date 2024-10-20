from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.database import get_async_session
from models.delivery import DishCategory, Dish
from shcemas.delivery import DishSchema, DishCategorySchema

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


@router.get("/dishes")
async def get_all_dishes(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Dish))
    dishes = result.scalars().all()

    if not dishes:
        raise HTTPException(status_code=404, detail="No dishes found")

    return [DishSchema.from_orm(d) for d in dishes]


@router.get("/dish-categories")
async def get_all_dish_categories(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(DishCategory))
    categories = result.scalars().all()

    if not categories:
        raise HTTPException(status_code=404, detail="No dish categories found")

    return [DishCategorySchema.from_orm(c) for c in categories]


@router.post("/dish-categories", response_model=DishCategorySchema)
async def create_dish_category(
        name: str,  # Принимаем имя категории как строку
        session: AsyncSession = Depends(get_async_session)
):
    # Проверяем существование категории
    existing_category = await session.execute(
        select(DishCategory).where(DishCategory.name == name)  # Используем name напрямую
    )
    existing_category = existing_category.scalars().first()

    if existing_category:
        raise HTTPException(
            status_code=400, detail="Dish category with this name already exists"
        )

    # Создание новой категории
    new_category = DishCategory(name=name)  # Создаем экземпляр модели

    try:
        session.add(new_category)  # Добавляем в сессию
        await session.commit()  # Коммитим изменения
        await session.refresh(new_category)  # Обновляем объект, чтобы получить id
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error adding dish category")

    return DishCategorySchema.from_orm(new_category)  # Возвращаем созданный объект
