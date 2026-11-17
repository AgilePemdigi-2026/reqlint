# Product overview

What ReqLint actually does today, based on the implementation (verified against `bfe72aa`).
This page describes the product as it exists — including partial and simulated parts.

## Core user flow

1. **Write or import a draft** — free text (one or many user stories) or PDF/TXT/MD import
   (PDF text is extracted server-side; up to 10 MB, 50,000 characters).
2. **Choose an evaluator** — Rule-Based (default), Traditional ML, or LLM/SLM.
3. **Run the audit** — the backend evaluates the draft and generates advisory content.
4. **Review results** — scorecard, per-category findings with highlighted spans, INVEST dimension
   results, provenance banner (which evaluator actually ran, model version), Stage-2 advisory.
5. **Revise** — 1-click apply of the AI rewrite / acceptance criteria, or manual editing; the
   Stage-1 score is recalculated synchronously.
6. **Export** — Markdown, CSV, JSON from the UI (the API also supports PDF).

## What each part does

| Area | Capability | Status |
|---|---|---|
| Editor | Draft editing with live squiggle underlines, clause/word/flag counts, sample templates | Implemented |
| Landing demo | Interactive in-browser analysis without an account or backend | Implemented (local rule engine) |
| Audits | Three evaluators, shared contract, provenance tracking, background execution | Implemented |
| Findings | Category, severity, highlighted text span, per-finding recommendation | Implemented (Stage-1 findings) |
| INVEST dimensions | PASS/FAIL with confidence (ML/LLM) or `INSUFFICIENT_EVIDENCE` (rule-based) | Implemented |
| Scorecard | 0–100 score, grade, ISO 29148 / INVEST meters (missing evidence shown as "–") | Implemented |
| Stage-2 advisory | Rewrite + Gherkin acceptance criteria; real provider or labeled demo mock | Implemented (mock is not AI — clearly labeled) |
| Apply / revision | Apply suggestions or manual edit with synchronous re-score | Implemented (manual revision is API-only; the UI uses apply + local editing) |
| History | Server-side list (search, filters, pagination) merged with local drafts | Implemented |
| Export | JSON/Markdown/PDF (API), Markdown/CSV/JSON (UI) | Implemented; **PDF not offered in the UI** |
| Auth | Register, login, profile, password reset (SMTP delivery optional) | Implemented |
| PDF upload | Server-side extraction, validation, guest uploads allowed | Implemented |
| Bilingual UI | Indonesian/English toggle, 501 keys | Implemented |
| Health | `/api/v1/health` (DB check; see backend.md for redis/slm semantics) | Implemented |
| Contact form | Client-side simulation only — no backend endpoint | **Simulated** |
| Password-reset email | Token delivery only when `SMTP_HOST` is configured | Implemented, delivery optional |

## Honest distinctions the product makes

- **Requested vs actual evaluator.** Every audit records both; the UI shows a provenance banner.
  If an evaluator fails, the audit fails with a coded error instead of substituting another
  evaluator's result.
- **Mock is not AI.** With `SLM_PROVIDER=mock` (default), Stage-2 suggestions are generic built-in
  templates explicitly labeled in API (`ai_suggestion_source: "mock"`) and UI. The LLM evaluator
  refuses to run on the mock provider.
- **Missing evidence is shown, not invented.** INVEST dimensions without evidence render as
  `INSUFFICIENT_EVIDENCE` / "–", never as fabricated scores.

## Known product limitations

- The in-app Help page claims PDF export; the UI currently offers Markdown/CSV/JSON (PDF is
  API-only).
- The editor shows a static "Backend FastAPI Terhubung" pill (always green); the real connectivity
  indicator is the navbar health badge (30 s polling).
- The notifications popover is decorative (static welcome text).
- History deletion only affects locally stored rows; backend audit rows have no delete API.
- Register-page Terms/Privacy links are placeholders (`#`).

## Roles and access

Single-role model: any authenticated user sees only their own audits and documents (ownership is
enforced server-side; see `backend/tests/test_task10_evaluator_pipeline.py` security tests and
`docs/task07/SECURITY_REVIEW.md` for the reviewed cases). Guests can use the landing demo and PDF
upload (`POST /documents/upload` accepts optional authentication), but not audits.
