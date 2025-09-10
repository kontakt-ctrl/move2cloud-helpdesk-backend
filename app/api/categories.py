from fastapi import APIRouter, Depends, HTTPException
from app.models.category import Category
from app.api.users import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/categories", tags=["categories"])

class CategoryIn(BaseModel):
    name: str

@router.get("/")
async def list_categories():
    return await Category.find_all().to_list()

@router.post("/")
async def create_category(data: CategoryIn, user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    if await Category.find_one(Category.name == data.name):
        raise HTTPException(status_code=400, detail="Category exists")
    cat = Category(name=data.name)
    await cat.insert()
    return cat