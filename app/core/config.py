import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Wczytaj zmienne z pliku .env (ładowanie na starcie)
load_dotenv()

class Settings(BaseSettings):
    # Teraz wartości będą poprawnie pobierane z .env lub systemowych env
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/helpdesk")
    jwt_secret: str = os.getenv("JWT_SECRET", "supersecretkey")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_exp_minutes: int = int(os.getenv("JWT_EXP_MINUTES", 60 * 24))
    
    # SMTP configuration for email sending
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", 587))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_pass: str = os.getenv("SMTP_PASS", "")

settings = Settings()
