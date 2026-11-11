from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List

from app.api.deps import get_current_user
from app.db.models import User
from app.schemas.requirement_schema import AuditRequest, AuditResponse
from app.services.nlp_stage1 import NLPStage1Service
from app.services.scoring import ScoringService
from app.services.invest_ml_service import InvestMLService

router = APIRouter()

CATEGORY_MAP = {
    "AMBIGUITY": "Ambiguity",
    "TIDAK_LENGKAP": "Incompleteness",
    "WEAK_DIRECTIVE": "Unverifiable",
    "PASSIVE_VOICE": "Unverifiable"
}

@router.post("/audit", response_model=AuditResponse)
def audit_requirement(payload: AuditRequest, current_user: User = Depends(get_current_user)):
    """
    Analyzes an Agile User Story text for INVEST criteria compliance, completeness, and ambiguity.
    Supports both Indonesian and English text with hybrid Stage 1 NLP and INVEST ML models.

    P0/SEC-02: this legacy endpoint previously allowed anonymous access with a
    CPU-heavy pipeline. Authentication is now REQUIRED (breaking change).
    """
    raw_text = (payload.requirement_text or "").strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="requirement_text must not be empty.")

    # 1. Detect language
    if payload.override_language:
        lang = payload.override_language.lower()
    else:
        text_lower = raw_text.lower()
        if any(w in text_lower for w in ["sebagai", "ingin", "sehingga", "supaya", "agar", "saya"]):
            lang = "id"
        else:
            lang = "en"

    # 2. Stage 1 Analysis (spaCy + Lexicon)
    stage1_res = NLPStage1Service.analyze_draft(raw_text)
    findings = stage1_res["findings"]
    stories = stage1_res["stories"]

    # 3. INVEST Machine Learning Evaluation
    invest_eval = InvestMLService.evaluate_story(raw_text)

    # 4. Scoring (ISO 29148 + INVEST breakdown)
    score_res = ScoringService.calculate_score(stories, findings, invest_results=invest_eval)
    iso_breakdown = score_res["breakdown"]["iso_29148"]

    # 5. Format smells according to API schema
    smells: List[Dict[str, Any]] = []
    for f in findings:
        cat = f.get("kategori_cacat", "AMBIGUITY")
        smells.append({
            "rule_id": cat,
            "category": CATEGORY_MAP.get(cat, "Ambiguity"),
            "severity": f.get("severity", "MEDIUM"),
            "message": f.get("saran_perbaikan", "Perbaiki bagian teks ini"),
            "target_text": f.get("potongan_teks_asli", ""),
            "start_char": f.get("highlight_start", 0),
            "end_char": f.get("highlight_end", len(f.get("potongan_teks_asli", "")))
        })

    # 6. Generate revision suggestion if defects exist
    revisions: List[Dict[str, Any]] = []
    if smells or any(not passed for k, passed in invest_eval.items() if k != "probabilities"):
        if lang == "id":
            # Clean template suggestion
            cleaned = raw_text
            for f in findings:
                if f.get("kategori_cacat") in ["AMBIGUITY", "WEAK_DIRECTIVE"]:
                    bad = f.get("potongan_teks_asli", "")
                    if bad and bad.lower() in ["cepat", "segera"]:
                        cleaned = cleaned.replace(bad, "< 2 detik")
                    elif bad and bad.lower() in ["mudah", "bagus"]:
                        cleaned = cleaned.replace(bad, "dalam 3 langkah terpandu")
                    elif bad and bad.lower() in ["sebaiknya", "bisa", "harus"]:
                        cleaned = cleaned.replace(bad, "dapat")

            revisions.append({
                "original_text": raw_text,
                "suggested_text": cleaned if cleaned != raw_text else f"Sebagai Pengguna, saya ingin {raw_text.replace('Sebagai', '').strip()}, sehingga kebutuhan dapat terverifikasi dengan jelas.",
                "rationale": "Mengganti kata sifat kualitatif dan direktif lemah dengan metrik terukur serta memenuhi standar format Connextra (INVEST).",
                "framework": "INVEST & Connextra"
            })
        else:
            cleaned = raw_text
            for f in findings:
                if f.get("kategori_cacat") in ["AMBIGUITY", "WEAK_DIRECTIVE"]:
                    bad = f.get("potongan_teks_asli", "")
                    if bad and bad.lower() in ["fast", "quickly"]:
                        cleaned = cleaned.replace(bad, "in under 2 seconds")
                    elif bad and bad.lower() in ["easy", "easily"]:
                        cleaned = cleaned.replace(bad, "within 3 guided steps")
                    elif bad and bad.lower() in ["should", "could"]:
                        cleaned = cleaned.replace(bad, "can")

            revisions.append({
                "original_text": raw_text,
                "suggested_text": cleaned if cleaned != raw_text else f"As a user, I want {raw_text.replace('As a', '').strip()}, so that the outcome is measurable.",
                "rationale": "Replaced qualitative adjectives and weak directives with measurable criteria complying with INVEST.",
                "framework": "INVEST & Connextra"
            })

    unambiguous_val = float(iso_breakdown.get("unambiguous") or 100.0)
    ambiguity_index = round(max(0.0, min(1.0, 1.0 - (unambiguous_val / 100.0))), 2)

    return AuditResponse(
        requirement_text=raw_text,
        detected_language=lang,
        quality_score=float(score_res["skor_kualitas"]),
        ambiguity_index=ambiguity_index,
        completeness_score=float(iso_breakdown.get("complete") or 100.0),
        verifiability_score=float(iso_breakdown.get("verifiable") or 100.0),
        smells=smells,
        revisions=revisions
    )
