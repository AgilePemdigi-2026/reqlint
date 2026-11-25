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
from app.services.nlp_stage2 import NLPStage2Service, LLMProviderUnavailableError
from app.services.scoring import ScoringService
from app.services.invest_ml_service import InvestMLService, MLEvaluatorUnavailableError
from app.services.multimodel_router_service import MultiModelRouterService
from app.services.evaluation_contract import (
    build_evaluation_result,
    build_dimensions,
    overall_verdict,
    framework_score,
    EVALUATORS,
)

logger = logging.getLogger("reqlint.audit_service")

class AuditService:
    @classmethod
    async def run_pipeline(cls, id_audit: int, db: Optional[AsyncSession] = None):
        """
        Task 06 pipeline: Evaluator dispatch -> Immutable Evaluation Result ->
        Shared Response Generation (verdict-preserving).

        The evaluator persisted on the audit row decides which evaluator runs
        (rule_based | traditional_ml | llm). Evaluator failures fail the audit
        explicitly — a Traditional ML audit never falls back to regex and an
        LLM audit never falls back to mock. Generation failures preserve the
        evaluation result (status PARTIAL, generation status recorded).
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
        evaluator = getattr(audit, "evaluator", None) or "rule_based"

        # PHASE 1 — evaluation (per-evaluator; the result is immutable from
        # this point on: the shared generator never changes it).
        try:
            if evaluator == "traditional_ml":
                evaluation = await cls._evaluate_traditional_ml(audit, text_to_analyze, db)
            elif evaluator == "multimodel_router":
                evaluation = await cls._evaluate_multimodel_router(audit, text_to_analyze, db)
            elif evaluator == "llm":
                evaluation = await cls._evaluate_llm(audit, text_to_analyze, db)
            else:
                evaluation = await cls._evaluate_rule_based(audit, text_to_analyze, db)
        except (MLEvaluatorUnavailableError, LLMProviderUnavailableError) as e:
            # Explicit evaluator failure — never silently switch evaluators.
            # The coded error is exposed via breakdown["evaluator_error"] and
            # detail["evaluator_error_code"]; raw error_message stays internal.
            # Task 09: LLMProviderRequestError carries a specific code
            # (LLM_PROVIDER_TIMEOUT, LLM_RATE_LIMITED, ...) that supersedes the
            # generic LLM_EVALUATOR_UNAVAILABLE so the frontend can localize.
            logger.error(f"Evaluator {evaluator} unavailable for audit {id_audit}: {e}")
            if isinstance(e, MLEvaluatorUnavailableError):
                code = "ML_EVALUATOR_UNAVAILABLE"
            else:
                code = getattr(e, "code", None) or "LLM_EVALUATOR_UNAVAILABLE"
            breakdown = dict(audit.breakdown or {})
            breakdown["evaluator_error"] = {"code": code, "evaluator": evaluator, "message": str(e)}
            audit.breakdown = breakdown
            audit.status_audit = "FAILED"
            audit.stage2_status = "FAILED"
            audit.error_message = str(e)
            await db.commit()
            return
        except Exception as e:
            logger.exception(f"Evaluation failed for audit {id_audit} ({evaluator}): {e}")
            breakdown = dict(audit.breakdown or {})
            breakdown["evaluator_error"] = {"code": "EVALUATION_FAILED", "evaluator": evaluator, "message": str(e)}
            audit.breakdown = breakdown
            audit.status_audit = "FAILED"
            audit.error_message = str(e)
            await db.commit()
            return

        # PHASE 2 — shared response generation (verdict-preserving).
        breakdown = dict(audit.breakdown or {})
        try:
            generation = await NLPStage2Service.generate_response(
                text_to_analyze, evaluation, stage1_findings=evaluation.get("findings")
            )
            audit.ai_rewrite = generation.get("ai_rewrite")
            audit.acceptance_criteria = generation.get("acceptance_criteria")
            breakdown["generation"] = {
                "provider": generation.get("provider"),
                "model": generation.get("model"),
                "status": "DONE",
                "explanation": generation.get("explanation"),
                "recommendation": generation.get("recommendation"),
            }
            # Task 06: LLM INVEST observations are ADVISORY ONLY — they never
            # change the evaluator's verdict, score or findings.
            breakdown["ai_invest_notes"] = generation.get("ai_invest_observations")
            audit.status_audit = "COMPLETED"
            audit.stage2_status = "DONE"
            audit.error_message = None
        except Exception as e:
            # Generation failure: the evaluation result is PRESERVED and the
            # failure is reported separately (PARTIAL = evaluation available,
            # generation unavailable — for every evaluator).
            logger.warning(f"Response generation failed for audit {id_audit}: {e}")
            breakdown["generation"] = {
                "provider": settings.SLM_PROVIDER,
                "model": settings.SLM_MODEL,
                "status": "FAILED",
                "error": str(e),
            }
            breakdown["ai_invest_notes"] = None
            audit.stage2_status = "FAILED"
            audit.error_message = f"GENERATION_FAILED: {e}"
            audit.status_audit = "PARTIAL"
        audit.breakdown = breakdown
        await db.commit()

    # ────────────────────────────────────────────────────────────────
    # Task 06 evaluators (each keeps its own internal mechanism; the shared
    # contract in evaluation_contract.py normalizes the output shape).
    # ────────────────────────────────────────────────────────────────

    @classmethod
    async def _evaluate_rule_based(cls, audit, text_to_analyze: str, db: AsyncSession) -> Dict[str, Any]:
        """Evaluator A — Rule-Based (internal penalty-scoring preserved)."""
        stage1_result = NLPStage1Service.analyze_draft(text_to_analyze)
        findings = stage1_result["findings"]
        stories = stage1_result["stories"]

        score_calc = ScoringService.calculate_score(stories, findings)

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

        audit.skor_kualitas = score_calc["skor_kualitas"]
        if audit.skor_awal is None:
            audit.skor_awal = score_calc["skor_kualitas"]

        # Task 06 scoring framework: derive INVEST dimensions ONLY where the
        # rule engine can genuinely assess them (pedoman mapping). Dimensions
        # without rule detectors are INSUFFICIENT_EVIDENCE — never fabricated.
        has_tidak_lengkap = any(f["kategori_cacat"] == "TIDAK_LENGKAP" for f in findings)
        has_testability_defect = any(
            f["kategori_cacat"] in ("AMBIGUITY", "WEAK_DIRECTIVE", "PASSIVE_VOICE")
            for f in findings
        )
        labels = {
            "independent": "INSUFFICIENT_EVIDENCE",
            "negotiable": "INSUFFICIENT_EVIDENCE",
            "valuable": "FAIL" if has_tidak_lengkap else "PASS",
            "estimable": "INSUFFICIENT_EVIDENCE",
            "small": "INSUFFICIENT_EVIDENCE",
            "testable": "FAIL" if has_testability_defect else "PASS",
        }
        rationales = {
            "independent": "EVALUATOR_UNSUPPORTED_DIMENSION",
            "negotiable": "EVALUATOR_UNSUPPORTED_DIMENSION",
            "valuable": "MISSING_BENEFIT findings" if has_tidak_lengkap else "NO_DEFECT_DETECTED",
            "estimable": "EVALUATOR_UNSUPPORTED_DIMENSION",
            "small": "EVALUATOR_UNSUPPORTED_DIMENSION",
            "testable": "AMBIGUITY/WEAK_DIRECTIVE/PASSIVE_VOICE findings" if has_testability_defect else "NO_DEFECT_DETECTED",
        }
        dimensions = build_dimensions(labels, rationales=rationales)

        breakdown = score_calc["breakdown"]
        # NOTE: the contract is stored WITHOUT a nested breakdown (circular
        # reference); scorecard.breakdown carries the ISO/INVEST structure.
        contract = build_evaluation_result(
            evaluator="rule_based",
            verdict=overall_verdict(dimensions),
            score=score_calc["skor_kualitas"],  # internal penalty mechanism preserved
            dimensions=dimensions,
            model_version=None,  # deterministic lexicon, no model
            findings=findings,
            breakdown=None,
            metadata={
                "note": "score = internal category-penalty mechanism (preserved); "
                        "I/N/E/S dimensions unsupported by rule detectors (IE)",
            },
        )
        breakdown["evaluation"] = contract
        audit.breakdown = breakdown
        await db.commit()
        return contract

    @classmethod
    async def _evaluate_traditional_ml(cls, audit, text_to_analyze: str, db: AsyncSession) -> Dict[str, Any]:
        """Evaluator B — Traditional ML: genuine model inference, no fallback."""
        result = InvestMLService.evaluate_story_ml(text_to_analyze)
        dimensions = result["dimensions"]

        contract = build_evaluation_result(
            evaluator="traditional_ml",
            verdict=overall_verdict(dimensions),
            score=framework_score(dimensions),  # equal-weighted over the 6 genuine dimensions
            dimensions=dimensions,
            model_version=result.get("model_version"),
            findings=[],  # ML yields verdicts + confidence, not span findings (honest)
            breakdown=None,
            metadata={
                "limitations": "context features (backlog similarity / category position) use "
                               "neutral defaults in single-story serving mode",
                "trained_metrics": (InvestMLService.get_model_metadata() or {}).get("trained_metrics"),
            },
        )

        audit.skor_kualitas = contract["score"] if contract["score"] is not None else 0.0
        if audit.skor_awal is None:
            audit.skor_awal = contract["score"]
        audit.model_version = contract["model_version"]
        audit.breakdown = {"evaluation": contract}
        await db.commit()
        return contract

    @classmethod
    async def _evaluate_multimodel_router(cls, audit, text_to_analyze: str, db: AsyncSession) -> Dict[str, Any]:
        """Evaluator D — Multi-Model White-Box & K-Means Router V2 (auto router or direct V2 classifier)."""
        existing_breakdown = dict(audit.breakdown or {})
        requested_ml_model = existing_breakdown.get("requested_ml_model")
        if requested_ml_model in MultiModelRouterService.DIRECT_MODEL_MAP:
            result = MultiModelRouterService.evaluate_story_direct(text_to_analyze, requested_ml_model)
        else:
            result = MultiModelRouterService.evaluate_story_router(text_to_analyze)
        dimensions = result["dimensions"]

        contract = build_evaluation_result(
            evaluator="multimodel_router",
            verdict=overall_verdict(dimensions),
            score=framework_score(dimensions),
            dimensions=dimensions,
            model_version=result.get("model_version"),
            findings=[],
            breakdown=None,
            metadata=result.get("routing_metadata") or {},
        )

        audit.skor_kualitas = contract["score"] if contract["score"] is not None else 0.0
        if audit.skor_awal is None:
            audit.skor_awal = contract["score"]
        audit.model_version = contract["model_version"]
        audit.breakdown = {"evaluation": contract}
        await db.commit()
        return contract

    @classmethod
    async def _evaluate_llm(cls, audit, text_to_analyze: str, db: AsyncSession) -> Dict[str, Any]:
        """Evaluator C — LLM/SLM classification (real provider required)."""
        result = await NLPStage2Service.classify_story_with_llm(text_to_analyze)
        dimensions = result["dimensions"]

        model_version = f"{result.get('provider')}/{result.get('model')}"
        contract = build_evaluation_result(
            evaluator="llm",
            verdict=overall_verdict(dimensions),
            score=framework_score(dimensions),  # equal-weighted over the 6 genuine dimensions
            dimensions=dimensions,
            model_version=model_version,
            findings=[],  # LLM yields per-criterion verdicts + reasons, not span findings
            breakdown=None,
            metadata={"rationale_source": "per-criterion reason from the provider"},
        )

        audit.skor_kualitas = contract["score"] if contract["score"] is not None else 0.0
        if audit.skor_awal is None:
            audit.skor_awal = contract["score"]
        audit.model_version = contract["model_version"]
        audit.breakdown = {"evaluation": contract}
        await db.commit()
        return contract

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

        # Task 06: evaluator selection (rule_based default for backward
        # compatibility with clients that do not send the field).
        evaluator = (payload.evaluator or "rule_based").strip().lower()
        if evaluator not in EVALUATORS:
            raise AppException(
                message="Evaluator tidak valid",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_code="INVALID_EVALUATOR",
                errors=[{"field": "evaluator", "message": f"evaluator harus salah satu dari {sorted(EVALUATORS)}"}]
            )

        ml_model = payload.ml_model.strip().lower() if payload.ml_model else None
        if ml_model is not None:
            valid_by_evaluator = {
                "traditional_ml": {"v1_logistic_regression"},
                "multimodel_router": {"v2_auto_router", "v2_logistic_regression", "v2_decision_tree", "v2_complement_nb"},
            }
            allowed = valid_by_evaluator.get(evaluator, set())
            if ml_model not in allowed:
                raise AppException(
                    message="Model ML tidak valid untuk evaluator terpilih",
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    error_code="INVALID_ML_MODEL",
                    errors=[{"field": "ml_model", "message": f"ml_model tidak valid: {ml_model}"}]
                )

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
            breakdown={"requested_ml_model": ml_model} if ml_model else None,
            error_message=None,
            evaluator=evaluator,
            model_version=None
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

        breakdown_data = audit.breakdown or {}
        evaluation_contract = breakdown_data.get("evaluation") or {}

        # Task 10 Phase 2: explicit evaluator provenance. The audit row's
        # `evaluator` is the REQUESTED evaluator and is preserved verbatim even
        # on failure (never overwritten by a fallback). `actual_evaluator` is
        # the evaluator that produced the persisted evaluation contract —
        # null when no evaluation result exists (e.g. FAILED audits), so a
        # failed evaluation can never masquerade as a successful one.
        requested_evaluator = getattr(audit, "evaluator", None) or "rule_based"
        if evaluation_contract.get("evaluator"):
            actual_evaluator = evaluation_contract["evaluator"]
        elif audit.status_audit == "FAILED":
            actual_evaluator = None
        else:
            actual_evaluator = requested_evaluator

        return {
            "id_audit": audit.id_audit,
            "id_draf": draf.id_draf,
            "judul_klausul": draf.judul_klausul,
            "tipe_masukan": draf.tipe_masukan,
            "status_audit": audit.status_audit,
            "stage2_status": audit.stage2_status,
            "status_revisi": draf.status_revisi,
            "tanggal_audit": audit.tanggal_audit.isoformat() if audit.tanggal_audit else None,
            "evaluator": requested_evaluator,
            "requested_evaluator": requested_evaluator,
            "actual_evaluator": actual_evaluator,
            "model_version": audit.model_version,
            "evaluator_error_code": breakdown_data.get("evaluator_error", {}).get("code"),
            "evaluator_error": breakdown_data.get("evaluator_error"),
            "generation": breakdown_data.get("generation"),
            "ai_invest_notes": breakdown_data.get("ai_invest_notes"),
            "evaluation": breakdown_data.get("evaluation"),
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
                "status_audit": audit.status_audit,
                "evaluator": getattr(audit, "evaluator", None) or "rule_based",
                "model_version": audit.model_version,
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
