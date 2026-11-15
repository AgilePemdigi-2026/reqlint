# IMPLEMENTATION_REPORT (Task 06)

**HEAD setelah implementasi:** `4d6f53c` + perubahan working tree (belum di-commit — menunggu instruksi).
**Semua perubahan = file berikut; tidak ada file riset/artefak yang disentuh.**

## File modified (6)

| File | Perubahan |
|---|---|
| `backend/app/services/audit_service.py` | Dispatch evaluator (rule_based/traditional_ml/llm); evaluation contract disimpan di `breakdown["evaluation"]`; verdict preservation (invest flags tidak lagi memotong skor → jadi `ai_invest_notes`); generation failure terpisah (PARTIAL + `generation.status=FAILED`); evaluator error eksplisit (`evaluator_error_code`); reanalyze reuse evaluator; `get_audit_detail` +`evaluator`/`model_version`/`generation`/`ai_invest_notes`/`evaluation`/`evaluator_error*` |
| `backend/app/services/invest_ml_service.py` | `MLEvaluatorUnavailableError`; `get_model_metadata()`; `evaluate_story_ml()` — genuine inference strict (tanpa fallback regex; artifact missing/corrupt/inference-fail = error eksplisit); legacy `evaluate_story()` tidak berubah |
| `backend/app/services/nlp_stage2.py` | `LLMProviderUnavailableError`; `classify_story_with_llm()` (Evaluator C — 3 label + reason, label off-contract → IE `PROVIDER_LABEL_INVALID`); `generate_response()` shared generator (grounded pada findings; verdict/score preserved di output; mock = template jujur berlabel); `Stage2OutputModel` +`explanation/recommendation/provider/model`; `run_stage2` legacy tetap |
| `backend/app/services/…/init_db.py` | Migrasi kolom ringan idempotent (`evaluator`, `model_version` di `audit_kebutuhan`) untuk DB eksisting — SQLite PRAGMA, PostgreSQL ALTER+except |
| `backend/app/db/models.py` | `AuditKebutuhan.evaluator` (default `rule_based`) + `model_version` |
| `backend/app/core/config.py` | SMTP_* + `PUBLIC_BASE_URL` |
| `backend/app/services/auth_service.py` | `forgot_password` kirim email via SMTP (stdlib smtplib, `asyncio.to_thread`); tautan reset `PUBLIC_BASE_URL/reset-password?token=…`; tanpa SMTP → warning (tanpa token di log); token tidak pernah masuk respons/log |
| `backend/app/schemas/audit.py` | `CreateAuditRequest.evaluator` (default `rule_based`) |
| `backend/requirements.txt` | +`scikit-learn==1.7.2`, +`joblib>=1.3.0` |
| `backend/Dockerfile` | COPY bundle ML ke `/app/pm-docs/rubrics/` |
| `backend/.env.example` | dokumentasi variabel SMTP + PUBLIC_BASE_URL |
| `frontend-qa/src/lib/api.ts` | `EvaluatorId`; payload `evaluator`; `BackendAuditDetail` +field Task 06 |
| `frontend-qa/src/app/(app)/editor/page.tsx` | Selector 3 evaluator (default Rule-Based); payload evaluator; fallback browser HANYA rule_based (ML/LLM = pesan error eksplisit, tanpa ganti evaluator) |
| `frontend-qa/src/app/(app)/audit/[id]/page.tsx` | Badge evaluator + model_version + generation status; alert `evaluatorError`; kartu advisory `ai_invest_notes` (terpisah dari findings) |
| `frontend-qa/src/lib/analyzer/adapter.ts` | Return-type + passthrough `evaluator/modelVersion/evaluatorError/generation/aiInvestNotes` |
| `frontend-qa/src/components/audit/summary-card.tsx` | Meter "ISO 29148" → "Praktik Dokumen (heuristik)" |
| `frontend-qa/src/components/landing/sections.tsx` | Klaim ISO dilunakkan (prinsip INVEST; kosakata ISO; bukan audit kepatuhan) |
| `frontend-qa/src/app/(app)/help/page.tsx` + `lib/i18n.ts` | Kartu FAQ in-app menautkan FAQ landing (i18n id/en) |

## File created (backend/tests)

`backend/tests/test_task06_evaluators.py` — 20 test: kontrak & framework scoring; ML inference nyata + missing/corrupt artifact; LLM classification (mock-unavailable, parse, coerce); verdict preservation; pipeline dispatch (rule_based/ML/LLM); 422 invalid evaluator; reanalyze reuse; SMTP reset (mocked SMTP) + no-token-leak.

## Architectural decisions

1. Kontrak disimpan di `breakdown["evaluation"]` (JSON kolom existing) — tanpa migrasi struktural DB; kolom baru `evaluator/model_version` + migrasi ringan.
2. Verdict preservation di level pipeline (bukan mengubah ScoringService) — ScoringService.calculate_score tetap utuh (legacy endpoint + test P0.1 tetap hijau).
3. ML strict: fallback regex HANYA di endpoint legacy; evaluator baru error eksplisit.
4. Evaluator C + mock = FAILED eksplisit (`LLM_EVALUATOR_UNAVAILABLE`) — mock tidak pernah menyamar sebagai analisis nyata.
5. Fallback browser frontend hanya untuk Rule-Based.
