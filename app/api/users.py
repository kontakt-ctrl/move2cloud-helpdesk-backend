import logging
from fastapi import APIRouter, Depends, HTTPException, Path, Body
from app.models.user import User
from app.core.security import decode_access_token, verify_password, hash_password
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from sqlalchemy import select as sqlalchemy_select
from app.core.db import get_session
from pydantic import BaseModel, EmailStr
from typing import Optional

logger = logging.getLogger("app.error")

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = session.exec(
            select(User).where(User.email == payload["sub"])
        ).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=404, detail="User not found or inactive")
        return user
    except Exception as e:
        logger.error("Błąd pobierania aktualnego użytkownika", exc_info=True)
        raise

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    try:
        return {
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active
        }
    except Exception as e:
        logger.error("Błąd pobierania danych użytkownika", exc_info=True)
        raise

@router.get("/")
def users_list(current: User = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        if current.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")
        result = session.exec(sqlalchemy_select(User))
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.error("Błąd pobierania listy użytkowników", exc_info=True)
        raise

# === Profile update ===

class ProfileUpdateRequest(BaseModel):
    full_name: str

@router.patch("/me", summary="Aktualizuj dane profilu")
def update_profile(
    data: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        user.full_name = data.full_name
        session.add(user)
        session.commit()
        session.refresh(user)
        return {
            "msg": "Profil został zaktualizowany",
            "full_name": user.full_name
        }
    except Exception as e:
        logger.error("Błąd aktualizacji profilu", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# === Password change (self) ===

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/me/change-password", summary="Zmień hasło użytkownika")
def change_password(
    data: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        if not verify_password(data.old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Stare hasło jest nieprawidłowe")
        user.hashed_password = hash_password(data.new_password)
        session.add(user)
        session.commit()
        return {"msg": "Hasło zostało zmienione"}
    except Exception as e:
        logger.error("Błąd zmiany hasła", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# === Admin PATCH /users/{id} ===

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

@router.patch("/{user_id}", summary="Aktualizuj dane użytkownika (admin)")
def admin_update_user(
    user_id: int = Path(..., description="ID użytkownika"),
    data: UserUpdateRequest = Body(...),
    current: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        if current.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")

        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if data.full_name is not None:
            user.full_name = data.full_name
        if data.email is not None:
            # Sprawdź, czy inny użytkownik nie ma już takiego e-maila
            existing = session.exec(select(User).where(User.email == data.email, User.id != user_id)).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already in use")
            user.email = data.email
        if data.role is not None:
            user.role = data.role
        if data.is_active is not None:
            user.is_active = data.is_active

        session.add(user)
        session.commit()
        session.refresh(user)

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active
        }
    except Exception as e:
        logger.error(f"Błąd aktualizacji użytkownika {user_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# === Admin POST /users/{id}/reset-password ===

class ResetPasswordRequest(BaseModel):
    new_password: str

@router.post("/{user_id}/reset-password", summary="Resetuj hasło użytkownika (admin)")
def reset_password(
    user_id: int = Path(..., description="ID użytkownika"),
    data: ResetPasswordRequest = Body(...),
    current: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        if current.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.hashed_password = hash_password(data.new_password)
        session.add(user)
        session.commit()
        return {"msg": "Hasło zostało zresetowane"}
    except Exception as e:
        logger.error(f"Błąd resetowania hasła użytkownika {user_id}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
