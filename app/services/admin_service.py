from fastapi import Depends

from dependencies import fastapi_users
from models.delivery import User


def get_current_user(user: User = Depends(fastapi_users.current_user())):
    return user
