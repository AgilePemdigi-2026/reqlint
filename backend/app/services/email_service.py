"""Shared SMTP email delivery service for Password Reset and Contact Us."""
import asyncio
import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from typing import Optional

from app.core.config import settings

logger = logging.getLogger("reqlint.email_service")


class EmailDeliveryError(RuntimeError):
    """Raised when SMTP is not configured or delivery fails."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _clean_header(value: str) -> str:
    """Strip CR/LF to prevent SMTP header injection."""
    return value.replace("\r", " ").replace("\n", " ").strip()


class EmailService:
    @staticmethod
    def is_configured() -> bool:
        return bool((settings.SMTP_HOST or "").strip())

    @staticmethod
    async def send_email(
        *,
        to_email: str,
        subject: str,
        body: str,
        reply_to: Optional[str] = None,
    ) -> None:
        if not EmailService.is_configured():
            raise EmailDeliveryError(
                "EMAIL_NOT_CONFIGURED",
                "SMTP_HOST is not configured on the server.",
            )

        from_addr = _clean_header(settings.SMTP_FROM or "reqlint@localhost")
        from_name = _clean_header(settings.SMTP_FROM_NAME or "")
        from_header = (
            formataddr((from_name, from_addr))
            if from_name and "<" not in from_addr
            else from_addr
        )

        msg = EmailMessage()
        msg["Subject"] = _clean_header(subject)
        msg["From"] = from_header
        msg["To"] = _clean_header(to_email)
        if reply_to:
            msg["Reply-To"] = _clean_header(reply_to)
        msg.set_content(body)

        def _send() -> None:
            use_ssl = settings.SMTP_USE_SSL or int(settings.SMTP_PORT) == 465
            if use_ssl:
                with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
                    if settings.SMTP_USERNAME:
                        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                    smtp.send_message(msg)
            else:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
                    if settings.SMTP_USE_TLS:
                        smtp.starttls()
                    if settings.SMTP_USERNAME:
                        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                    smtp.send_message(msg)

        try:
            await asyncio.to_thread(_send)
        except EmailDeliveryError:
            raise
        except Exception as exc:
            logger.error(
                "SMTP email delivery failed (host=%s port=%s error=%s)",
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                type(exc).__name__,
                exc_info=True,
            )
            raise EmailDeliveryError(
                "EMAIL_DELIVERY_FAILED",
                f"Failed to deliver email via SMTP ({type(exc).__name__}).",
            ) from exc
