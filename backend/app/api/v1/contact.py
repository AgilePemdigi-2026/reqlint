"""Contact Us endpoint with validation, anti-spam protection, and real SMTP delivery."""
import logging
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import APIRouter, Request, status

from app.core.config import settings
from app.core.errors import AppException
from app.core.responses import success_response
from app.schemas.contact import ContactRequest
from app.services.email_service import EmailDeliveryError, EmailService

logger = logging.getLogger("reqlint.contact")
router = APIRouter(tags=["Contact"])

# Simple in-memory per-IP sliding window rate limiter (5 requests / 10 minutes)
_RATE_WINDOW_SECONDS = 600
_RATE_MAX_REQUESTS = 5
_ip_hits: Dict[str, Deque[float]] = defaultdict(deque)


def _check_rate_limit(client_ip: str) -> None:
    now = time.monotonic()
    hits = _ip_hits[client_ip]
    cutoff = now - _RATE_WINDOW_SECONDS
    while hits and hits[0] < cutoff:
        hits.popleft()
    if len(hits) >= _RATE_MAX_REQUESTS:
        raise AppException(
            message="Terlalu banyak permintaan kontak. Silakan coba lagi beberapa menit lagi.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMITED",
        )
    hits.append(now)


@router.post("/contact", status_code=status.HTTP_200_OK, summary="Send Contact Us message")
async def send_contact_message(payload: ContactRequest, request: Request):
    # Honeypot check against automated bots
    if payload.website and payload.website.strip():
        raise AppException(
            message="Permintaan ditolak oleh filter anti-spam.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="SPAM_DETECTED",
        )

    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    recipient = (settings.CONTACT_RECIPIENT_EMAIL or "").strip()
    if not recipient or not EmailService.is_configured():
        logger.error("Contact Us email not configured (SMTP_HOST or CONTACT_RECIPIENT_EMAIL missing)")
        raise AppException(
            message="Layanan pengiriman email kontak belum dikonfigurasi pada server.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EMAIL_NOT_CONFIGURED",
        )

    email_body = (
        f"Pesan baru dari formulir Contact Us ReqLint:\n\n"
        f"Nama   : {payload.name}\n"
        f"Email  : {payload.email}\n"
        f"Subjek : {payload.subject}\n\n"
        f"Pesan:\n{payload.message}\n"
    )

    try:
        await EmailService.send_email(
            to_email=recipient,
            subject=f"[ReqLint Contact] {payload.subject}",
            body=email_body,
            reply_to=str(payload.email),
        )
    except EmailDeliveryError as exc:
        raise AppException(
            message="Gagal mengirim pesan melalui penyedia email. Silakan coba lagi nanti.",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code=exc.code,
        ) from exc

    logger.info("Contact Us email delivered to configured recipient")
    return success_response(
        message="Pesan Anda telah berhasil dikirim.",
        data={"delivered": True},
        status_code=status.HTTP_200_OK,
    )
