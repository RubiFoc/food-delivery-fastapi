from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "postgres")
DB_NAME = os.environ.get("DB_NAME", "db")
DB_PORT = os.environ.get("DB_PORT", "5434")
DOCKER_PORT = "5432"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SECRET = os.environ.get("SECRET", "ajsdio1u90uojahsdasdlaskfaljsf")
SECRET_MANAGER = os.environ.get("SECRET_MANAGER", "kjadskjahsoijo1i90u2rhskhqf82yhrh1nd")
API_HOST = "localhost"
API_PORT = 8000

YANDEX_API_KEY = "4c49979c-a82a-4fda-863b-38812df1351d"
