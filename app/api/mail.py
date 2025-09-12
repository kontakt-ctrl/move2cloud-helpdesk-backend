import logging
import smtplib
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from email.mime.text import MIMEText
import os
from app.api.users import get_current_user  # DODANE


print("SMTP_USER:", os.getenv("SMTP_USER"))
print("SMTP_PASS:", os.getenv("SMTP_PASS"))

logger = logging.getLogger("app.error")
router = APIRouter(prefix="/mail", tags=["mail"])

class SendMailRequest(BaseModel):
    to: EmailStr
    subject: str = "Wiadomość z systemu Helpdesk"
    body: str

@router.post("/send")
def send_mail(
    data: SendMailRequest,
    user=Depends(get_current_user)  # DODANE
):
    try:
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        from_addr = smtp_user or "no-reply@move2.cloud"

        if not smtp_user or not smtp_pass:
            logger.error("Brak konfiguracji SMTP (SMTP_USER/SMTP_PASS)")
            raise HTTPException(status_code=500, detail="SMTP not configured")

        msg = MIMEText(data.body, "plain", "utf-8")
        msg["Subject"] = data.subject
        msg["From"] = from_addr
        msg["To"] = data.to

        # Obsługa SSL/STARTTLS zależnie od portu
        if smtp_port == 465:
            import smtplib
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(from_addr, [data.to], msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(from_addr, [data.to], msg.as_string())

        return {"msg": "E-mail wysłany"}
    except Exception as e:
        logger.error(f"Błąd wysyłki e-maila do {data.to}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Błąd wysyłki e-maila")
