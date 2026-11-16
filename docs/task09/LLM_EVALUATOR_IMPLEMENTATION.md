# LLM EVALUATOR IMPLEMENTATION — Task 09

Scope: make the existing Task 06 Evaluator C operational with a real provider (Groq) **without** changing the
three-evaluator architecture, the evaluation contract, or any research artifact.

## 1. What changed (backend)

### 1.1 `backend/app/services/nlp_stage2.py`

- **`LLMProviderRequestError(LLMProviderUnavailableError)`** — typed provider failure carrying a stable
  machine-readable `code` (+ optional `http_status`). Codes:
  - `LLM_PROVIDER_KEY_MISSING` — `SLM_PROVIDER=openai_compatible` with empty `GROQ_API_KEY` (fails fast **before
    any network call**; regression test proves the HTTP client is never constructed).
  - `LLM_PROVIDER_AUTH_FAILED` (401/403), `LLM_MODEL_NOT_FOUND` (404), `LLM_RATE_LIMITED` (429),
    `LLM_PROVIDER_SERVER_ERROR` (5xx), `LLM_PROVIDER_REQUEST_REJECTED` (other 4xx),
    `LLM_PROVIDER_TIMEOUT`, `LLM_PROVIDER_UNREACHABLE`, `LLM_INVALID_RESPONSE`.
  - `RETRYABLE = {TIMEOUT, RATE_LIMITED, SERVER_ERROR, INVALID_RESPONSE}` — deterministic failures (missing key,
    bad credentials, unknown model) are **not** retried; transient ones retry once (preserving the historical
    retry-on-invalid-JSON behavior).
- **`_raise_provider_error()`** maps `httpx` transport/HTTP exceptions to the codes above. Messages are
  secret-free and truncated: no API key, no headers, no verbatim provider bodies, no stack traces.
- **`generate_response()` fix (found by the real-Groq E2E):** returns `acceptance_criteria` as plain dicts
  (`[ac.model_dump() for ac in validated.acceptance_criteria]`). Previously it returned pydantic models, which
  SQLAlchemy cannot serialize into the audit JSON column → **every real-provider audit would have hung in
  PROCESSING at the generation commit**. The mock path already returned dicts, so mocked tests never caught it.
- Classification + generation behavior otherwise unchanged: six-dimension labels `PASS | FAIL |
  INSUFFICIENT_EVIDENCE`, grounding prompt with `<user_story>` data-delimiter injection guard, mock-provider
  guard intact, no silent fallback to another evaluator.

### 1.2 `backend/app/services/audit_service.py`

- The evaluator-failure branch now surfaces `getattr(e, "code", None)` — a plain `LLMProviderUnavailableError`
  still yields the legacy `LLM_EVALUATOR_UNAVAILABLE`; typed errors yield their specific code via
  `detail["evaluator_error_code"]` and `breakdown["evaluator_error"]["code"]`. Frontend fallback for unknown
  codes: raw backend message (message text only — never secrets).

### 1.3 `backend/app/core/config.py` / `.env.example`

- `SLM_TIMEOUT_SECONDS` default 4 → 20 (mock path unaffected; see GROQ_PROVIDER_DIAGNOSIS.md §5).
- `.env.example` SLM section rewritten: exactly one active block, live-catalog verification instruction,
  explicit duplicate-key warning.

### 1.4 Test-suite isolation (`backend/tests/conftest.py`)

- The suite pins `os.environ["SLM_PROVIDER"] = "mock"` **before** app import. Every mocked test was written
  against the mock provider (e.g. `ai_suggestion_source == "mock"` assertions) and must stay deterministic and
  offline now that the developer `.env` points at real Groq. This preserves — not weakens — the original test
  assumptions. Live-provider verification is a standalone script, never a pytest test.

## 2. Real-provider E2E verification (`backend/scripts/task09_groq_e2e.py`)

Standalone script (isolated temp SQLite; the dev DB is never touched), executed 2026-11-15 with the real
`backend/.env` Groq configuration. All steps PASS:

1. Backend recognizes Groq config — provider `openai_compatible`, model `openai/gpt-oss-120b`, timeout 30 s,
   `GROQ_API_KEY: configured` (value never printed).
2. Connectivity `GET /models` — HTTP 200 in 1.6 s, configured model listed.
3. Real 6-dimension classification — all six labels returned, 2.5 s.
4. Evaluation-contract validation — `verdict=PASS`, `score=100.0`, `model_version=openai_compatible/openai/gpt-oss-120b`.
5. Shared response generation — 3 acceptance criteria in 2.9 s; `verdict_preserved=PASS`, `score_preserved=100.0`.
6. Full pipeline through the API — audit `COMPLETED`, `stage2=DONE`, `generation=DONE/openai_compatible`, 10.9 s.
7. Frontend-facing fields — `ai_suggestion_source=provider`, `ai_invest_notes` present.
8. Reanalysis — evaluator identity `llm` persists end-to-end.

## 3. Frontend LLM experience (Phase 5)

- All three evaluators remain independently selectable (`evaluator-options.ts`, unchanged contract).
- The audit detail page maps `evaluator_error_code` → localized, actionable messages via the
  `llm_error.*` dictionary entries (12 codes × ID/EN); unknown codes fall back to the backend message.
  Provider/model provenance shown (`Evaluator / Model / Generator` banner), generation status reported
  separately from evaluation status (`PARTIAL` keeps the evaluation + score visible).
- No silent evaluator switching anywhere (browser fallback still restricted to Rule-Based).

## 4. Error-handling matrix (user-visible behavior)

| Condition | Code surfaced | Frontend behavior |
|---|---|---|
| No provider configured (mock) | `LLM_EVALUATOR_UNAVAILABLE` | localized message, audit FAILED, no fallback |
| Key missing on server | `LLM_PROVIDER_KEY_MISSING` | localized actionable message; fails before network |
| Invalid/revoked key | `LLM_PROVIDER_AUTH_FAILED` | localized "check GROQ_API_KEY"; no retry storm |
| Model not on account | `LLM_MODEL_NOT_FOUND` | localized "check SLM_MODEL against live catalog" |
| Rate limit | `LLM_RATE_LIMITED` | localized "wait, then Reanalyze"; one retry |
| Timeout | `LLM_PROVIDER_TIMEOUT` | localized; one retry |
| Provider 5xx | `LLM_PROVIDER_SERVER_ERROR` | localized; one retry |
| Non-JSON / schema-invalid output | `LLM_INVALID_RESPONSE` | localized; one retry |
| Generation failure after evaluation | generation status `FAILED`, audit `PARTIAL` | evaluation + score preserved; Reanalyze offered |

Secrets are never exposed in any of these paths (regression-tested).
