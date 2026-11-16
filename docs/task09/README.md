# TASK 09 — Complete Bilingual Localization & LLM/SLM Provider Integration

**Project:** ReqLint · **Date:** 2026-11-15 · **Branch:** `fix/frontend-docker-npm-ci` (work left uncommitted per the task rules)

## Outcome in one paragraph

The Groq-backed LLM/SLM evaluator is now **operationally verified against the real Groq API** end-to-end
(6-dimension INVEST classification + shared response generation + persistence + reanalysis), the root cause of
its previous failure was found and fixed, and the **entire user-facing application is now fully
Indonesian/English bilingual** — including the landing page that Task 08 deferred, the pages that ignored the
translation system, every toast/filter/aria-label/validation message, and Markdown/CSV/JSON export labels in
both the frontend generator and the backend export service. All three evaluators remain independently
selectable; evaluation integrity is unchanged.

## Documents

| File | Content |
|---|---|
| [BASELINE_AUDIT.md](./BASELINE_AUDIT.md) | Phase 0 read-only audit: architecture, gap inventory, provider path, root-cause hypothesis |
| [LOCALIZATION_COMPLETION_REPORT.md](./LOCALIZATION_COMPLETION_REPORT.md) | Route-by-route coverage table, lib-level localization, rendered verification, remaining strings |
| [GROQ_PROVIDER_DIAGNOSIS.md](./GROQ_PROVIDER_DIAGNOSIS.md) | Root cause (duplicate `.env` keys, last-wins), live model-catalog verification, model selection, secrets safety |
| [LLM_EVALUATOR_IMPLEMENTATION.md](./LLM_EVALUATOR_IMPLEMENTATION.md) | Typed provider errors, fail-fast, retry policy, serialization bug fix, frontend error mapping |
| [OLLAMA_COMPATIBILITY.md](./OLLAMA_COMPATIBILITY.md) | Ollama branch review (preserved), setup/validation steps, honest not-live-verified status |
| [TEST_RESULTS.md](./TEST_RESULTS.md) | All regression suites, new tests, real-Groq E2E transcript, browser verification, source audit |
| [RELEASE_READINESS.md](./RELEASE_READINESS.md) | DoD assessment, verification-level matrix, deployment checklist, risks |

## Quick facts

- **Root cause of the Groq failure:** `backend/.env` defined `SLM_PROVIDER` three times; dotenv last-wins made
  the effective provider `mock`, so the evaluator's mock-guard rejected every LLM audit before any network call.
  Additionally, the previously configured `llama-3.1-8b-instant` is no longer in the live Groq catalog —
  the new default is `openai/gpt-oss-120b` (live-verified; `openai/gpt-oss-20b` documented fallback).
- **Dictionary:** 211 → **383 keys**, ID/EN parity 100% (test-enforced). No new i18n library.
- **Live Groq latency observed:** ~1.6 s (models list), ~2.5 s (classification), ~2.9 s (generation).
- **Regression:** backend pytest **109 passed** (baseline 91), frontend Vitest **62 passed** (baseline 51),
  TypeScript clean, `next build` success, BDD **32 passed**, real-Groq E2E all PASS, rendered ID/EN
  verification in a real browser with locale round-trip.

## Rules compliance highlights

- No git commit/push/history rewrite; no destructive operations; Task 01–04C research artifacts untouched;
  Traditional ML model not retrained; all uncommitted Task 06–08 work preserved.
- The API key exists only in `backend/.env`; never printed, logged, committed, or included in tests/docs —
  reported only as `configured / missing`; a regression test asserts errors never leak it.
- Real-provider evidence is separate from mocked tests: live verification lives in
  `backend/scripts/task09_groq_e2e.py` + the transcript in TEST_RESULTS.md, never as a pytest test.
- No existing test was weakened; the suite-level `SLM_PROVIDER=mock` pin preserves the original mock-provider
  assumptions that the whole mocked suite was written against.
