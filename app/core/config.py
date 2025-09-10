import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.environ.get("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/helpdesk")
    jwt_secret: str = os.environ.get("JWT_SECRET", "supersecretkey")
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60 * 24

settings = Settings()
