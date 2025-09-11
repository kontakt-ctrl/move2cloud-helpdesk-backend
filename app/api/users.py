import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.core.security import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.core.db import get_session

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
        users = session.exec(select(User)).all()
        return users
    except Exception as e:
        logger.error("Błąd pobierania listy użytkowników", exc_info=True)
        raise
