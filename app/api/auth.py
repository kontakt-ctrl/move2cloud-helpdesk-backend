import logging
from fastapi import APIRouter, HTTPException, status, Depends, Security
from pydantic import BaseModel, EmailStr
from sqlalchemy.future import select
from sqlmodel import Session
from app.models.user import User
from app.core.db import get_session
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

logger = logging.getLogger("app.error")
router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int, email: str):
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_exp_minutes)
    to_encode = {
        "sub": email,
        "user_id": user_id,
        "exp": expire
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""

class RegisterResponse(BaseModel):
    msg: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    try:
        result = session.exec(select(User).where(User.email == data.email))
        user = result.first()
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return RegisterResponse(msg="Registration successful")
    except Exception as e:
        logger.error(f"Błąd rejestracji użytkownika {data.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    try:
        result = session.exec(select(User).where(User.email == data.email))
        user = result.first()
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(user_id=user.id, email=user.email)
        return TokenResponse(access_token=token)
    except Exception as e:
        logger.error(f"Błąd logowania użytkownika {data.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/me", response_model=RegisterRequest)
def get_me(token: str = Security(oauth2_scheme), session: Session = Depends(get_session)):
    payload = decode_token(token)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return RegisterRequest(email=user.email, full_name=user.full_name, password="")
