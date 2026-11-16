import asyncio
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, BackgroundTasks, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.responses import success_response, error_response
from app.core.errors import AppException
from app.api.deps import get_current_user
from app.db.models import User, DrafKebutuhan, AuditKebutuhan, HistoryDownload
from app.schemas.audit import CreateAuditRequest, ApplyAuditRequest, RevisionAuditRequest
from app.services.audit_service import AuditService
from app.services.export_service import ExportService

router = APIRouter(prefix="/audits", tags=["Audits"])

@router.post("", status_code=status.HTTP_202_ACCEPTED, summary="Create new audit")
async def create_audit(
    payload: CreateAuditRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    data = await AuditService.create_audit(db, current_user.id_user, payload)
    id_audit = data["id_audit"]

    if settings.AUDIT_EXECUTION_MODE == "celery":
        try:
            from app.workers.tasks import run_audit_task
            task = run_audit_task.delay(id_audit)
            # update task id
            stmt = select(AuditKebutuhan).where(AuditKebutuhan.id_audit == id_audit)
            res = await db.execute(stmt)
            audit = res.scalar_one_or_none()
            if audit:
                audit.celery_task_id = task.id
                await db.commit()
        except Exception:
            # Fallback to inline background task if celery unavailable
            background_tasks.add_task(AuditService.run_pipeline, id_audit)
    else:
        background_tasks.add_task(AuditService.run_pipeline, id_audit)

    return success_response(
        message="Draf diterima dan sedang dianalisis",
        data=data,
        status_code=status.HTTP_202_ACCEPTED
    )

@router.get("", status_code=status.HTTP_200_OK, summary="List and filter audit history")
async def list_audits(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    q: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    max_score: Optional[float] = Query(None),
    status_revisi: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    sort_by: str = Query("tanggal", pattern="^(tanggal|skor)$"),
    order: str = Query("desc", pattern="^(desc|asc)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await AuditService.list_audits(
        db=db,
        user_id=current_user.id_user,
        page=page,
        limit=limit,
        q=q,
        min_score=min_score,
        max_score=max_score,
        status_revisi=status_revisi,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        order=order
    )
    return success_response(
        message=res["message"],
        data={
            "items": res["items"],
            "pagination": res["pagination"],
            "has_any_history": res["has_any_history"]
        },
        status_code=status.HTTP_200_OK
    )

@router.get("/{id_audit}/status", status_code=status.HTTP_200_OK, summary="Lightweight audit status polling")
async def get_audit_status(
    id_audit: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    data = await AuditService.get_audit_status(db, current_user.id_user, id_audit)
    return success_response(message="OK", data=data, status_code=status.HTTP_200_OK)

@router.get("/{id_audit}", status_code=status.HTTP_200_OK, summary="Get full audit result")
async def get_audit_detail(
    id_audit: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    data = await AuditService.get_audit_detail(db, current_user.id_user, id_audit)
    return success_response(message="OK", data=data, status_code=status.HTTP_200_OK)

@router.post("/{id_audit}/reanalyze", status_code=status.HTTP_202_ACCEPTED, summary="Reanalyze requirement")
async def reanalyze_audit(
    id_audit: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    data = await AuditService.reanalyze_audit(db, current_user.id_user, id_audit)

    if settings.AUDIT_EXECUTION_MODE == "celery":
        try:
            from app.workers.tasks import run_audit_task
            run_audit_task.delay(id_audit)
        except Exception:
            background_tasks.add_task(AuditService.run_pipeline, id_audit)
    else:
        background_tasks.add_task(AuditService.run_pipeline, id_audit)

    return success_response(
        message="Analisis ulang dimulai",
        data=data,
        status_code=status.HTTP_202_ACCEPTED
    )

@router.post("/{id_audit}/apply", status_code=status.HTTP_200_OK, summary="1-Click Apply AI recommendation")
async def apply_recommendation(
    id_audit: int,
    payload: ApplyAuditRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    data = await AuditService.apply_recommendation(db, current_user.id_user, id_audit, payload.terapkan)
    return success_response(
        message="Draf berhasil diperbarui",
        data=data,
        status_code=status.HTTP_200_OK
    )

@router.put("/{id_audit}/revision", status_code=status.HTTP_200_OK, summary="Manual revision and synchronous rescore")
async def manual_revision(
    id_audit: int,
    payload: RevisionAuditRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    data = await AuditService.manual_revision(db, current_user.id_user, id_audit, payload)
    return success_response(
        message="Draf berhasil diperbarui",
        data=data,
        status_code=status.HTTP_200_OK
    )

@router.get("/{id_audit}/export", summary="Export audit report in PDF, Markdown, or JSON")
async def export_audit(
    id_audit: int,
    format: str = Query(..., description="pdf | md | json"),
    # Task 09: report labels follow the selected UI locale ("id" default keeps
    # the previous behavior for existing clients).
    lang: str = Query("id", description="Report label language: id | en"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    clean_format = format.lower().strip()
    if clean_format not in {"pdf", "md", "json"}:
        raise AppException(
            message="Format tidak didukung",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="UNSUPPORTED_FORMAT"
        )
    clean_lang = lang.lower().strip()
    if clean_lang not in {"id", "en"}:
        raise AppException(
            message="Bahasa laporan tidak didukung",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="UNSUPPORTED_LANG"
        )

    # Ownership and state check
    stmt = (
        select(AuditKebutuhan, DrafKebutuhan)
        .join(DrafKebutuhan, AuditKebutuhan.id_draf == DrafKebutuhan.id_draf)
        .where(AuditKebutuhan.id_audit == id_audit, DrafKebutuhan.id_user == current_user.id_user)
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise AppException(
            message="Data audit tidak ditemukan",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="AUDIT_NOT_FOUND"
        )

    audit, draf = row
    if audit.status_audit not in {"COMPLETED", "PARTIAL"}:
        raise AppException(
            message="Hasil audit belum siap diekspor",
            status_code=status.HTTP_409_CONFLICT,
            error_code="AUDIT_NOT_READY"
        )

    # Get full detail for report
    audit_detail = await AuditService.get_audit_detail(db, current_user.id_user, id_audit)
    konten_asli = draf.konten_asli
    konten_revisi = draf.konten_revisi or ""

    try:
        loop = asyncio.get_running_loop()
        if clean_format == "pdf":
            file_bytes = await loop.run_in_executor(None, ExportService.render_pdf, audit_detail, konten_asli, konten_revisi, clean_lang)
            media_type = "application/pdf"
            ext = "pdf"
        elif clean_format == "md":
            file_bytes = await loop.run_in_executor(None, ExportService.render_markdown, audit_detail, konten_asli, konten_revisi, clean_lang)
            media_type = "text/markdown; charset=utf-8"
            ext = "md"
        else:
            file_bytes = await loop.run_in_executor(None, ExportService.render_json, audit_detail, konten_asli, konten_revisi)
            media_type = "application/json"
            ext = "json"

        # Record download history ONLY if render succeeds
        history = HistoryDownload(
            id_audit=audit.id_audit,
            format_dokumen=clean_format,
            waktu_download=datetime.now(timezone.utc)
        )
        db.add(history)
        await db.commit()

        filename = f"reqlint-audit-{id_audit}.{ext}"
        return Response(
            content=file_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except Exception:
        raise AppException(
            message="Gagal membuat berkas unduhan, silakan coba beberapa saat lagi",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="EXPORT_FAILED"
        )
