import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, or_, and_, desc, asc
from fastapi import status

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.errors import AppException
from app.db.models import User, DrafKebutuhan, AuditKebutuhan, TemuanCacat, DokumenUpload
from app.schemas.audit import CreateAuditRequest, ApplyAuditRequest, RevisionAuditRequest
from app.services.story_parser import StoryParser
from app.services.nlp_stage1 import NLPStage1Service
from app.services.nlp_stage2 import NLPStage2Service
from app.services.scoring import ScoringService

logger = logging.getLogger("reqlint.audit_service")

class AuditService:
    @classmethod
    async def run_pipeline(cls, id_audit: int, db: Optional[AsyncSession] = None):
        """
        Core audit execution pipeline (Stage 1 -> Stage 2 -> Scoring).
        Can be invoked from Celery or BackgroundTasks / inline runner or test harness.
        """
        if db is not None:
            await cls._execute_pipeline(id_audit, db)
        else:
            async with AsyncSessionLocal() as session:
                await cls._execute_pipeline(id_audit, session)

    @classmethod
    async def _execute_pipeline(cls, id_audit: int, db: AsyncSession):
        stmt = select(AuditKebutuhan).where(AuditKebutuhan.id_audit == id_audit)
        res = await db.execute(stmt)
        audit = res.scalar_one_or_none()
        if not audit:
            logger.error(f"Audit {id_audit} not found")
            return

        stmt_draf = select(DrafKebutuhan).where(DrafKebutuhan.id_draf == audit.id_draf)
        res_draf = await db.execute(stmt_draf)
        draf = res_draf.scalar_one_or_none()
        if not draf:
            logger.error(f"Draft for audit {id_audit} not found")
            return

        text_to_analyze = draf.konten_revisi if draf.konten_revisi else draf.konten_asli

        try:
            # STAGE 1 (spaCy & rule-based)
            stage1_result = NLPStage1Service.analyze_draft(text_to_analyze)
            findings = stage1_result["findings"]
            stories = stage1_result["stories"]

            # Calculate Stage 1 preliminary score
            score_calc = ScoringService.calculate_score(stories, findings)
            stage1_score = score_calc["skor_kualitas"]

            # Save Stage 1 findings
            for f in findings:
                temuan = TemuanCacat(
                    id_audit=audit.id_audit,
                    kategori_cacat=f["kategori_cacat"],
                    potongan_teks_asli=f["potongan_teks_asli"],
                    saran_perbaikan=f["saran_perbaikan"],
                    severity=f["severity"],
                    story_index=f["story_index"],
                    highlight_start=f["highlight_start"],
                    highlight_end=f["highlight_end"],
                    stage=1,
                    iso_characteristic=f.get("iso_characteristic")
                )
                db.add(temuan)

            audit.skor_kualitas = stage1_score
            if audit.skor_awal is None:
                audit.skor_awal = stage1_score
            audit.breakdown = score_calc["breakdown"]

            await db.commit()

        except Exception as e:
            logger.exception(f"Stage 1 failed for audit {id_audit}: {e}")
            audit.status_audit = "FAILED"
            audit.error_message = str(e)
            await db.commit()
            return

        # STAGE 2 (SLM)
        try:
            stage2_result = await NLPStage2Service.run_stage2(text_to_analyze, findings)
            audit.ai_rewrite = stage2_result.get("ai_rewrite")
            audit.acceptance_criteria = stage2_result.get("acceptance_criteria")

            # Recompute final score with INVEST results
            # P0/UI-48: absent INVEST data stays None (unknown) — scoring must
            # never treat missing data as "all criteria pass".
            invest_flags = stage2_result.get("invest")
            final_score_calc = ScoringService.calculate_score(stories, findings, invest_results=invest_flags)
            audit.skor_kualitas = final_score_calc["skor_kualitas"]
            audit.breakdown = final_score_calc["breakdown"]

            audit.status_audit = "COMPLETED"
            audit.stage2_status = "DONE"
            audit.error_message = None
            await db.commit()

        except Exception as e:
            # SAFE-2: Fallback to PARTIAL so Stage 1 remains available
            logger.warning(f"Stage 2 failed for audit {id_audit}: {e}")
            audit.status_audit = "PARTIAL"
            audit.stage2_status = "FAILED"
            audit.error_message = str(e)
            await db.commit()

    @staticmethod
    async def create_audit(db: AsyncSession, user_id: int, payload: CreateAuditRequest) -> Dict[str, Any]:
        raw_text = payload.konten.strip()
        if not raw_text:
            raise AppException(
                message="Draf kebutuhan tidak boleh kosong",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_code="EMPTY_DRAFT",
                errors=[{"field": "konten", "message": "Draf kebutuhan tidak boleh kosong"}]
            )

        if len(raw_text) > settings.MAX_TEXT_CHARS:
            raise AppException(
                message="Draf kebutuhan melebihi batas karakter",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_code="DRAFT_TOO_LONG"
            )

        # Check document ownership if provided
        if payload.tipe_masukan == "pdf":
            if not payload.id_dokumen:
                raise AppException(
                    message="ID dokumen wajib disertakan untuk input PDF",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    error_code="MISSING_DOCUMENT_ID"
                )
            stmt_doc = select(DokumenUpload).where(
                DokumenUpload.id_dokumen == payload.id_dokumen,
                DokumenUpload.id_user == user_id
            )
            res_doc = await db.execute(stmt_doc)
            if not res_doc.scalar_one_or_none():
                raise AppException(
                    message="Data dokumen tidak ditemukan",
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_code="DOCUMENT_NOT_FOUND"
                )

        # Default title is first 60 characters
        judul = payload.judul_klausul.strip() if payload.judul_klausul and payload.judul_klausul.strip() else raw_text[:60]

        now = datetime.now(timezone.utc)
        draf = DrafKebutuhan(
            id_dokumen=payload.id_dokumen,
            id_user=user_id,
            judul_klausul=judul,
            tipe_masukan=payload.tipe_masukan,
            konten_asli=raw_text,
            konten_revisi=None,
            status_revisi="BELUM_DIREVISI",
            created_at=now
        )
        db.add(draf)
        await db.flush()

        audit = AuditKebutuhan(
            id_draf=draf.id_draf,
            skor_kualitas=0.0,
            tanggal_audit=now,
            status_audit="PROCESSING",
            stage2_status="PENDING",
            skor_awal=None,
            ai_rewrite=None,
            acceptance_criteria=None,
            breakdown=None,
            error_message=None
        )
        db.add(audit)
        await db.commit()
        await db.refresh(draf)
        await db.refresh(audit)

        return {
            "id_draf": draf.id_draf,
            "id_audit": audit.id_audit,
            "status_audit": "PROCESSING",
            "stage2_status": "PENDING",
            "poll_url": f"/api/v1/audits/{audit.id_audit}/status"
        }

    @staticmethod
    async def get_audit_status(db: AsyncSession, user_id: int, id_audit: int) -> Dict[str, Any]:
        stmt = (
            select(AuditKebutuhan, DrafKebutuhan)
            .join(DrafKebutuhan, AuditKebutuhan.id_draf == DrafKebutuhan.id_draf)
            .where(AuditKebutuhan.id_audit == id_audit, DrafKebutuhan.id_user == user_id)
        )
        res = await db.execute(stmt)
        row = res.first()
        if not row:
            raise AppException(
                message="Data audit tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="AUDIT_NOT_FOUND"
            )

        audit, _ = row
        stage1_ready = audit.skor_awal is not None or audit.status_audit != "PROCESSING"

        return {
            "id_audit": audit.id_audit,
            "status_audit": audit.status_audit,
            "stage2_status": audit.stage2_status,
            "stage1_ready": stage1_ready
        }

    @staticmethod
    async def get_audit_detail(db: AsyncSession, user_id: int, id_audit: int) -> Dict[str, Any]:
        stmt = (
            select(AuditKebutuhan, DrafKebutuhan)
            .join(DrafKebutuhan, AuditKebutuhan.id_draf == DrafKebutuhan.id_draf)
            .where(AuditKebutuhan.id_audit == id_audit, DrafKebutuhan.id_user == user_id)
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

        # Fetch findings
        stmt_f = select(TemuanCacat).where(TemuanCacat.id_audit == audit.id_audit).order_by(TemuanCacat.highlight_start)
        res_f = await db.execute(stmt_f)
        findings_records = res_f.scalars().all()

        temuan_list = [
            {
                "id_temuan": f.id_temuan,
                "story_index": f.story_index,
                "kategori_cacat": f.kategori_cacat,
                "severity": f.severity,
                "stage": f.stage,
                "iso_characteristic": f.iso_characteristic,
                "potongan_teks_asli": f.potongan_teks_asli,
                "highlight_start": f.highlight_start,
                "highlight_end": f.highlight_end,
                "saran_perbaikan": f.saran_perbaikan
            }
            for f in findings_records
        ]

        ringkasan = {
            "ambiguity": sum(1 for f in temuan_list if f["kategori_cacat"] == "AMBIGUITY"),
            "tidak_lengkap": sum(1 for f in temuan_list if f["kategori_cacat"] == "TIDAK_LENGKAP"),
            "weak_directive": sum(1 for f in temuan_list if f["kategori_cacat"] == "WEAK_DIRECTIVE"),
            "passive_voice": sum(1 for f in temuan_list if f["kategori_cacat"] == "PASSIVE_VOICE"),
            "total": len(temuan_list)
        }

        # Recommendations
        rekomendasi_ai = None
        if audit.stage2_status == "DONE" and audit.ai_rewrite:
            rekomendasi_ai = {
                "ai_rewrite": audit.ai_rewrite,
                "acceptance_criteria": audit.acceptance_criteria or []
            }

        # P0.1/R3-2: eksplisit bedakan saran AI nyata vs contoh mock.
        # Catatan: provider dibaca dari konfigurasi AKTIF (aproksimasi untuk
        # audit historis — provider saat audit dijalankan tidak direkam di DB;
        # pada deployment tunggal nilainya konsisten).
        ai_suggestion_source = None
        if rekomendasi_ai is not None:
            ai_suggestion_source = "mock" if settings.SLM_PROVIDER == "mock" else "provider"

        # Notifications
        notifikasi = None
        if audit.status_audit == "PARTIAL":
            notifikasi = {
                "tipe": "warning",
                "message": "Gagal memuat rekomendasi AI, silakan klik tombol Analisis Ulang",
                "aksi": "reanalyze"
            }
        elif audit.status_audit == "FAILED":
            notifikasi = {
                "tipe": "error",
                "message": "Gagal memuat hasil analisis, silakan klik tombol Analisis Ulang",
                "aksi": "reanalyze"
            }

        # Scorecard
        scorecard = None
        if audit.status_audit != "PROCESSING" or audit.skor_awal is not None:
            scorecard = {
                "skor_awal": audit.skor_awal,
                "skor_kualitas": audit.skor_kualitas,
                "breakdown": audit.breakdown or ScoringService.default_breakdown(stage2_done=audit.stage2_status == "DONE")
            }

        # Diff
        revised_text = draf.konten_revisi if draf.konten_revisi else audit.ai_rewrite
        diff = {
            "original": {
                "teks": draf.konten_asli,
                "skor": audit.skor_awal
            },
            "revised": {
                "teks": revised_text,
                "skor": audit.skor_kualitas if draf.status_revisi == "SUDAH_DIREVISI" else None
            }
        }

        return {
            "id_audit": audit.id_audit,
            "id_draf": draf.id_draf,
            "judul_klausul": draf.judul_klausul,
            "tipe_masukan": draf.tipe_masukan,
            "status_audit": audit.status_audit,
            "stage2_status": audit.stage2_status,
            "status_revisi": draf.status_revisi,
            "tanggal_audit": audit.tanggal_audit.isoformat() if audit.tanggal_audit else None,
            "scorecard": scorecard,
            "ringkasan": ringkasan,
            "temuan": temuan_list,
            "rekomendasi_ai": rekomendasi_ai,
            "ai_suggestion_source": ai_suggestion_source,
            "diff": diff,
            "notifikasi": notifikasi
        }

    @staticmethod
    async def reanalyze_audit(db: AsyncSession, user_id: int, id_audit: int) -> Dict[str, Any]:
        stmt = (
            select(AuditKebutuhan, DrafKebutuhan)
            .join(DrafKebutuhan, AuditKebutuhan.id_draf == DrafKebutuhan.id_draf)
            .where(AuditKebutuhan.id_audit == id_audit, DrafKebutuhan.id_user == user_id)
        )
        res = await db.execute(stmt)
        row = res.first()
        if not row:
            raise AppException(
                message="Data audit tidak ditemukan",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="AUDIT_NOT_FOUND"
            )

        audit, _ = row
        if audit.status_audit == "PROCESSING":
            raise AppException(
                message="Analisis masih berjalan",
                status_code=status.HTTP_409_CONFLICT,
                error_code="AUDIT_IN_PROGRESS"
            )

        # Clear old findings
        await db.execute(delete(TemuanCacat).where(TemuanCacat.id_audit == audit.id_audit))

        # Reset status
        audit.status_audit = "PROCESSING"
        audit.stage2_status = "PENDING"
        audit.ai_rewrite = None
        audit.acceptance_criteria = None
        audit.error_message = None

        await db.commit()

        return {
            "id_audit": audit.id_audit,
            "status_audit": "PROCESSING",
            "stage2_status": "PENDING",
            "poll_url": f"/api/v1/audits/{audit.id_audit}/status"
        }

    @staticmethod
    async def apply_recommendation(db: AsyncSession, user_id: int, id_audit: int, terapkan: List[str]) -> Dict[str, Any]:
        stmt = (
            select(AuditKebutuhan, DrafKebutuhan)
            .join(DrafKebutuhan, AuditKebutuhan.id_draf == DrafKebutuhan.id_draf)
            .where(AuditKebutuhan.id_audit == id_audit, DrafKebutuhan.id_user == user_id)
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
        if audit.stage2_status != "DONE" or not audit.ai_rewrite:
            raise AppException(
                message="Rekomendasi AI belum tersedia",
                status_code=status.HTTP_409_CONFLICT,
                error_code="AI_NOT_READY"
            )

        # Build revised content
        base_text = audit.ai_rewrite if "rewrite" in terapkan else (draf.konten_revisi if draf.konten_revisi else draf.konten_asli)

        if "acceptance_criteria" in terapkan and audit.acceptance_criteria:
            ac_blocks = ["Acceptance Criteria:"]
            for ac in audit.acceptance_criteria:
                ac_blocks.append(f"- Given {ac.get('given')}, When {ac.get('when')}, Then {ac.get('then')}")
            konten_baru = f"{base_text.strip()}\n\n" + "\n".join(ac_blocks)
        else:
            konten_baru = base_text.strip()

        # Synchronous rescore via Stage 1 (<50ms)
        stage1_res = NLPStage1Service.analyze_draft(konten_baru)
        new_findings = stage1_res["findings"]
        new_score_calc = ScoringService.calculate_score(stage1_res["stories"], new_findings)
        new_score = new_score_calc["skor_kualitas"]

        # Atomic update (ACID, SAFE-4)
        draf.konten_revisi = konten_baru
        draf.status_revisi = "SUDAH_DIREVISI"
        audit.skor_kualitas = new_score
        audit.breakdown = new_score_calc["breakdown"]

        await db.commit()

        return {
            "id_audit": audit.id_audit,
            "status_revisi": "SUDAH_DIREVISI",
            "konten_revisi": konten_baru,
            "skor_awal": audit.skor_awal,
            "skor_kualitas": new_score,
            "label": "Skor Kualitas Terkini",
            "ringkasan": stage1_res["ringkasan"],
            "temuan": new_findings,
            "diff": {
                "original": {"teks": draf.konten_asli, "skor": audit.skor_awal},
                "revised": {"teks": konten_baru, "skor": new_score}
            }
        }

    @staticmethod
    async def manual_revision(db: AsyncSession, user_id: int, id_audit: int, payload: RevisionAuditRequest) -> Dict[str, Any]:
        raw_text = payload.konten_revisi.strip()
        if not raw_text:
            raise AppException(
                message="Draf kebutuhan tidak boleh kosong",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_code="EMPTY_DRAFT",
                errors=[{"field": "konten_revisi", "message": "Draf kebutuhan tidak boleh kosong"}]
            )

        stmt = (
            select(AuditKebutuhan, DrafKebutuhan)
            .join(DrafKebutuhan, AuditKebutuhan.id_draf == DrafKebutuhan.id_draf)
            .where(AuditKebutuhan.id_audit == id_audit, DrafKebutuhan.id_user == user_id)
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

        # Rescore synchronously Stage 1
        stage1_res = NLPStage1Service.analyze_draft(raw_text)
        new_findings = stage1_res["findings"]
        new_score_calc = ScoringService.calculate_score(stage1_res["stories"], new_findings)
        new_score = new_score_calc["skor_kualitas"]

        draf.konten_revisi = raw_text
        draf.status_revisi = "SUDAH_DIREVISI"
        audit.skor_kualitas = new_score
        audit.breakdown = new_score_calc["breakdown"]

        await db.commit()

        return {
            "id_audit": audit.id_audit,
            "status_revisi": "SUDAH_DIREVISI",
            "konten_revisi": raw_text,
            "skor_awal": audit.skor_awal,
            "skor_kualitas": new_score,
            "label": "Skor Kualitas Terkini",
            "ringkasan": stage1_res["ringkasan"],
            "temuan": new_findings,
            "diff": {
                "original": {"teks": draf.konten_asli, "skor": audit.skor_awal},
                "revised": {"teks": raw_text, "skor": new_score}
            }
        }

    @staticmethod
    async def list_audits(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        limit: int = 10,
        q: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        status_revisi: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: str = "tanggal",
        order: str = "desc"
    ) -> Dict[str, Any]:
        # Check if user has ANY audit without filter
        stmt_any = (
            select(func.count(AuditKebutuhan.id_audit))
            .join(DrafKebutuhan, AuditKebutuhan.id_draf == DrafKebutuhan.id_draf)
            .where(DrafKebutuhan.id_user == user_id)
        )
        total_user_audits = (await db.execute(stmt_any)).scalar() or 0
        has_any_history = total_user_audits > 0

        if not has_any_history:
            return {
                "message": "Belum ada riwayat audit yang tersedia",
                "items": [],
                "pagination": {"page": page, "limit": limit, "total_items": 0, "total_pages": 0},
                "has_any_history": False
            }

        # Build filtered query
        query = (
            select(AuditKebutuhan, DrafKebutuhan)
            .join(DrafKebutuhan, AuditKebutuhan.id_draf == DrafKebutuhan.id_draf)
            .where(DrafKebutuhan.id_user == user_id)
        )

        filters = []
        if q and q.strip():
            search_term = f"%{q.strip()}%"
            filters.append(
                or_(
                    DrafKebutuhan.judul_klausul.ilike(search_term),
                    DrafKebutuhan.konten_asli.ilike(search_term)
                )
            )

        if min_score is not None:
            filters.append(AuditKebutuhan.skor_kualitas >= min_score)
        if max_score is not None:
            filters.append(AuditKebutuhan.skor_kualitas <= max_score)
        if status_revisi:
            filters.append(DrafKebutuhan.status_revisi == status_revisi)
        if date_from:
            try:
                dt_from = datetime.fromisoformat(date_from)
                filters.append(AuditKebutuhan.tanggal_audit >= dt_from)
            except Exception:
                pass
        if date_to:
            try:
                dt_to = datetime.fromisoformat(date_to)
                filters.append(AuditKebutuhan.tanggal_audit <= dt_to)
            except Exception:
                pass

        if filters:
            query = query.where(and_(*filters))

        # Count filtered items
        count_query = select(func.count()).select_from(query.subquery())
        total_items = (await db.execute(count_query)).scalar() or 0

        # Sort
        sort_col = AuditKebutuhan.skor_kualitas if sort_by == "skor" else AuditKebutuhan.tanggal_audit
        query = query.order_by(desc(sort_col) if order.lower() == "desc" else asc(sort_col))

        # Paginate
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        rows = result.all()

        items = [
            {
                "id_audit": audit.id_audit,
                "id_draf": draf.id_draf,
                "tanggal_audit": audit.tanggal_audit.isoformat() if audit.tanggal_audit else None,
                "judul_klausul": draf.judul_klausul,
                "skor_kualitas": audit.skor_kualitas,
                "status_revisi": draf.status_revisi,
                "status_audit": audit.status_audit
            }
            for audit, draf in rows
        ]

        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
        message = "OK" if total_items > 0 else "Tidak ada riwayat yang cocok dengan pencarian"

        return {
            "message": message,
            "items": items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total_items,
                "total_pages": total_pages
            },
            "has_any_history": True
        }
