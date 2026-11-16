# TEST RESULTS — Task 09

**Date:** 2026-11-15 · All commands executed from their standard working directories on Windows (Git Bash).

## 1. Regression suites (Phase 7)

| Suite | Command | Baseline | Result after Task 09 |
|---|---|---|---|
| Backend pytest | `python -m pytest tests -q` (from `backend/`) | 91 passed | **109 passed** ✅ |
| Frontend Vitest | `npx vitest run` (from `frontend-qa/`) | 51 passed | **62 passed** ✅ |
| TypeScript | `npx tsc --noEmit` | clean | **clean** ✅ |
| Production build | `npx next build` | success | **success (13 routes)** ✅ |
| BDD | `python ../run_bdd.py` (from `backend/`) | 32 passed | **32 passed** ✅ |
| Real Groq E2E | `python scripts/task09_groq_e2e.py` (from `backend/`) | — (new) | **all steps PASS** ✅ |

No existing assertion was weakened. The only pre-existing-test modification is *environmental*: the suite
conftest now pins `SLM_PROVIDER=mock` before app import so mocked tests remain deterministic/offline after the
developer `.env` was fixed to point at real Groq (the tests were originally written against that same mock
behavior — see LLM_EVALUATOR_IMPLEMENTATION.md §1.4).

## 2. New tests added

### Backend — `backend/tests/test_task09_provider.py` (18 tests, all mocked/offline)

- Missing `GROQ_API_KEY` fails fast with `LLM_PROVIDER_KEY_MISSING`; HTTP client never constructed.
- Mock-provider guard unchanged (`LLM_EVALUATOR_UNAVAILABLE`).
- Typed error mapping: timeout (retried once) → `LLM_PROVIDER_TIMEOUT`; 401 → `LLM_PROVIDER_AUTH_FAILED`
  (fail-fast, single call); 404 → `LLM_MODEL_NOT_FOUND`; 429 → `LLM_RATE_LIMITED`; 503 →
  `LLM_PROVIDER_SERVER_ERROR`; non-JSON output → `LLM_INVALID_RESPONSE` (after retry).
- Generation path uses the same typed errors.
- **Secret safety:** a fake key injected into the environment never appears in error text/`str(e)`.
- Pipeline surfacing: `evaluator_error_code == "LLM_RATE_LIMITED"` on detail; evaluation not fabricated on failure.
- Generation failure → `PARTIAL` with evaluation, verdict, score and six dimensions preserved.
- Real-provider shape regression: mocked provider payloads of the REAL shape (incl. acceptance criteria) →
  audit `COMPLETED`, criteria stored as serializable dicts, advisory notes separate from the verdict.
  (This test would have caught the pydantic→JSON-column serialization bug found by the live E2E.)
- Reanalysis keeps evaluator identity after a provider error.
- Backend exports: ID default labels, EN labels (`lang` param), PDF renders with EN labels,
  unknown `lang` → 422 `UNSUPPORTED_LANG`.

### Frontend — `src/lib/i18n-task09.test.ts` (11 tests)

- Namespace-wide ID/EN non-empty parity; ~70 required keys enumerated across landing/demo/editor/history/
  audit/components/auth/shell/badge/labels/ai-status/adapter/validation/llm_error.
- Locale-switch spot checks (with a localStorage stub for the node test environment).
- `resolveAiSuggestionStatus` locale behavior; category/grade/tagline labels; `formatDate` locale switching.
- Locale-aware zod validation messages (EN required-message, ID length message, EN mismatch message).
- Exports follow the UI locale: EN markdown headings, ID backward-compatible default, EN/ID CSV headers,
  `buildExport` passes locale through.

## 3. Real Groq E2E transcript (Phase 4 — recorded separately from mocked tests)

Script: `backend/scripts/task09_groq_e2e.py` (isolated temp SQLite; dev DB untouched; key never printed).

```
[PASS] backend recognizes Groq configuration — provider=openai_compatible
       base=https://api.groq.com/openai model=openai/gpt-oss-120b timeout=30s GROQ_API_KEY=configured
[PASS] provider connectivity (GET /models) — HTTP 200 in 1.6s, 11 models, configured model listed: True
[PASS] real 6-dimension LLM classification — labels={"independent": "PASS", "negotiable": "PASS",
       "valuable": "PASS", "estimable": "PASS", "small": "PASS", "testable": "PASS"} in 2.5s
[PASS] structured response satisfies the evaluation contract — verdict=PASS score=100.0
       model_version=openai_compatible/openai/gpt-oss-120b
[PASS] shared response generation (real provider) — verdict_preserved=PASS score_preserved=100.0
       criteria=3 in 2.9s
[PASS] audit persisted + retrieved via API (LLM evaluator) — status=COMPLETED stage2=DONE evaluator=llm
       model=openai_compatible/openai/gpt-oss-120b generation=DONE/openai_compatible in 10.9s
[PASS] frontend-facing LLM fields present — ai_suggestion_source=provider ai_invest_notes=present
[PASS] reanalysis keeps evaluator identity (llm) end-to-end — status=COMPLETED evaluator=llm
```

Test story (non-sensitive, per the task doc): *"As a registered customer, I want to view my order status so
that I can track the delivery of my purchase."* No credentials or authorization headers recorded.

**Defect found & fixed by this run:** the shared generator returned pydantic `AcceptanceCriteriaModel` objects
which SQLAlchemy cannot serialize into the audit JSON column → every real-provider audit would have hung in
`PROCESSING`. Fixed by returning plain dicts; regression test added (see LLM_EVALUATOR_IMPLEMENTATION.md §1.1).

## 4. Rendered-page localization verification (browser, production build)

`next start -p 3100` + in-app browser (DOM snapshot checks + screenshot):

| Check | Result |
|---|---|
| Landing ID (default) — hero/features/CTA/nav Indonesian, `lang="id"`, no EN leakage | ✅ |
| Landing EN (persisted locale + reload) — all sections English, `lang="en"`, no ID leakage | ✅ |
| Login EN — title/CTA/demo/forgot/aria ("Show password") English, no ID leakage | ✅ |
| Login ID (switch back) — fully Indonesian, no EN leakage, `lang` returns to `id` | ✅ |
| Demo card EN — paste/upload/examples/analyze/labels English; textarea content follows analysis-language tab (content, not chrome) | ✅ |
| EN landing screenshot — layout intact after server→client conversion | ✅ |

Authenticated pages (editor/history/audit) could not be driven in the browser without a running backend, but
they use the same `useT()` store verified above, their keys are covered by the dictionary tests, and the
source-audit script reports 0 hardcoded flags on rendered surfaces.

## 5. i18n source audit

`node scripts/i18n-source-audit.mjs` — heuristic scan (JSX text, aria/placeholder/title, toast/confirm
literals; allow-lists for CSS classes, keys, technical tokens): **0 flags on rendered surfaces**; remaining
flags only in `KNOWN_DEAD` unrendered legacy components (documented in LOCALIZATION_COMPLETION_REPORT.md §4.1).
