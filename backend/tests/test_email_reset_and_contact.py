"""Tests for Password Reset (token lifecycle + SMTP) and Contact Us (validation, anti-spam, SMTP)."""
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.api.v1 import contact as contact_module
from app.core.database import AsyncSessionLocal
from app.db.models import PasswordResetToken, User


@pytest.mark.asyncio
async def test_forgot_and_reset_password_full_lifecycle(client: AsyncClient, caplog):
    email = "resetflow@example.com"
    old_pwd = "OldPass123"
    new_pwd = "NewPass456"
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Reset User", "email": email, "password": old_pwd, "password_confirmation": old_pwd},
    )

    sent_messages = []

    class FakeSMTP:
        def __init__(self, host, port, timeout=15):
            self.host = host
            self.port = port

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self):
            pass

        def login(self, user, pwd):
            pass

        def send_message(self, msg):
            sent_messages.append(msg)

    caplog.set_level(logging.INFO)
    with patch("app.services.email_service.settings.SMTP_HOST", "smtp.example.test"), \
         patch("app.services.email_service.settings.SMTP_PORT", 587), \
         patch("app.services.email_service.settings.SMTP_USE_TLS", True), \
         patch("app.services.email_service.settings.SMTP_USE_SSL", False), \
         patch("app.services.email_service.settings.PUBLIC_BASE_URL", "https://reqlint.test"), \
         patch("smtplib.SMTP", FakeSMTP):
        r = await client.post("/api/v1/auth/forgot-password", json={"email": email})
        assert r.status_code == 200

        # Unregistered email returns identical 200 (anti-enumeration)
        r_unknown = await client.post("/api/v1/auth/forgot-password", json={"email": "nobody@example.com"})
        assert r_unknown.status_code == 200
        assert r_unknown.json()["message"] == r.json()["message"]

    assert len(sent_messages) == 1
    body = sent_messages[0].get_content()
    assert "https://reqlint.test/reset-password?token=" in body
    raw_token = body.split("token=")[1].split()[0].strip()

    # Raw token must NEVER appear in logs
    assert raw_token not in caplog.text

    # Reset password with valid token
    r_reset = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw_token, "password": new_pwd, "password_confirmation": new_pwd},
    )
    assert r_reset.status_code == 200

    # Token cannot be reused
    r_reuse = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw_token, "password": "Another999", "password_confirmation": "Another999"},
    )
    assert r_reuse.status_code == 400
    assert r_reuse.json()["error_code"] == "INVALID_RESET_TOKEN"

    # Old password fails, new password succeeds
    assert (await client.post("/api/v1/auth/login", json={"email": email, "password": old_pwd})).status_code == 401
    assert (await client.post("/api/v1/auth/login", json={"email": email, "password": new_pwd})).status_code == 200


@pytest.mark.asyncio
async def test_reset_password_rejects_expired_token(client: AsyncClient):
    email = "expiredtok@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Expired", "email": email, "password": "Pass1234", "password_confirmation": "Pass1234"},
    )
    raw_token = "expired-raw-token-value-123456"
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.alamat_email == email))).scalar_one()
        db.add(
            PasswordResetToken(
                id_user=user.id_user,
                token_hash=token_hash,
                expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            )
        )
        await db.commit()

    r = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": raw_token, "password": "NewPass123", "password_confirmation": "NewPass123"},
    )
    assert r.status_code == 400
    assert r.json()["error_code"] == "INVALID_RESET_TOKEN"


@pytest.mark.asyncio
async def test_forgot_password_smtp_failure_still_returns_200_and_logs(client: AsyncClient, caplog):
    email = "smtpfail@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={"name": "SmtpFail", "email": email, "password": "Pass1234", "password_confirmation": "Pass1234"},
    )
    with patch("app.services.email_service.settings.SMTP_HOST", "smtp.example.test"), \
         patch("smtplib.SMTP", side_effect=OSError("connection refused")):
        r = await client.post("/api/v1/auth/forgot-password", json={"email": email})
        assert r.status_code == 200
    assert "EMAIL_DELIVERY_FAILED" in caplog.text


@pytest.mark.asyncio
async def test_contact_us_delivery_validation_antispam_and_failures(client: AsyncClient):
    contact_module._ip_hits.clear()

    valid_payload = {
        "name": "Farhan Akbar",
        "email": "sender@example.com",
        "subject": "Pertanyaan Integrasi",
        "message": "Halo tim ReqLint, ini adalah pesan uji coba lengkap.",
        "website": "",
    }

    # 1. Missing SMTP / recipient -> 503 EMAIL_NOT_CONFIGURED (never pretends success)
    with patch("app.api.v1.contact.settings.CONTACT_RECIPIENT_EMAIL", ""), \
         patch("app.services.email_service.settings.SMTP_HOST", ""):
        r_unconf = await client.post("/api/v1/contact", json=valid_payload)
        assert r_unconf.status_code == 503
        assert r_unconf.json()["error_code"] == "EMAIL_NOT_CONFIGURED"

    # 2. Invalid input -> 422
    r_bad = await client.post("/api/v1/contact", json={"name": "A", "email": "not-an-email", "subject": "Hi", "message": "short"})
    assert r_bad.status_code == 422

    # 3. Honeypot triggered -> 422 SPAM_DETECTED
    r_spam = await client.post("/api/v1/contact", json={**valid_payload, "website": "https://spam.example"})
    assert r_spam.status_code == 422
    assert r_spam.json()["error_code"] == "SPAM_DETECTED"

    # 4. SMTP provider failure -> 502 EMAIL_DELIVERY_FAILED
    with patch("app.api.v1.contact.settings.CONTACT_RECIPIENT_EMAIL", "owner@example.com"), \
         patch("app.services.email_service.settings.SMTP_HOST", "smtp.example.test"), \
         patch("app.services.email_service.settings.SMTP_PORT", 465), \
         patch("app.services.email_service.settings.SMTP_USE_SSL", True), \
         patch("smtplib.SMTP_SSL", side_effect=OSError("auth failed")):
        r_fail = await client.post("/api/v1/contact", json=valid_payload)
        assert r_fail.status_code == 502
        assert r_fail.json()["error_code"] == "EMAIL_DELIVERY_FAILED"

    # 5. Successful SSL delivery
    captured = []
    mock_smtp_ssl = MagicMock()
    mock_smtp_ssl.return_value.__enter__.return_value.send_message.side_effect = lambda m: captured.append(m)

    contact_module._ip_hits.clear()
    with patch("app.api.v1.contact.settings.CONTACT_RECIPIENT_EMAIL", "owner@example.com"), \
         patch("app.services.email_service.settings.SMTP_HOST", "smtp.example.test"), \
         patch("app.services.email_service.settings.SMTP_PORT", 465), \
         patch("app.services.email_service.settings.SMTP_USE_SSL", True), \
         patch("app.services.email_service.settings.SMTP_FROM", "noreply@example.com"), \
         patch("smtplib.SMTP_SSL", mock_smtp_ssl):
        r_ok = await client.post("/api/v1/contact", json=valid_payload)
        assert r_ok.status_code == 200
        assert r_ok.json()["data"]["delivered"] is True

    assert len(captured) == 1
    assert captured[0]["To"] == "owner@example.com"
    assert captured[0]["Reply-To"] == "sender@example.com"
    assert "[ReqLint Contact] Pertanyaan Integrasi" == captured[0]["Subject"]
