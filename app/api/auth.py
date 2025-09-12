import logging
import random
from fastapi import APIRouter, HTTPException, status, Depends, Security
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select  # <-- zmiana tutaj!
from app.models.user import User
from app.core.db import get_session
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from app.api.mail import send_mail  # import funkcji mailowej

logger = logging.getLogger("app.error")
router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# In-memory reset code store: {email: (code, expiry_datetime)}
reset_codes = {}

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

# ... (istniejące klasy i endpointy login/register/get_me)

class ResetPasswordRequest(BaseModel):
    email: EmailStr

@router.post("/reset-password/request")
def request_reset_password(data: ResetPasswordRequest, session: Session = Depends(get_session)):
    try:
        result = session.exec(select(User).where(User.email == data.email))
        user = result.first()
        if not user:
            # Nie ujawniamy, czy konto istnieje
            return {"msg": "Jeśli konto istnieje, wysłano e-mail z kodem resetu."}
        # Generujemy kod 6-cyfrowy
        code = "{:06d}".format(random.randint(0, 999999))
        expiry = datetime.utcnow() + timedelta(minutes=15)
        reset_codes[data.email] = (code, expiry)
        # Wyślij e-mail
        mail_body = f"Twój kod resetu hasła to: {code}\nWażny przez 15 minut."
        send_mail(
            data=type("obj", (), {"to": data.email, "subject": "Reset hasła - Helpdesk", "body": mail_body})()
        )
        return {"msg": "Jeśli konto istnieje, wysłano e-mail z kodem resetu."}
    except Exception as e:
        logger.error(f"Błąd generowania kodu resetu dla {data.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Błąd resetu hasła")

class ResetPasswordConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str

@router.post("/reset-password/confirm")
def confirm_reset_password(data: ResetPasswordConfirm, session: Session = Depends(get_session)):
    try:
        entry = reset_codes.get(data.email)
        if not entry:
            raise HTTPException(status_code=400, detail="Niepoprawny kod lub e-mail.")
        code, expiry = entry
        if datetime.utcnow() > expiry or data.code != code:
            raise HTTPException(status_code=400, detail="Niepoprawny kod lub kod wygasł.")
        result = session.exec(select(User).where(User.email == data.email))
        user = result.first()
        if not user:
            raise HTTPException(status_code=404, detail="Nie znaleziono użytkownika.")
        user.hashed_password = hash_password(data.new_password)
        session.add(user)
        session.commit()
        del reset_codes[data.email]
        return {"msg": "Hasło zostało zresetowane. Możesz się zalogować nowym hasłem."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd resetu hasła dla {data.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Błąd resetu hasła")
