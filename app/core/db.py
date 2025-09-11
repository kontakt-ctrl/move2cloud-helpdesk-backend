from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = Session

def init_db():
    with engine.begin() as conn:
        SQLModel.metadata.create_all(conn)
