from fastapi import APIRouter, Depends, HTTPException
from app.models.priority import Priority
from app.api.users import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/priorities", tags=["priorities"])

class PriorityIn(BaseModel):
    name: str
    level: int

@router.get("/")
async def list_priorities():
    return await Priority.find_all().to_list()

@router.post("/")
async def create_priority(data: PriorityIn, user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    if await Priority.find_one(Priority.name == data.name):
        raise HTTPException(status_code=400, detail="Priority exists")
    prio = Priority(name=data.name, level=data.level)
    await prio.insert()
    return prio