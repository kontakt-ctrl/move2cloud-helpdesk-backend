import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.priority import Priority
from app.api.users import get_current_user
from pydantic import BaseModel

logger = logging.getLogger("app.error")

router = APIRouter(prefix="/priorities", tags=["priorities"])

class PriorityIn(BaseModel):
    name: str
    level: int

@router.get("/")
async def list_priorities():
    try:
        return await Priority.find_all().to_list()
    except Exception as e:
        logger.error("Błąd pobierania priorytetów", exc_info=True)
        raise

@router.post("/")
async def create_priority(data: PriorityIn, user=Depends(get_current_user)):
    try:
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")
        if await Priority.find_one(Priority.name == data.name):
            raise HTTPException(status_code=400, detail="Priority exists")
        prio = Priority(name=data.name, level=data.level)
        await prio.insert()
        return prio
    except Exception as e:
        logger.error("Błąd tworzenia priorytetu", exc_info=True)
        raise
