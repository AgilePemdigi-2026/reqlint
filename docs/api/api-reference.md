# API reference

REST API of the FastAPI backend (`backend/app/`), verified against `bfe72aa`.

- Base URL: `/api/v1` (configurable via `API_V1_STR`).
- Interactive OpenAPI docs: **`/docs`** (Swagger UI) and `/redoc` on the running backend; the
  machine-readable schema is at `/api/v1/openapi.json`. This page is a hand-written companion —
  the live OpenAPI document is authoritative.
- All endpoints return JSON unless noted.

## Conventions

**Success envelope** (all endpoints except the two exceptions below):

```json
{ "status": "success", "message": "…", "data": { } }
```

**Error envelope:**

```json
{ "status": "error", "message": "…", "error_code": "STABLE_CODE", "errors": [ { "field": "…", "message": "…" } ] }
```

`error_code` is a stable machine-readable identifier; `errors` is populated for validation errors
(422). `GET /` and `POST /api/v1/requirements/audit` are the only non-enveloped responses (root
info dict; bare `AuditResponse` respectively). `GET /audits/{id}/export` returns raw file bytes.

**Authentication** — `Authorization: Bearer <JWT>` (from `POST /auth/login`). Header-based JWT;
no cookies. Endpoints marked *optional* accept guests. All timestamps are ISO-8601.

## Endpoint summary

| # | Method | Path | Auth | Purpose |
|---|---|---|---|---|
| 1 | GET | `/` | — | Service info (name, version, doc links) |
| 2 | GET | `/api/v1/health` | — | DB/Redis/SLM health report |
| 3 | POST | `/api/v1/auth/register` | — | Create account (201) |
| 4 | POST | `/api/v1/auth/login` | — | Obtain JWT |
| 5 | GET | `/api/v1/auth/me` | ✓ | Current user profile |
| 6 | POST | `/api/v1/auth/forgot-password` | — | Request reset token (email optional) |
| 7 | POST | `/api/v1/auth/reset-password` | — | Reset with token |
| 8 | POST | `/api/v1/documents/upload` | optional | Upload PDF, extract text |
| 9 | POST | `/api/v1/audits` | ✓ | Create audit (202) |
| 10 | GET | `/api/v1/audits` | ✓ | List audits (pagination, filters) |
| 11 | GET | `/api/v1/audits/{id_audit}/status` | ✓ | Lightweight status poll |
| 12 | GET | `/api/v1/audits/{id_audit}` | ✓ | Full audit result |
| 13 | POST | `/api/v1/audits/{id_audit}/reanalyze` | ✓ | Clear findings and re-run (202) |
| 14 | POST | `/api/v1/audits/{id_audit}/apply` | ✓ | Apply AI rewrite / acceptance criteria |
| 15 | PUT | `/api/v1/audits/{id_audit}/revision` | ✓ | Manual revision + re-score |
| 16 | GET | `/api/v1/audits/{id_audit}/export` | ✓ | Export audit (pdf/md/json, id/en) |
| 17 | POST | `/api/v1/lint` | ✓ | Stateless Stage-1 lint |
| 18 | POST | `/api/v1/requirements/audit` | ✓ | Legacy standalone analyzer |

## Health & root

### `GET /api/v1/health`
No params. Data: `{ "db": "up|down", "redis": "up|down", "slm": "mock|up", "version": "1.0.0" }`.
`redis` is checked only in `AUDIT_EXECUTION_MODE=celery` (reported `"up"` unconditionally in
inline mode); `slm` is `"mock"` when `SLM_PROVIDER=mock`, else `"up"` (never `"down"`).

### `GET /`
Non-enveloped: `{ "name": "ReqLint API", "version": "1.0.0", "docs": "/docs", "health": "/api/v1/health" }`.

## Auth

