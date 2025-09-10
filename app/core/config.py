import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = os.environ.get("MONGODB_URL", "")
    jwt_secret: str = os.environ.get("JWT_SECRET", "supersecretkey")
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60 * 24

settings = Settings()