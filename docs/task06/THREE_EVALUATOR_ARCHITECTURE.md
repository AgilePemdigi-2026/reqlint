# THREE_EVALUATOR_ARCHITECTURE (Task 06)

## Arsitektur final

```
User Story Input (Text/PDF)
   → Evaluator Selection (frontend selector; payload.evaluator)
   → Selected Evaluator (backend dispatch di audit_service._execute_pipeline)
        ├─ rule_based     → NLP Stage-1 + penalty scoring (mekanisme internal dipertahankan)
        ├─ traditional_ml → genuine model inference (bundle 2.1.0-srs-hybrid, 23 fitur)
        └─ llm            → LLM classification (real provider wajib; mock = error eksplisit)
   → Immutable Evaluation Result (kontrak di breakdown["evaluation"])
   → Shared Response Generator (nlp_stage2.generate_response — verdict-preserving)
   → Final Audit Report (skor + findings + evidence + penjelasan + rekomendasi + AC + sumber)
```

## Kontrak evaluation result (breakdown["evaluation"] + detail["evaluation"])

```json
{
  "evaluator": "rule_based | traditional_ml | llm",
  "model_version": null | "2.1.0-srs-hybrid" | "groq/llama-3.1-8b-instant",
  "verdict": "PASS | FAIL | INSUFFICIENT_EVIDENCE",
  "score": 0.0–100.0,
  "confidence": null,
  "dimensions": {
    "independent": {"label": "PASS|FAIL|IE", "confidence": 0..1|null, "rationale": "kode/teks"}
  },
  "assessed_dimensions": ["…"],
  "invest_framework_score": 0.0–100.0 | null,
  "findings": [],
  "evidence": [],
  "breakdown": null,
  "metadata": { "limitations": "…" }
}
```

**Scoring framework (keputusan owner):** INVEST, 0–100, initial equal weighting (100 × Σ PASS / Σ assessed; IE dikecualikan + renormalisasi). Tidak diarang: dimensi yang tak dapat dinilai evaluator = IE.

| Evaluator | Dimensi genuin | Overall score |
|---|---|---|
| rule_based | V (←TIDAK_LENGKAP), T (←AMBIGUITY/WEAK_DIRECTIVE/PASSIVE_VOICE); I/N/E/S = IE | **skor penalty internal** (mekanisme dipertahankan) |
| traditional_ml | keenam dari `predict_proba` (threshold 0.5; confidence = proba) | framework equal-weighted |
| llm | keenam dari klasifikasi LLM (+ reason) | framework equal-weighted |

**Limitasi jujur ML (di metadata kontrak):** 10 fitur konteks (backlog similarity/posisi kategori) memakai default netural pada mode single-story.

## Verdict preservation (strict separation)

- Generator (`nlp_stage2.generate_response`) menerima evaluation result dan **hanya** menghasilkan explanation/recommendation/rewrite/AC.
- invest observasi LLM = `ai_invest_notes` (advisory) di breakdown — **tidak pernah** memotong skor (penalty −4 dihapus dari pipeline rule_based; teruji).
- Kegagalan generator → status `PARTIAL` + `generation.status=FAILED`; evaluation result tetap utuh.
- Evaluator gagal → status `FAILED` + `evaluator_error_code` (`ML_EVALUATOR_UNAVAILABLE` / `LLM_EVALUATOR_UNAVAILABLE` / `EVALUATION_FAILED`) — **tanpa fallback evaluator lain**.
- Reanalyze reuse `evaluator` + `model_version` yang tersimpan → before/after sebanding (skor_awal vs skor_kualitas + evaluation contract per run).

## API changes

| Endpoint | Perubahan |
|---|---|
| `POST /audits` | payload baru: `evaluator` (default `rule_based`; 422 `INVALID_EVALUATOR` bila tidak sah) |
| `GET /audits/{id}` | field baru: `evaluator`, `model_version`, `evaluator_error_code`, `evaluator_error`, `generation`, `ai_invest_notes`, `evaluation` (kontrak) |
| Endpoint lain | tidak berubah (backward compatible) |

## Environment variables baru

`SMTP_HOST`, `SMTP_PORT` (587), `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS` (true), `PUBLIC_BASE_URL` — dokumen lengkap di `IMPLEMENTATION_REPORT.md`.

## Dependency changes

`scikit-learn==1.7.2` (parity dgn bundle; versi berbeda memicu InconsistentVersionWarning — dilaporkan), `joblib>=1.3.0`. Dockerfile men-COPY bundle ML ke `/app/pm-docs/rubrics/` (path kandidat loader).
