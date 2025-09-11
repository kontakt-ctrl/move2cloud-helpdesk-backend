from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.database_url
print("=== DATABASE_URL ===")
print(DATABASE_URL)
print("====================")

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    with engine.begin() as conn:
        SQLModel.metadata.create_all(conn)
