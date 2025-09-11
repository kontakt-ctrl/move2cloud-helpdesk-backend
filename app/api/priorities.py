import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.priority import Priority
from app.api.users import get_current_user
from pydantic import BaseModel
from sqlmodel import Session
from app.core.db import SessionLocal

logger = logging.getLogger("app.error")

router = APIRouter(prefix="/priorities", tags=["priorities"])

class PriorityIn(BaseModel):
    name: str
    level: int

def get_session():
    with SessionLocal(bind=None) as session:
        yield session

@router.get("/")
def list_priorities(session: Session = Depends(get_session)):
    try:
        return session.exec(Priority.select()).all()
    except Exception as e:
        logger.error("Błąd pobierania priorytetów", exc_info=True)
        raise

@router.post("/")
def create_priority(data: PriorityIn, user=Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")
        if session.exec(Priority.select().where(Priority.name == data.name)).first():
            raise HTTPException(status_code=400, detail="Priority exists")
        prio = Priority(name=data.name, level=data.level)
        session.add(prio)
        session.commit()
        session.refresh(prio)
        return prio
    except Exception as e:
        logger.error("Błąd tworzenia priorytetu", exc_info=True)
        raise
