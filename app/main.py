from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware

from auth.auth import auth_backend
from routers.courier_worker import courier_worker_router
from routers.users import router as auth_router
from routers.delivery import router as delivery_router
from routers.admin import admin_router
from settings.fastapi_settings import fastapi_settings

app = FastAPI(
    title="Food delivery"
)

# app.add_middleware(AuthenticationMiddleware, backend=auth_backend)
app.include_router(courier_worker_router)
app.include_router(auth_router)
app.include_router(delivery_router)
app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=fastapi_settings.host, port=fastapi_settings.port)
