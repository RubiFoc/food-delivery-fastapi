from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers.courier import courier_router
from routers.courier_worker import courier_worker_router
from routers.users import router as auth_router
from routers.delivery import router as delivery_router
from routers.admin import admin_router
from routers.kitchen_worker import kitchen_worker_router
from settings.fastapi_settings import fastapi_settings

app = FastAPI(
    title="Food delivery"
)

app.include_router(courier_worker_router)
app.include_router(auth_router)
app.include_router(delivery_router)
app.include_router(admin_router)
app.include_router(kitchen_worker_router)
app.include_router(courier_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],  # Укажите ваш фронтенд-домен
    allow_credentials=True,
    allow_methods=["*"],  # Или конкретные методы, например, ["GET", "POST"]
    allow_headers=["*"],  # Или конкретные заголовки
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=fastapi_settings.host, port=fastapi_settings.port)
