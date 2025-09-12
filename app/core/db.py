from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from app.models.password_reset import PasswordResetToken  # <-- DODANE

DATABASE_URL = settings.database_url
print("=== DATABASE_URL ===")
print(DATABASE_URL)
print("====================")

engine = create_engine(DATABASE_URL, echo=True, future=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    with engine.begin() as conn:
        SQLModel.metadata.create_all(conn)
