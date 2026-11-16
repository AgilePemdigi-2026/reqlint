# BASELINE AUDIT — Task 09 (Phase 0)

**Date:** 2026-11-15 · **Branch:** `fix/frontend-docker-npm-ci` · **Mode:** read-only audit (no code modified in this phase)

## 1. Working-tree safety review

- `git status`: Task 06/07/08 work is present as **uncommitted modifications + untracked files** (backend services, frontend pages/components, `docs/task06..08/`, several root-level audit reports).
- Nothing will be committed/pushed; no destructive git operations; Task 01–04C research artifacts untouched.
- Files Task 09 will touch (planned): `frontend-qa/src/**` (localization), `backend/app/services/nlp_stage2.py`, `backend/app/services/audit_service.py` (error-code surfacing only), `backend/app/core/config.py` (timeout default), `backend/.env.example`, `backend/.env` (local, untracked), `backend/app/services/export_service.py` + `backend/app/api/v1/audits.py` (optional `lang` param), plus new tests and `docs/task09/`.

## 2. Localization architecture (as found)

- `frontend-qa/src/lib/i18n.ts`: `'use client'` module; `createLocalStore<UILocale>('reqlint.ui_locale', 'id')`; `translations` record (211 keys, exported); `t()` + `useT()` with `{placeholder}` interpolation and fallback `id → raw key`. Store is SSR-safe (`useSyncExternalStore`, server snapshot = default).
- `LanguageToggle` in app shell flips ID/EN; persistence via localStorage; navigation does not reset locale.
- Existing tests: `lib/i18n.test.ts` (dictionary parity, evaluator labels), `lib/export.test.ts` (export integrity; relies on default `locale ?? 'id'`), `lib/adapter.test.ts`, `lib/history.test.ts`, `lib/ai-status.test.ts`.

### 2.1 Pages/components with incomplete localization (rendered-text audit)

| Surface | Status | Evidence |
|---|---|---|
| Landing `/` (page.tsx) | ❌ 100% hardcoded ID (server component) | banner copy |
| `landing/hero.tsx` | ❌ hardcoded ID (server component) | badge, h1, body, CTA, privacy note |
| `landing/sections.tsx` | ❌ hardcoded ID (server component) | Features(6×2), Steps(3), ISO criteria(5×2), INVEST(6), Privacy, FAQ(6), FinalCta |
| `landing/footer.tsx` | ❌ hardcoded ID | nav labels, tagline |
| `landing/landing-nav.tsx` | ❌ hardcoded ID | links, CTAs |
| `landing/demo-card.tsx` | ⚠️ client component, hardcoded ID | toasts, labels, placeholders, aria |
| `login/page.tsx` | ❌ does **not** call `useT()` although `login.*` keys exist | all strings hardcoded |
| `register/page.tsx` | ❌ same | `register.*` keys exist but unused |
| `forgot-password/page.tsx` | ✅ localized | uses `forgot.*` |
| `reset-password/page.tsx` | ⚠️ mostly localized | 2 inline validation messages |
| `(app)/editor/page.tsx` | ⚠️ partial | crumb/title/subtitle, hints, upload strings, tips card, aria labels hardcoded; evaluator selector + toasts localized |
| `(app)/history/page.tsx` | ⚠️ partial (worst offender) | `history.*` keys exist in dictionary but the page hardcodes filters, empty states, toasts, row statuses, confirm dialogs |
| `(app)/audit/[id]/page.tsx` | ⚠️ partial | polling stages, loading card, PageHeader, toasts, privacy note hardcoded; advisory strings hardcoded although `audit.flagged` / `audit.passed_llm` / `audit.unknown_val` keys exist |
| `(app)/help/page.tsx` | ✅ localized | — |
| `(app)/contact/page.tsx` | ✅ localized | — |
| `app-shell.tsx` | ⚠️ partial | `nav.help`/`nav.contact` keys missing (string-`startsWith` hack instead); `'Navigasi utama'`, `'Notifikasi'` aria, `'Arsitektur Terintegrasi'` |
| `audit/revision-cards.tsx` | ❌ hardcoded | headings, empty texts, buttons, aria |
| `audit/diff-viewer.tsx` | ❌ hardcoded | pane titles, badges, legend, note |
| `audit/score-card.tsx` | ❌ hardcoded | tooltip, aria |
| `audit/summary-card.tsx` | ⚠️ partial | aria `'Tidak ada temuan'`, `'Lihat detail INVEST'`, `'Belum dievaluasi'/'Lulus'/'Belum lulus'` |
| `audit/findings-table.tsx` | ⚠️ partial | `'Kalimat {n}'` hardcoded |
| `auth/auth-shell.tsx` | ❌ `'Kembali ke workspace'` | server component |
| `auth/fields.tsx` | ❌ show/hide password aria | client component |
| `language-toggle.tsx` | ⚠️ asymmetric aria (`Switch to English` EN / `Ganti ke Bahasa Indonesia` ID — acceptable pattern) | keep |
| `backend-badge.tsx` | ❌ titles + `'FastAPI: Online'` etc. | client component |
| `code-editor.tsx` | ⚠️ default ariaLabel + placeholder | client component |
| `lib/format.ts` | ❌ `CATEGORY_LABEL`/`GRADE_TAGLINE` ID-only; `formatDate` fixed `id-ID` | — |
| `lib/ai-status.ts` | ❌ ID-only explanations | — |
| `lib/validation.ts` | ❌ zod messages ID-only | — |
| `lib/analyzer/adapter.ts` | ⚠️ 2 ID-only INVEST notes | — |
| `lib/export.ts` | ✅ bilingual `LABELS` but `toCsv` headers ID-only; audit page passes **story language** as `meta.locale` | Task 09 requires UI locale |
| `components/analysis/AuditScorecard.tsx`, `SmellList.tsx`, `audit/backend-audit-card.tsx` | ℹ️ hardcoded ID but **not imported by any page** (legacy dead code; `auditRequirement` API likewise unused) | out of scope; documented, untouched |

