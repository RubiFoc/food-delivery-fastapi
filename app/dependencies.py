from fastapi import Depends
from fastapi_users import FastAPIUsers

from auth.auth import auth_backend
from auth.manager import get_user_manager
from models.delivery import User

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


def get_current_user(user: User = Depends(fastapi_users.current_user())):
    return user


def get_current_superuser(user: User = Depends(fastapi_users.current_user(active=True, superuser=True))):
    return user
