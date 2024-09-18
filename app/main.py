from fastapi import FastAPI

from routers.routers import router
from config.fastapi_settings import fastapi_settings

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=fastapi_settings.host, port=fastapi_settings.port)
