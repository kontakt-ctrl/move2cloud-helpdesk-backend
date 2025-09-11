import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.category import Category
from app.api.users import get_current_user
from pydantic import BaseModel
from sqlmodel import Session
from app.core.db import SessionLocal

logger = logging.getLogger("app.error")

router = APIRouter(prefix="/categories", tags=["categories"])

class CategoryIn(BaseModel):
    name: str

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@router.get("/")
def list_categories(session: Session = Depends(get_session)):
    try:
        return session.exec(Category.select()).all()
    except Exception as e:
        logger.error("Błąd pobierania kategorii", exc_info=True)
        raise

@router.post("/")
def create_category(data: CategoryIn, user=Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")
        if session.exec(Category.select().where(Category.name == data.name)).first():
            raise HTTPException(status_code=400, detail="Category exists")
        cat = Category(name=data.name)
        session.add(cat)
        session.commit()
        session.refresh(cat)
        return cat
    except Exception as e:
        logger.error("Błąd tworzenia kategorii", exc_info=True)
        raise
