from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import FastAPIUsers
from starlette.requests import Request

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

# Проверка аутентификации в других местах
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
