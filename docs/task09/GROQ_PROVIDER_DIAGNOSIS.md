# GROQ PROVIDER DIAGNOSIS — Task 09

**Date:** 2026-11-15 · All findings verified against the live Groq API (no key material printed anywhere).

## 1. Root cause of the "LLM/SLM evaluator unusable" failure

The Groq API key **was** correctly configured in `backend/.env` (loaded, length 56, never printed).
The evaluator never reached Groq because `backend/.env` contained **three consecutive assignments of the
same variables** (leftover template blocks that had been uncommented):

```
SLM_PROVIDER=openai_compatible      ← intended Groq block
SLM_BASE_URL=https://api.groq.com/openai
SLM_MODEL=llama-3.1-8b-instant
SLM_PROVIDER=ollama                 ← leftover block 2
SLM_BASE_URL=http://localhost:11434
SLM_MODEL=phi3:mini
SLM_PROVIDER=mock                   ← leftover block 3
SLM_TIMEOUT_SECONDS=4
```

`python-dotenv` / `pydantic-settings` let the **last assignment win**, so the effective runtime config was:

| Variable | Effective (broken) | Effective (after fix) |
|---|---|---|
| `SLM_PROVIDER` | `mock` | `openai_compatible` |
| `SLM_BASE_URL` | `http://localhost:11434` | `https://api.groq.com/openai` |
| `SLM_MODEL` | `phi3:mini` | `openai/gpt-oss-120b` |
| `SLM_TIMEOUT_SECONDS` | `4` | `30` |
| `GROQ_API_KEY` | configured | configured (untouched) |

With `SLM_PROVIDER=mock`, `NLPStage2Service.classify_story_with_llm()` raised
`LLMProviderUnavailableError` immediately (`_require_real_provider` guard) — the Groq call was never attempted.

**Fix applied:** `backend/.env` rewritten to a single Groq block (8 duplicate SLM lines removed, 4 inserted);
`backend/.env.example` rewritten with an explicit warning about the last-wins duplicate-key trap.

## 2. Latent failure #2: the configured model no longer exists

Verified live against `GET https://api.groq.com/openai/v1/models` (HTTP 200, 1.6 s). The current catalog for
this account (11 models) **no longer includes `llama-3.1-8b-instant`** — fixing only the `.env` duplicates
would still have produced a 404 `LLM_MODEL_NOT_FOUND` on the first real audit.

Current chat-capable models observed: `allam-2-7b`, `openai/gpt-oss-120b`, `openai/gpt-oss-20b`,
`openai/gpt-oss-safeguard-20b`, `qwen/qwen3.8-27b` (whisper-*/orpheus-*/prompt-guard-* are audio/safety models).

Candidate probe (real chat completion with the 6-dimension INVEST classification prompt):

| Model | Result | Latency |
|---|---|---|
| `openai/gpt-oss-20b` | HTTP 200, valid JSON, 6 labels | 1.9 s |
| `openai/gpt-oss-120b` | HTTP 200, valid JSON, 6 labels | 2.0 s |
| `qwen/qwen3.8-27b` | HTTP 429 — OTPM limit (reasoning output too large for free tier) | 7.7 s |

**Selected default: `openai/gpt-oss-120b`** — strongest quality at identical latency, JSON-friendly,
bilingual (ID/EN) capable. Documented fallback: `openai/gpt-oss-20b`. Deployment must re-verify against
the live model list (the catalog changes; do not trust tutorial model IDs).

## 3. Request-path verification (all stages)

| Stage | Status | Evidence |
|---|---|---|
| Frontend evaluator selection | ✅ | `evaluator: 'llm'` in POST `/api/v1/audits` payload (`editor/page.tsx`, `evaluator-options.ts`) |
| Backend dispatch | ✅ | `audit_service._execute_pipeline` → `_evaluate_llm` (Task 06 architecture, unchanged) |
| Provider selection | ✅ | `SLM_PROVIDER=openai_compatible` branch in `nlp_stage2._call_provider` |
| Env configuration | ✅ | settings import prints provider/URL/model/timeout; key reported only as `configured` |
| Groq endpoint | ✅ | `https://api.groq.com/openai/v1/chat/completions` (base + `/v1/chat/completions`) |
| Auth | ✅ | `Authorization: Bearer $GROQ_API_KEY` — request made **from the backend only**; key never sent to the browser, never logged, never committed |
| Response parsing | ✅ | `_extract_json` handles fenced/brace JSON; off-contract labels degrade to `INSUFFICIENT_EVIDENCE` with `PROVIDER_LABEL_INVALID` reason |
| Shared generator | ✅ | real generation verified; verdict/score preserved (see TEST_RESULTS.md §E2E) |
| Persistence | ✅ | audit `COMPLETED`, `stage2=DONE`, `model_version=openai_compatible/openai/gpt-oss-120b` |
| Frontend detail | ✅ | evaluator banner, generation status, `ai_suggestion_source=provider` |

## 4. Secrets safety audit

- Key exists only in `backend/.env` (untracked, gitignored); loaded via `pydantic-settings`.
- Not present in frontend code, tests, fixtures, or documentation; the only permitted representation is
  `GROQ_API_KEY: configured / missing`.
- Provider error mapping (`LLMProviderRequestError`) never includes the key, request headers, or raw provider
  payloads; a regression test asserts a fake key never appears in error text (`test_task09_provider.py`).
- Deployment (Coolify) needs: `SLM_PROVIDER=openai_compatible`, `SLM_BASE_URL=https://api.groq.com/openai`,
  `SLM_MODEL=openai/gpt-oss-120b`, `GROQ_API_KEY=…`, `SLM_TIMEOUT_SECONDS>=20`.

## 5. Timeout

`SLM_TIMEOUT_SECONDS` default raised 4 → 20 (config default; `.env` uses 30). The mock provider never opens
a connection, so the PERF-2 mock path is unaffected. Real-provider latency observed: ~1.6–3 s per call.
