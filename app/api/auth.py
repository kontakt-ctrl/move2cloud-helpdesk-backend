from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.core.db import async_session
import logging

logger = logging.getLogger("app.error")
router = APIRouter(prefix="/auth", tags=["auth"])

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@router.post("/register")
async def register(data: RegisterRequest, session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = User(email=data.email, hashed_password=hash_password(data.password), full_name=data.full_name)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return {"msg": "Registration successful"}
    except Exception as e:
        logger.error(f"Błąd rejestracji użytkownika {data.email}: {e}", exc_info=True)
        raise
