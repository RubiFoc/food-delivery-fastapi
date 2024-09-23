from pydantic.v1 import BaseSettings


class FastAPISettings(BaseSettings):
    host: str
    port: int

    class Config:
        env_prefix = "API_"
        env_file = ".env"


fastapi_settings = FastAPISettings()
