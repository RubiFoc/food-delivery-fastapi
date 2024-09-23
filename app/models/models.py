from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import MetaData, Column, Integer, JSON, String, Table, ForeignKey, DateTime, Boolean

metadata = MetaData()

role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("permissions", JSON)
)

user = Table(
    "user",
    metadata,
    Column("id", Integer, unique=True, primary_key=True),
    Column("email", EmailStr, nullable=False, unique=True),
    Column("username", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("role_id", Integer, ForeignKey(role.c.id), nullable=False),
    Column("registration_date", DateTime, nullable=False, default=datetime.utcnow),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)
