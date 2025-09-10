import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

logger = logging.getLogger("app.error")

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(data: RegisterRequest):
    try:
        if await User.find_one(User.email == data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        await user.insert()
        return {"msg": "Registration successful"}
    except Exception as e:
        logger.error(f"Błąd rejestracji użytkownika {data.email}: {e}", exc_info=True)
        raise

@router.post("/login")
async def login(data: LoginRequest):
    try:
        user = await User.find_one(User.email == data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": str(user.id), "role": user.role})
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Błąd logowania użytkownika {data.email}: {e}", exc_info=True)
        raise
