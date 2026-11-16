# RELEASE READINESS — Task 09

## Definition of Done assessment

| Requirement (task doc §12) | Status |
|---|---|
| Entire user-facing application supports Indonesian and English | ✅ All rendered routes, components, toasts, filters, aria-labels, validation, exports (route table in LOCALIZATION_COMPLETION_REPORT.md) |
| No major route or component unintentionally hardcoded to one language | ✅ Source-audit script: 0 flags on rendered surfaces; 4 known unrendered legacy components documented |
| Groq can perform a real LLM evaluation through the ReqLint interface | ✅ Verified live end-to-end (mocked tests alone were NOT used as evidence) |
| Shared response generation works with the real provider | ✅ Verdict/score preserved, 3 acceptance criteria generated live |
| Provider failures are explicit and safe | ✅ 12 typed error codes, localized ID/EN, no secret leakage (regression-tested) |
| All three evaluators remain independently selectable | ✅ rule_based / traditional_ml / llm untouched; reanalysis persistence regression-tested |
| Existing evaluation integrity preserved | ✅ contract, scoring, verdict-preservation, P0 rules intact; 109 backend + 32 BDD green |

## Verification levels (required distinction)

| Level | Items |
|---|---|
| **Verified against real Groq API** | config recognition, connectivity, 6-dimension classification, evaluation contract, shared generation, full API pipeline, provenance fields, reanalysis identity |
| **Verified with mocks (deterministic regression)** | typed provider error mapping ×7, missing-key fail-fast, secret non-leakage, pipeline error surfacing, PARTIAL preservation, AC serialization shape, export lang param, all 51 pre-existing frontend tests, all pre-existing backend/BDD tests |
| **Verified rendered in browser** | landing/login/demo-card in ID + EN, locale round-trip, `<html lang>` sync, layout screenshot |
| **Blocked by infrastructure** | live Ollama run (no daemon in this environment — setup documented); Coolify deployment (lecturer-provided environment; required env vars documented) |

## Deployment checklist (Coolify / any environment)

1. Set **exactly once** in the environment: `SLM_PROVIDER=openai_compatible`,
   `SLM_BASE_URL=https://api.groq.com/openai`, `SLM_MODEL=openai/gpt-oss-120b`,
   `GROQ_API_KEY=<secret>`, `SLM_TIMEOUT_SECONDS>=20`.
2. Re-verify the model ID against `GET https://api.groq.com/openai/v1/models` before go-live (catalog drift
   already bit once: `llama-3.1-8b-instant` was removed).
3. `GROQ_API_KEY` must exist only as an environment variable — never in the image, repo, or frontend.
4. No other env changes required; `ENV != dev` still requires an explicit `JWT_SECRET` (P0/SEC-01 unchanged).

## Known limitations & follow-ups (non-blocking)

1. Legacy unrendered components still contain ID strings (dead code, preserved by rule; candidates for deletion in a future cleanup task).
2. `qwen/qwen3.8-27b` hits free-tier OTPM limits with reasoning output — do not select as default.
3. Root-layout metadata (`<title>`) remains Indonesian by design (build-time static).
4. Ollama compatibility is code-reviewed, not live-run (see OLLAMA_COMPATIBILITY.md).

## Risk assessment

Low. Localization changes are UI-chrome only (analysis content untouched); backend changes are additive typed
errors + a serialization fix + config defaults; all pre-existing suites pass unchanged in count and assertion
strength. Rollback = revert the working-tree changes (nothing committed).