### `POST /auth/register` → 201
Body: `{ name (2–100 chars), email (EmailStr), password (min 8), password_confirmation }`.
Data: `{ id_user, name, email, tanggal_registrasi }`.
Errors: `422 INVALID_PASSWORD` (confirmation mismatch, or missing letter+digit), `409 EMAIL_TAKEN`,
`422 VALIDATION_ERROR`.

### `POST /auth/login` → 200
Body: `{ email, password }`. Data: `{ access_token, token_type: "bearer", expires_in,
user: { id_user, name, email } }`. Errors: `401 INVALID_CREDENTIALS`.

### `GET /auth/me` → 200
Data: `{ id_user, name, email, tanggal_registrasi }`. Errors: `401 UNAUTHORIZED`.

### `POST /auth/forgot-password` → 200 (always)
Body: `{ email }`. Always returns `data: {}` (anti-enumeration). Creates a SHA-256-hashed token
(1 h expiry); emails it only when `SMTP_HOST` is configured.

### `POST /auth/reset-password` → 200
Body: `{ token, password (min 8), password_confirmation }`. Data: `{}`.
Errors: `422 INVALID_PASSWORD`, `400 INVALID_RESET_TOKEN`, `404 USER_NOT_FOUND`.

## Documents

### `POST /documents/upload` → 200 (multipart)
Auth optional (guests allowed; authenticated uploads are persisted as `DokumenUpload`).
Form field: `file` (PDF only). Data: `{ id_dokumen (null for guests), nama_dokumen,
ukuran_dokumen (bytes), jumlah_halaman, jumlah_karakter, truncated (bool), teks }` — extracted
text (truncated to `MAX_TEXT_CHARS` with `truncated: true`).
Errors: `422 INVALID_FILE_FORMAT` (non-PDF extension, missing `%PDF` magic, extraction failure),
`413 FILE_TOO_LARGE` (> `MAX_UPLOAD_MB`), `422 EMPTY_PDF_TEXT` (scanned/no text layer).

## Audits

### `POST /audits` → 202
Body: `{ konten: string (required), judul_klausul?: string, tipe_masukan: "manual"|"pdf" = "manual",
id_dokumen?: int, evaluator: "rule_based"|"traditional_ml"|"llm" = "rule_based" }`.
Data: `{ id_draf, id_audit, status_audit: "PROCESSING", stage2_status: "PENDING",
poll_url: "/api/v1/audits/{id}/status" }`.
Errors: `422 EMPTY_DRAFT`, `422 DRAFT_TOO_LONG` (> `MAX_TEXT_CHARS`), `422 MISSING_DOCUMENT_ID`
(`tipe_masukan="pdf"` without `id_dokumen`), `404 DOCUMENT_NOT_FOUND`, `422 INVALID_EVALUATOR`.
Execution: BackgroundTasks (inline) or Celery dispatch with inline fallback.

### `GET /audits` → 200
Query: `page (≥1, default 1)`, `limit (1–50, default 10)`, `q`, `min_score`, `max_score`,
`status_revisi`, `date_from` / `date_to` (ISO; invalid values silently ignored), `sort_by`
(`tanggal|skor`, default `tanggal`), `order` (`desc|asc`, default `desc`).
Data: `{ items: [{ id_audit, id_draf, tanggal_audit, judul_klausul, skor_kualitas, status_revisi,
status_audit }], pagination: { page, limit, total_items, total_pages }, has_any_history }`.
Errors: `401`, `422 VALIDATION_ERROR`.

### `GET /audits/{id_audit}/status` → 200
Data: `{ id_audit, status_audit, stage2_status, stage1_ready (bool) }`. Errors: `401`,
`404 AUDIT_NOT_FOUND`.

