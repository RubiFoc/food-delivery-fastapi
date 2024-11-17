from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import FastAPIUsers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from auth.database import get_async_session
from dependencies import get_current_superuser
from models.delivery import User
from schemas.user import UserCreate, UserRead
from auth.auth import auth_backend
from auth.manager import get_admin_manager, AdminManager

# Создаем роутер для администраторов
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Настраиваем FastAPIUsers для администраторов
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
        current_user: User = Depends(get_current_superuser),  # Ensure the current user is a superuser
):
    """
    Register a new admin. This action can only be performed by an existing admin.
    """
    # Check if the current user is a superuser (admin)
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an existing admin can create another admin.")

    # Proceed with the user creation
    user = await admin_manager.create(user_create, request=request)
    return user


@admin_router.put("/block_user/{user_id}")
async def block_user(
        user_id: int,
        current_user: User = Depends(get_current_superuser),  # Ensure the user is an admin
        session: AsyncSession = Depends(get_async_session),
):
    """
    Block (deactivate) a user by setting is_active to False.
    This can only be done by an admin.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can block users.")

    result = await session.execute(select(User).filter(User.id == user_id))
    user_to_block = result.scalars().first()

    if user_to_block is None:
        raise HTTPException(status_code=404, detail="User not found.")

    user_to_block.is_active = False

    await session.commit()

    return {"message": f"User {user_to_block.username} has been blocked."}


@admin_router.put("/unblock_user/{user_id}")
async def unblock_user(
        user_id: int,
        current_user: User = Depends(get_current_superuser),  # Ensure the user is an admin
        session: AsyncSession = Depends(get_async_session),
):
    """
    Unblock a user by setting is_active to True.
    This can only be done by an admin.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only an admin can unblock users.")

    # Get the user to be unblocked
    result = await session.execute(select(User).filter(User.id == user_id))
    user_to_unblock = result.scalars().first()

    if user_to_unblock is None:
        raise HTTPException(status_code=404, detail="User not found.")

    if user_to_unblock.is_active is True:
        raise HTTPException(status_code=400, detail="User is not blocked.")

    # Unblock the user by setting is_active to True
    user_to_unblock.is_active = True

    # Commit the changes to the database
    await session.commit()

    return {"message": f"User {user_to_unblock.username} has been unblocked."}
