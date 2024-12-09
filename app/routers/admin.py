from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi_users import FastAPIUsers
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from auth.database import get_async_session
from dependencies import get_current_superuser
from models.delivery import User, Dish, DishCategory, OrderStatus, Customer, Courier
from schemas.delivery import DishSchema, DishCategorySchema
from schemas.order import OrderStatusUpdate
from schemas.user import UserCreate, UserRead, UserUpdate, CustomerUpdate, CourierUpdate
from auth.auth import auth_backend
from auth.manager import get_admin_manager, AdminManager

admin_router = APIRouter(prefix="/admins", tags=["admin"])

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


@admin_router.get("/order_statuses")
async def get_order_statuses(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    result = await session.execute(select(OrderStatus).options(joinedload(OrderStatus.order)))
    order_statuses = result.scalars().all()
    return order_statuses


# Изменение статуса заказа
@admin_router.put("/order_status/{order_id}")
async def update_order_status(
        order_id: int,
        order_status_update: OrderStatusUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    result = await session.execute(select(OrderStatus).filter(OrderStatus.order_id == order_id))
    order_status = result.scalars().first()
    if not order_status:
        raise HTTPException(status_code=404, detail="Order status not found.")

    for field, value in order_status_update.dict(exclude_unset=True).items():
        setattr(order_status, field, value)

    await session.commit()
    return {"message": f"Order status for order {order_id} updated successfully."}


# Удаление статуса заказа
@admin_router.delete("/order_status/{order_id}")
async def delete_order_status(
        order_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    order_status_to_delete = await session.get(OrderStatus, order_id)
    if not order_status_to_delete:
        raise HTTPException(status_code=404, detail="Order status not found")

    await session.delete(order_status_to_delete)
    await session.commit()

    return {"message": "Order status successfully deleted"}


@admin_router.get("/customers")
async def get_customers(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    """
    Получить всех пользователей с ролью Customer.
    """
    result = await session.execute(
        select(Customer).options(joinedload(Customer.user), joinedload(Customer.role))
    )
    customers = result.scalars().all()
    return customers


@admin_router.get("/customer/{customer_id}")
async def get_customer(
        customer_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    """
    Получить информацию о конкретном Customer по ID.
    """
    result = await session.execute(
        select(Customer).filter(Customer.id == customer_id)
        .options(joinedload(Customer.user), joinedload(Customer.role))
    )
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return customer


@admin_router.put("/customer/{customer_id}")
async def update_customer(
        customer_id: int,
        customer_update: CustomerUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    """
    Обновить данные о Customer по ID.
    """
    result = await session.execute(select(Customer).filter(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    # Обновляем поля из CustomerUpdate
    update_data = customer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    await session.commit()
    return {"message": f"Customer {customer_id} updated successfully."}

@admin_router.get("/couriers")
async def get_couriers(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    """
    Получить всех пользователей с ролью Courier.
    """
    result = await session.execute(
        select(Courier).options(joinedload(Courier.user), joinedload(Courier.role))
    )
    couriers = result.scalars().all()
    return couriers


@admin_router.get("/courier/{courier_id}")
async def get_courier(
        courier_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    """
    Получить информацию о конкретном Courier по ID.
    """
    result = await session.execute(
        select(Courier).filter(Courier.id == courier_id)
        .options(joinedload(Courier.user), joinedload(Courier.role))
    )
    courier = result.scalars().first()
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found.")
    return courier


@admin_router.put("/courier/{courier_id}")
async def update_courier(
        courier_id: int,
        courier_update: CourierUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_superuser)
):
    """
    Обновить данные о Courier по ID, включая количество оценок.
    """
    result = await session.execute(select(Courier).filter(Courier.id == courier_id))
    courier = result.scalars().first()
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found.")

    # Обновляем поля из CourierUpdate
    update_data = courier_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(courier, field):
            setattr(courier, field, value)

    # Если передано количество оценок, обновляем его
    if courier_update.number_of_marks is not None:
        courier.number_of_marks = courier_update.number_of_marks

    await session.commit()
    return {"message": f"Courier {courier_id} updated successfully."}
