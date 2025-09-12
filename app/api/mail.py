import logging
import aiosmtplib
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings

logger = logging.getLogger("app.error")
router = APIRouter(prefix="/mail", tags=["mail"])


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str = "Wiadomość z systemu helpdesk"
    body: str


class EmailResponse(BaseModel):
    success: bool
    message: str


@router.post("/send", response_model=EmailResponse)
async def send_email(email_request: EmailRequest):
    """
    Wysyła e-mail na podany adres z określoną treścią i tematem.
    """
    # Sprawdź czy konfiguracja SMTP jest ustawiona
    if not all([settings.smtp_host, settings.smtp_user, settings.smtp_pass]):
        logger.error("SMTP configuration is incomplete")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMTP configuration is not properly set up"
        )

    try:
        # Utworz wiadomość
        message = MIMEMultipart()
        message["From"] = settings.smtp_user
        message["To"] = email_request.to
        message["Subject"] = email_request.subject

        # Dodaj treść wiadomości
        body = MIMEText(email_request.body, "plain", "utf-8")
        message.attach(body)

        # Wyślij e-mail
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            start_tls=True,
            username=settings.smtp_user,
            password=settings.smtp_pass,
        )

        logger.info(f"Email sent successfully to {email_request.to}")
        return EmailResponse(
            success=True,
            message=f"Email sent successfully to {email_request.to}"
        )

    except aiosmtplib.SMTPException as e:
        error_msg = f"SMTP error while sending email to {email_request.to}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email due to SMTP error"
        )
    except Exception as e:
        error_msg = f"Unexpected error while sending email to {email_request.to}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email due to unexpected error"
        )