### `GET /audits/{id_audit}` → 200
Full result. Data keys: `id_audit, id_draf, judul_klausul, tipe_masukan, status_audit,
stage2_status, status_revisi, tanggal_audit, evaluator, requested_evaluator, actual_evaluator,
model_version, evaluator_error_code, evaluator_error, generation, ai_invest_notes, evaluation,
scorecard ({skor_awal, skor_kualitas, breakdown:{iso_29148, invest}}), ringkasan
({ambiguity, tidak_lengkap, weak_directive, passive_voice, total}), temuan
(findings with kategori_cacat, severity, stage, iso_characteristic, potongan_teks_asli,
highlight_start/end, saran_perbaikan), rekomendasi_ai ({ai_rewrite, acceptance_criteria} | null),
ai_suggestion_source ("mock"|"provider"|null), diff ({original, revised}), notifikasi`.
Errors: `401`, `404 AUDIT_NOT_FOUND`.

### `POST /audits/{id_audit}/reanalyze` → 202
No body. Clears persisted findings, resets to `PROCESSING`/`PENDING`, re-dispatches.
Data: same as create. Errors: `401`, `404 AUDIT_NOT_FOUND`, `409 AUDIT_IN_PROGRESS`.

### `POST /audits/{id_audit}/apply` → 200
Body: `{ terapkan: string[] }` — any of `"rewrite"`, `"acceptance_criteria"`. Applies the stored
Stage-2 suggestion(s) to the draft and re-scores synchronously.
Data: `{ id_audit, status_revisi: "SUDAH_DIREVISI", konten_revisi, skor_awal, skor_kualitas,
label, ringkasan, temuan, diff }`. Errors: `401`, `404 AUDIT_NOT_FOUND`, `409 AI_NOT_READY`
(Stage 2 not DONE or no suggestion stored).

### `PUT /audits/{id_audit}/revision` → 200
Body: `{ konten_revisi: string (required) }`. Manual edit + synchronous re-score. Same data shape
as apply. Errors: `401`, `422 EMPTY_DRAFT`, `404 AUDIT_NOT_FOUND`. *(Not called by the current UI.)*

### `GET /audits/{id_audit}/export` → 200 (file bytes)
Query: `format` (**required**: `pdf|md|json`), `lang` (`id|en`, default `id`). Returns the rendered
file with `Content-Disposition: attachment; filename="reqlint-audit-{id}.{ext}"`; records a
`HistoryDownload` row on success.
Errors: `422 UNSUPPORTED_FORMAT`, `422 UNSUPPORTED_LANG`, `404 AUDIT_NOT_FOUND`,
`409 AUDIT_NOT_READY` (status not COMPLETED/PARTIAL), `500 EXPORT_FAILED`.

## Lint & legacy analyzer

### `POST /lint` → 200
Body: `{ konten: string = "" }`. Stateless Stage-1 analysis; empty input returns
`{ skor_perkiraan: 100.0, ringkasan: {all zeros}, temuan: [] }`.
Data: `{ skor_perkiraan, ringkasan: {ambiguity, tidak_lengkap, weak_directive, passive_voice,
total}, temuan: [{kategori_cacat, severity, potongan_teks_asli, highlight_start, highlight_end,
saran_perbaikan}] }`. Errors: `401`.

### `POST /requirements/audit` → 200 (bare `AuditResponse`, no envelope)
Body: `{ requirement_text: string (required, ≤ MAX_TEXT_CHARS), override_language?: "id"|"en" }`.
Legacy hybrid analyzer: Stage-1 rules + `InvestMLService.evaluate_story` (heuristic-or-ML).
Data: `{ requirement_text, detected_language, quality_score, ambiguity_index, completeness_score,
verifiability_score, smells: [{rule_id, category, severity, message, target_text, start_char,
end_char}], revisions: [{original_text, suggested_text, rationale, framework: "INVEST & Connextra"}] }`.
Errors: `401`, `400` (empty text), `422 VALIDATION_ERROR`. Used today only by an unused legacy UI
component; kept for compatibility.

## Non-goals

- No WebSocket/SSE endpoints — clients poll `GET /audits/{id}/status`.
- No admin endpoints; no multi-tenancy — ownership filtering is per-user.
