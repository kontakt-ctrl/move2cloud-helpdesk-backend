import os
import logging
import smtplib
from email.mime.text import MIMEText
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

logger = logging.getLogger("app.error")
router = APIRouter(prefix="/mail", tags=["mail"])

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_ADDR = SMTP_USER

class MailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str
    html: bool = False  # NOWE pole

@router.post("/send")
def send_mail(data: MailRequest):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        logger.error("Brak konfiguracji SMTP (SMTP_USER/SMTP_PASS)")
        raise HTTPException(status_code=500, detail="SMTP not configured")
    try:
        # Ustal MIME typu maila na html jeśli html=True, w przeciwnym razie text/plain
        mime_type = "html" if data.html else "plain"
        msg = MIMEText(data.body, mime_type, "utf-8")
        msg["Subject"] = data.subject
        msg["From"] = FROM_ADDR
        msg["To"] = data.to

        # OVH wymaga SMTP_SSL na porcie 465, bez starttls!
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_ADDR, [data.to], msg.as_string())

        return {"msg": "E-mail wysłany"}
    except Exception as e:
        logger.error(f"Błąd wysyłki e-maila do {data.to}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Błąd wysyłki e-maila")
