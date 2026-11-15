# TEST RESULTS — Task 10

**Date:** 2026-11-16 · Real-provider verification separate from mocked suites, per Task 09/10 rules.

## 1. Regression suites

| Suite | Command | Before Task 10 | After Task 10 |
|---|---|---|---|
| Backend pytest | `python -m pytest tests -q` (backend/) | 109 passed | **119 passed** ✅ (+10 new) |
| BDD | `python ../run_bdd.py` (backend/) | 32 passed | **32 passed** ✅ |
| Frontend Vitest | `npx vitest run` (frontend-qa/) | 62 passed | **66 passed** ✅ (+4 new) |
| TypeScript | `npx tsc --noEmit` | clean | **clean** ✅ |
| Production build | `npx next build` | success | **success (13 routes)** ✅ |
| Real Groq pipeline | UI E2E + direct generate_response runs | — | **5/5 direct + all 3 UI audits COMPLETED/DONE** ✅ |

## 2. New regression tests

**Backend — `tests/test_task10_evaluator_pipeline.py` (10 tests, mocked/offline):**
- Generation tolerates annotated `invest_observations` (`"notes"` key) — the exact reproduced failure.
- Generation tolerates lenient booleans (`"true"/"false"/1/0`); fully-uncoercible advisory objects are dropped
  without failing generation.
- Generation prompt carries ML dimension evidence (labels, confidence %, rationales) and the strict
  six-boolean-keys instruction.
- `_extract_json` handles fenced JSON with surrounding prose and raw JSON with prose.
- Detail response exposes `requested_evaluator` / `actual_evaluator`; FAILED LLM audit → `actual_evaluator`
  null + placeholder score never presented as success; PARTIAL audit keeps ML provenance (never RB-substituted).

**Frontend — `src/lib/analyzer/adapter-task10.test.ts` (4 tests):**
- Provenance passthrough (requested/actual/evaluation contract).
- ML audits: `compliance.iso29148` is `null` (never the ML score masquerading as an ISO percentage).
- Six INVEST checks remain honestly unevaluated when the numeric breakdown is absent (authoritative display
  comes from `evaluation.dimensions`).
- Failed LLM audit propagates `actual_evaluator: null` + error code (no fabricated provenance).

## 3. End-to-end acceptance (real frontend + backend, same User Story)

| Check | Rule-Based (31) | Traditional ML (32) | LLM/SLM (33) | Failure test (34) |
|---|---|---|---|---|
| Correct dispatch (requested==actual in DB + UI banner) | ✅ | ✅ | ✅ | ✅ (requested=llm, failure explicit) |
| Real inference / provider call | ✅ (rule engine) | ✅ (2.1.0-srs-hybrid, 6 dims) | ✅ (Groq gpt-oss-120b) | deliberate 404 model |
| Six INVEST dimensions displayed | ✅ (V/T assessed; others IE) | ✅ (4 PASS/2 FAIL + confidence %) | ✅ | n/a (failure panel) |
| Score provenance shown | ✅ | ✅ | ✅ | no score card at all |
| Findings/evidence | ✅ (3 span findings) | ✅ (dimension rationale text) | ✅ (rationale text) | — |
| Processing lifecycle (loading card, requested evaluator, poll, stop) | ✅ | ✅ | ✅ | ✅ (retry re-polls) |
| Generator status | ✅ DONE (openai_compatible) | ✅ DONE | ✅ DONE | — |
| Contextual revision + acceptance criteria | ✅ | ✅ (screenshot: grounded rewrite + Given/When/Then + diff) | ✅ | — |
| Silent fallback | none | none | none | none — explicit failure panel, localized `LLM_MODEL_NOT_FOUND`, "tidak ada fallback" |
| Retry recovery | — | — | — | ✅ same audit → COMPLETED, evaluator identity preserved |

## 4. Browser evidence (screenshots captured during the E2E)

1. Pre-fix ML audit 27 — provenance banner but zero dimension display, ISO meter = ML score (the reported symptom).
2. Pre-fix submit flow — instant local scorecard at t≈400 ms (no loading state).
3. Post-fix Rule-Based audit 30/31 — provenance banner + generator failure detail (30) then DONE (31).
4. Post-fix ML audit 32 — "Evaluator diminta/aktual: Traditional ML", "Skor dihasilkan oleh evaluator
   Traditional ML.", honest "–" meters, Hasil Dimensi INVEST panel; contextual revision + AC + diff screenshot.
5. Post-fix LLM audit 33 — full provenance incl. `openai_compatible/openai/gpt-oss-120b`, score 100,
   dimension panel with LLM attribution.
6. Deliberate failure audit 34 — "Evaluasi Gagal" panel, localized model-not-found message, no score card.

## 5. Provider-failure behavior (deliberate)

- Bogus model → audit FAILED with `LLM_MODEL_NOT_FOUND`; UI shows the failure panel (no score, no findings,
  no fallback), retry available; after fixing the config the SAME audit reanalyzed to COMPLETED.
- The mocked suite additionally pins: missing key → `LLM_PROVIDER_KEY_MISSING` fail-fast; 401 → auth failure
  without retry; 429/timeout/5xx → one retry then explicit failure (Task 09 suite, still green).

## 6. Notes

- The mocked backend suite pins `SLM_PROVIDER=mock` (Task 09 conftest) — offline determinism preserved.
- Dev-environment fixes applied during diagnosis: `CORS_ORIGINS` += `http://localhost:3100`; backend restarted
  (an orphaned reload child was also serving stale code on :8000); `.next` rebuilt after a dev run clobbered it.
