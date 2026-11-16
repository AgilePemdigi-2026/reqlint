from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "user"

    id_user = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama_lengkap = Column(String(150), nullable=False)
    alamat_email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    tanggal_registrasi = Column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc), nullable=False)

    dokumen = relationship("DokumenUpload", back_populates="user", cascade="all, delete-orphan")
    draf = relationship("DrafKebutuhan", back_populates="user", cascade="all, delete-orphan")

class DokumenUpload(Base):
    __tablename__ = "dokumen_upload"

    id_dokumen = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama_dokumen = Column(String(255), nullable=False)
    ukuran_dokumen = Column(Integer, nullable=False)
    waktu_upload = Column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc), nullable=False)
    id_user = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="dokumen")
    draf = relationship("DrafKebutuhan", back_populates="dokumen")

class DrafKebutuhan(Base):
    __tablename__ = "draf_kebutuhan"

    id_draf = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_dokumen = Column(Integer, ForeignKey("dokumen_upload.id_dokumen", ondelete="SET NULL"), nullable=True)
    id_user = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE"), nullable=False, index=True)
    judul_klausul = Column(String(255), nullable=False)
    tipe_masukan = Column(String(20), nullable=False, default="manual")  # manual | pdf
    konten_asli = Column(Text, nullable=False)
    konten_revisi = Column(Text, nullable=True)
    status_revisi = Column(String(30), nullable=False, default="BELUM_DIREVISI")  # BELUM_DIREVISI | SUDAH_DIREVISI
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="draf")
    dokumen = relationship("DokumenUpload", back_populates="draf")
    audits = relationship("AuditKebutuhan", back_populates="draf", cascade="all, delete-orphan")

class AuditKebutuhan(Base):
    __tablename__ = "audit_kebutuhan"

    id_audit = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_draf = Column(Integer, ForeignKey("draf_kebutuhan.id_draf", ondelete="CASCADE"), nullable=False, index=True)
    skor_kualitas = Column(Float, nullable=False, default=0.0)
    tanggal_audit = Column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc), nullable=False)
    status_audit = Column(String(30), nullable=False, default="PROCESSING")  # PROCESSING | COMPLETED | PARTIAL | FAILED
    skor_awal = Column(Float, nullable=True)
    stage2_status = Column(String(30), nullable=False, default="PENDING")  # PENDING | DONE | FAILED
    ai_rewrite = Column(Text, nullable=True)
    acceptance_criteria = Column(JSON, nullable=True)
    breakdown = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    celery_task_id = Column(String(100), nullable=True)
    # Task 06: evaluator selection persisted on the audit row so reanalyze
    # reuses the same evaluator and the report can display provenance.
    evaluator = Column(String(20), nullable=False, default="rule_based", server_default="rule_based")
    model_version = Column(String(80), nullable=True)

    draf = relationship("DrafKebutuhan", back_populates="audits")
    temuan = relationship("TemuanCacat", back_populates="audit", cascade="all, delete-orphan")
    history_download = relationship("HistoryDownload", back_populates="audit", cascade="all, delete-orphan")

class TemuanCacat(Base):
    __tablename__ = "temuan_cacat"

    id_temuan = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_audit = Column(Integer, ForeignKey("audit_kebutuhan.id_audit", ondelete="CASCADE"), nullable=False, index=True)
    kategori_cacat = Column(String(50), nullable=False)  # AMBIGUITY | TIDAK_LENGKAP | WEAK_DIRECTIVE | PASSIVE_VOICE
    potongan_teks_asli = Column(Text, nullable=False)
    saran_perbaikan = Column(Text, nullable=False)
    kriteria_penerimaan = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False, default="MEDIUM")  # LOW | MEDIUM | HIGH
    story_index = Column(Integer, nullable=False, default=0)
    highlight_start = Column(Integer, nullable=False, default=0)
    highlight_end = Column(Integer, nullable=False, default=0)
    stage = Column(Integer, nullable=False, default=1)  # 1 | 2
    iso_characteristic = Column(String(50), nullable=True)

    audit = relationship("AuditKebutuhan", back_populates="temuan")

class HistoryDownload(Base):
    __tablename__ = "history_download"

    id_ekspor = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_audit = Column(Integer, ForeignKey("audit_kebutuhan.id_audit", ondelete="CASCADE"), nullable=False, index=True)
    format_dokumen = Column(String(20), nullable=False)  # pdf | md | json
    waktu_download = Column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc), nullable=False)

    audit = relationship("AuditKebutuhan", back_populates="history_download")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey("user.id_user", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
