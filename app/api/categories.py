import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.category import Category
from app.api.users import get_current_user
from pydantic import BaseModel

logger = logging.getLogger("app.error")

router = APIRouter(prefix="/categories", tags=["categories"])

class CategoryIn(BaseModel):
    name: str

@router.get("/")
async def list_categories():
    try:
        return await Category.find_all().to_list()
    except Exception as e:
        logger.error("Błąd pobierania kategorii", exc_info=True)
        raise

@router.post("/")
async def create_category(data: CategoryIn, user=Depends(get_current_user)):
    try:
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")
        if await Category.find_one(Category.name == data.name):
            raise HTTPException(status_code=400, detail="Category exists")
        cat = Category(name=data.name)
        await cat.insert()
        return cat
    except Exception as e:
        logger.error("Błąd tworzenia kategorii", exc_info=True)
        raise
