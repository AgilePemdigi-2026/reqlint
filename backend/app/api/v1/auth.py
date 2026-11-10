from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.responses import success_response
from app.schemas.auth import RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register user")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    data = await AuthService.register(db, payload)
    return success_response(
        message="Pendaftaran berhasil, silakan masuk",
        data=data,
        status_code=status.HTTP_201_CREATED
    )

@router.post("/login", status_code=status.HTTP_200_OK, summary="Login user")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    data = await AuthService.login(db, payload)
    return success_response(
        message="Login berhasil",
        data=data,
        status_code=status.HTTP_200_OK
    )

@router.get("/me", status_code=status.HTTP_200_OK, summary="Get current authenticated user profile")
async def me(current_user: User = Depends(get_current_user)):
    return success_response(
        message="OK",
        data={
            "id_user": current_user.id_user,
            "name": current_user.nama_lengkap,
            "email": current_user.alamat_email,
            "tanggal_registrasi": current_user.tanggal_registrasi.isoformat() if current_user.tanggal_registrasi else None
        }
    )

@router.post("/forgot-password", status_code=status.HTTP_200_OK, summary="Request password reset token")
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    await AuthService.forgot_password(db, payload)
    # Selalu kembalikan sukses untuk mencegah user enumeration
    return success_response(
        message="Jika email terdaftar, tautan reset telah dikirim.",
        data=None,
        status_code=status.HTTP_200_OK
    )

@router.post("/reset-password", status_code=status.HTTP_200_OK, summary="Reset password with token")
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await AuthService.reset_password(db, payload)
    return success_response(
        message="Kata sandi berhasil diperbarui. Silakan masuk.",
        data=None,
        status_code=status.HTTP_200_OK
    )
