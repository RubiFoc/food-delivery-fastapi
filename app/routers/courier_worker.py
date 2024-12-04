from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import FastAPIUsers
from schemas.user import UserCreate, UserRead
from auth.auth import auth_backend
from auth.manager import get_courier_worker_manager

courier_worker_router = APIRouter(prefix="/courier_worker", tags=["courier_worker"])

fastapi_users_courier_worker = FastAPIUsers(
    get_courier_worker_manager,
    [auth_backend],
)

courier_worker_router.include_router(
    fastapi_users_courier_worker.get_register_router(UserRead, UserCreate),
    prefix="/register",
)