Hydration: store pattern is safe; landing components will be converted to client components using the same store (no new mismatch class). `<html lang="id">` is static — Task 09 adds a small sync effect (`document.documentElement.lang = locale`).

## 3. Export localization (3.4)

- Frontend local generator already bilingual (`LABELS` in `lib/export.ts`); audit page passes `locale: currentLang` (story language) → **must become UI locale**. `toCsv` headers need locale awareness.
- Backend `ExportService.render_markdown/render_pdf` labels are hardcoded Indonesian; `/audits/{id}/export` accepts no language param. Plan: optional `lang` query param (`id|en`, default `id` — backward compatible with BDD 05), pass UI locale from frontend.
- User-authored text and backend analysis content stay untranslated (only labels/headings/verdict descriptions are localized).

## 4. Groq/LLM provider path (as found)

```
editor selector (rule_based|traditional_ml|llm)
→ POST /api/v1/audits {evaluator}
→ audit_service.run_pipeline → _evaluate_llm
→ NLPStage2Service.classify_story_with_llm  (raises LLMProviderUnavailableError if provider==mock)
→ _call_provider (httpx; ollama | openai_compatible)
→ 6 INVEST dimensions {label: PASS|FAIL|INSUFFICIENT_EVIDENCE, reason}
→ evaluation_contract.build_evaluation_result (verdict, framework_score, model_version=provider/model)
→ generate_response (shared generator; verdict/score-preserving; failure → PARTIAL)
→ audit detail → frontend evaluator banner / generation status / advisory
```

### 4.1 Diagnosis — configuration (root cause confirmed)

`backend/.env` contains **three consecutive assignments of the same variables**:

```
SLM_PROVIDER=openai_compatible      ← intended Groq block
SLM_BASE_URL=https://api.groq.com/openai
SLM_MODEL=llama-3.1-8b-instant
SLM_PROVIDER=ollama                 ← leftover template block (uncommented)
SLM_BASE_URL=http://localhost:11434
SLM_MODEL=phi3:mini
SLM_PROVIDER=mock                   ← final value WINS in python-dotenv/pydantic-settings
SLM_TIMEOUT_SECONDS=4
```

Verified by importing `app.core.config.settings` in the backend venv:

```
SLM_PROVIDER   = mock
SLM_BASE_URL   = http://localhost:11434
SLM_MODEL      = phi3:mini
SLM_TIMEOUT    = 4
GROQ_API_KEY   = configured (len=56)   ← value never printed
```

