from fastapi import FastAPI

from routers.users import router as auth_router
from routers.delivery import router as courses_router
from settings.fastapi_settings import fastapi_settings

app = FastAPI(
    title="Food delivery"
)

app.include_router(auth_router)
app.include_router(courses_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=fastapi_settings.host, port=fastapi_settings.port)
