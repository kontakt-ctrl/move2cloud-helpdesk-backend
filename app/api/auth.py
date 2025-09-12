import logging
import random
import string
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.core.db import get_session
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
from datetime import datetime, timedelta
from app.api.mail import send_mail

logger = logging.getLogger("app.error")
router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# --- RESET PASSWORD MODELS ---

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str

# --- RESET PASSWORD ENDPOINTS ---

@router.post("/reset-password/request")
def request_reset_password(
    data: ResetPasswordRequest, 
    session: Session = Depends(get_session)
):
    # ZAWSZE zwracamy tę samą odpowiedź (nie ujawniamy czy user istnieje)
    msg = {"msg": "Jeśli konto istnieje, wysłano e-mail z kodem resetu."}
    try:
        user = session.exec(select(User).where(User.email == data.email)).first()
        if not user:
            return msg
        # Usuń stare, niewykorzystane tokeny
        session.exec(
            select(PasswordResetToken)
            .where(
                (PasswordResetToken.email == data.email) & 
                (PasswordResetToken.used == False)
            )
        ).delete()
        # Generuj kod 6-cyfrowy
        code = "".join(random.choices(string.digits, k=6))
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        token = PasswordResetToken(
            email=data.email,
            code=code,
            expires_at=expires_at,
            used=False
        )
        session.add(token)
        session.commit()
        # Wyślij e-mail
        mail_body = (
            f"Twój kod resetu hasła to: {code}\n"
            f"Kod ważny do: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"Jeśli nie prosiłeś o reset hasła, zignoruj tę wiadomość."
        )
        send_mail(
            data=type("obj", (), {
                "to": data.email,
                "subject": "Reset hasła - Helpdesk",
                "body": mail_body
            })()
        )
        return msg
    except Exception as e:
        logger.error(f"Błąd generowania kodu resetu dla {data.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Błąd resetu hasła")

@router.post("/reset-password/confirm")
def confirm_reset_password(
    data: ResetPasswordConfirm, 
    session: Session = Depends(get_session)
):
    try:
        token = session.exec(
            select(PasswordResetToken)
            .where(
                (PasswordResetToken.email == data.email) &
                (PasswordResetToken.code == data.code) &
                (PasswordResetToken.used == False)
            )
        ).first()
        if not token or token.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Niepoprawny lub wygasły kod.")
        user = session.exec(select(User).where(User.email == data.email)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Nie znaleziono użytkownika.")
        user.hashed_password = hash_password(data.new_password)
        session.add(user)
        token.used = True
        session.add(token)
        session.commit()
        return {"msg": "Hasło zostało zresetowane. Możesz się zalogować nowym hasłem."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd resetu hasła dla {data.email}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Błąd resetu hasła")