**Root cause:** duplicate keys — the last `SLM_PROVIDER=mock` wins, so `classify_story_with_llm()` raises `LLMProviderUnavailableError` immediately; the Groq call is never attempted. The key itself **is** correctly present and loadable from the backend env.

Secondary defects found in the same path:

1. `SLM_TIMEOUT_SECONDS=4` — too tight for real LLM calls (Groq llama-3.1-8b-instant typically needs 1–10 s under load; generation prompt is larger). Mock path never uses the HTTP client, so raising the default is safe.
2. `_call_provider` (openai_compatible) sends the request **without error when `GROQ_API_KEY` is empty** → provider 401 with an opaque message instead of a clear "key missing" error.
3. Provider HTTP failures surface as raw exception text (`str(e)`), no machine-readable error codes (timeout vs 401 vs 429 vs model-not-found) → frontend cannot localize.
4. `audit_service._execute_pipeline` records a single code `LLM_EVALUATOR_UNAVAILABLE` for every LLM failure.

### 4.2 Provider/endpoint correctness

- Endpoint construction: `SLM_BASE_URL=https://api.groq.com/openai` + `/v1/chat/completions` → `https://api.groq.com/openai/v1/chat/completions` ✅ (matches Groq OpenAI-compatible API).
- Auth: `Authorization: Bearer $GROQ_API_KEY` ✅. Request is sent **from the backend** (browser never sees the key) ✅.
- Model `llama-3.1-8b-instant`: to be verified live against `GET https://api.groq.com/openai/v1/models` in Phase 2 (do not trust stale tutorials; results in `GROQ_PROVIDER_DIAGNOSIS.md`).
- JSON robustness: `_extract_json` already handles ```json fences + brace slicing; off-contract labels degrade to `INSUFFICIENT_EVIDENCE` with `PROVIDER_LABEL_INVALID` ✅.
- Secrets: `.gitignore` covers `.env`; key never in frontend/tests/docs; only `configured/missing` reported.

## 5. Environment & deployment notes

- `.env.example` documents the Groq/ollama/mock options but as **multiple uncommented blocks** — the exact trap that produced the duplicate-key failure. Task 09 rewrites it as one commented template with exactly one active block.
- Coolify: same env vars; diagnosis report will include the required variable list.
- Docker/Coolify must receive `SLM_PROVIDER=openai_compatible`, `SLM_BASE_URL=https://api.groq.com/openai`, `SLM_MODEL=<verified>`, `GROQ_API_KEY=…`, `SLM_TIMEOUT_SECONDS>=20`.

## 6. Test baselines (pre-change)

- Backend: `python -m pytest backend/tests -q` → 91 passed (Task 08 report; re-run in Phase 7).
- Frontend: `npx vitest run` → 51 passed; `tsc --noEmit` clean; `next build` OK.
- BDD: `python run_bdd.py` → 32 passed.

## 7. Implementation plan

1. **Backend provider fix (Phases 2–3):** repair `backend/.env` (single Groq block, timeout 20); verify Groq model list live; add typed provider errors (`LLM_PROVIDER_KEY_MISSING/TIMEOUT/AUTH_FAILED/RATE_LIMITED/MODEL_NOT_FOUND/SERVER_ERROR/INVALID_RESPONSE`) surfaced via `evaluator_error_code`; fail-fast on missing key; keep mocked tests deterministic (monkeypatched provider), add new mocked-error tests + real-Groq smoke script (Phase 4) executed once and recorded.
2. **Frontend localization (Phase 1):** extend the dictionary (~120 new keys, namespaced `landing.*`, `editor.*`, `history.*`, `auth.*`, `common.*`, `llmError.*`…); convert landing to client components; localize every surface in §2.1; localize lib helpers (`format`, `ai-status`, `validation`, `adapter`) with locale-aware helpers; pass UI locale to exports (frontend + backend `lang` param); `<html lang>` sync; no new i18n library.
3. **Frontend LLM experience (Phase 5):** map `evaluator_error_code` → localized, actionable message; keep evaluator identity; generation status separate.
4. **Regression (Phase 7):** all baselines + new i18n/provider tests; source-audit script `scripts/i18n-source-audit.mjs`.

Preserved: all three evaluators, existing scoring/verdict mechanisms, mocked tests, research artifacts.
