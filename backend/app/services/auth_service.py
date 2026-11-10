import re
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import status

from app.db.models import User, PasswordResetToken
from app.schemas.auth import RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.core.security import hash_password, verify_password, dummy_verify_password, create_access_token
from app.core.errors import AppException
from app.core.config import settings

class AuthService:
    @staticmethod
    async def register(db: AsyncSession, payload: RegisterRequest) -> dict:
        # Check password criteria: min 8 char, at least 1 letter and 1 digit
        has_letter = bool(re.search(r'[A-Za-z]', payload.password))
        has_digit = bool(re.search(r'\d', payload.password))
        password_format_valid = len(payload.password) >= 8 and has_letter and has_digit
        password_match = payload.password == payload.password_confirmation

        if not password_match or not password_format_valid:
            error_field = "password_confirmation" if not password_match else "password"
            error_msg = "Konfirmasi sandi tidak cocok" if not password_match else "Sandi harus memuat minimal 8 karakter dengan huruf dan angka"
            raise AppException(
                message="Format sandi tidak valid atau konfirmasi sandi tidak cocok",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_code="INVALID_PASSWORD",
                errors=[{"field": error_field, "message": error_msg}]
            )

        # Check existing user
        stmt = select(User).where(User.alamat_email == payload.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise AppException(
                message="Email sudah terdaftar",
                status_code=status.HTTP_409_CONFLICT,
                error_code="EMAIL_TAKEN"
            )

        hashed = hash_password(payload.password)
        now = datetime.now(timezone.utc)
        new_user = User(
            nama_lengkap=payload.name,
            alamat_email=payload.email,
            password=hashed,
            tanggal_registrasi=now
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return {
            "id_user": new_user.id_user,
            "name": new_user.nama_lengkap,
            "email": new_user.alamat_email,
            "tanggal_registrasi": new_user.tanggal_registrasi.isoformat() if new_user.tanggal_registrasi else now.isoformat()
        }

    @staticmethod
    async def login(db: AsyncSession, payload: LoginRequest) -> dict:
        stmt = select(User).where(User.alamat_email == payload.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            # Timing defense
            dummy_verify_password(payload.password)
            raise AppException(
                message="Kredensial tidak valid",
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code="INVALID_CREDENTIALS"
            )

        if not verify_password(payload.password, user.password):
            raise AppException(
                message="Kredensial tidak valid",
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code="INVALID_CREDENTIALS"
            )

        expires_in = settings.JWT_EXPIRE_HOURS * 3600
        token = create_access_token({
            "sub": str(user.id_user),
            "email": user.alamat_email
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "user": {
                "id_user": user.id_user,
                "name": user.nama_lengkap,
                "email": user.alamat_email
            }
        }

    @staticmethod
    async def forgot_password(db: AsyncSession, payload: ForgotPasswordRequest) -> None:
        """
        Membuat token reset password.
        Selalu berhasil tanpa error untuk mencegah user enumeration.
        Pada implementasi produksi, token dikirim via email.
        """
        stmt = select(User).where(User.alamat_email == payload.email.strip().lower())
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            # Jangan berikan info bahwa email tidak ditemukan (anti-enumeration)
            return

        # Buat token reset
        raw_token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        reset_token = PasswordResetToken(
            id_user=user.id_user,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        db.add(reset_token)
        await db.commit()

        # NOTE: Pada implementasi produksi, kirim email berisi:
        # f"{FRONTEND_URL}/reset-password?token={raw_token}"
        # Untuk keperluan demo/development, token disimpan di database
        # dan bisa diakses langsung

    @staticmethod
    async def reset_password(db: AsyncSession, payload: ResetPasswordRequest) -> None:
        """
        Reset password menggunakan token yang valid.
        """
        # Validasi password baru
        has_letter = bool(re.search(r'[A-Za-z]', payload.password))
        has_digit = bool(re.search(r'\d', payload.password))
        if len(payload.password) < 8 or not has_letter or not has_digit:
            raise AppException(
                message="Sandi harus memuat minimal 8 karakter dengan huruf dan angka",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_code="INVALID_PASSWORD",
                errors=[{"field": "password", "message": "Sandi harus memuat minimal 8 karakter dengan huruf dan angka"}]
            )

        if payload.password != payload.password_confirmation:
            raise AppException(
                message="Konfirmasi sandi tidak cocok",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_code="INVALID_PASSWORD",
                errors=[{"field": "password_confirmation", "message": "Konfirmasi sandi tidak cocok"}]
            )

        # Cari token
        token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > datetime.now(timezone.utc)
        )
        result = await db.execute(stmt)
        reset_record = result.scalar_one_or_none()

        if not reset_record:
            raise AppException(
                message="Token reset tidak valid atau sudah kedaluwarsa",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="INVALID_RESET_TOKEN"
            )

        # Update password
        user_stmt = select(User).where(User.id_user == reset_record.id_user)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            raise AppException(
                message="Pengguna tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="USER_NOT_FOUND"
            )

        user.password = hash_password(payload.password)
        reset_record.used_at = datetime.now(timezone.utc)

        await db.commit()
