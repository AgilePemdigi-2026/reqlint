# TASK 10 — Critical Evaluator Pipeline & Revision Generator Repair

**Date:** 2026-11-16 · **Branch:** `fix/frontend-docker-npm-ci` (uncommitted, per task constraints)

## Outcome

Every evaluator selection now provably executes the selected evaluator, displays results with explicit
provenance (`requested_evaluator` / `actual_evaluator`), shows a real processing lifecycle (no more instant
Rule-Based look-alikes), renders the previously-invisible ML/LLM INVEST dimension results, and the shared
revision generator — which failed on nearly every real audit — now succeeds end-to-end. Failures are explicit,
localized, and retryable with **no Rule-Based substitution anywhere**.

## Root causes found (verified by reproduction, not assumption)

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| RC-1 | A: "Rule-Based works" / B/C: browser says backend unreachable | **CORS mismatch**: `backend/.env` allowed only `http://localhost:3000` while the frontend runs on `:3100` → **every** browser→backend call failed; the editor silently used its local browser Rule-Based engine | added `http://localhost:3100` to `CORS_ORIGINS`; also documented that the frontend port must be allow-listed |
| RC-2 | D: "Generator: failed — evaluation results remain available" on nearly every audit | **Generator schema fragility**: the model frequently annotates `invest_observations` with extra keys (`"notes": "…"` — captured live from Groq) and the strict `Dict[str, bool]` pydantic schema rejected the whole response → `LLM_INVALID_RESPONSE` after retry → PARTIAL. Second layer: `acceptance_criteria` is a required field with strict per-item fields — a single omitted/malformed item failed everything | `_sanitize_invest_observations()` (six known keys kept, lenient booleans coerced, annotations dropped — advisory data only) + `_coerce_generation_payload()` (rewrite default, malformed criteria items dropped) + prompt tightened ("ONLY the six boolean keys") + `_extract_json` fence-fallthrough |
| RC-3 | B/C: "ML results absent, INVEST dimensions not displayed, scorecard origin unclear" | **Frontend never rendered `evaluation.dimensions`** — ML/LLM audits showed an empty findings table (honest) with no dimension evidence anywhere | new `DimensionResults` panel: six verdicts (PASS/FAIL/IE badges, confidence %, rationale) attributed "Dinilai oleh evaluator {X}" |
| RC-4 | B/C: "immediately displays Rule-Based results; no meaningful loading screen" | **Audit page skipped the loading state whenever a local browser audit existed** (always true for editor submissions) → instant local Rule-Based analysis while the backend ran; fetch errors also silently fell back to the local RB result | full lifecycle rewrite: backend audits always show loading/processing → terminal; local RB analysis rendered **only** for `AUD-*` offline audits; backend fetch failure shows an explicit error panel (no substitution) |
| RC-5 | misleading scorecard on ML/LLM audits | adapter substituted the evaluator **score** for the ISO "document practice" meter when the breakdown was absent; FAILED audits rendered a normal score-0 card | adapter reports `null` (honest "–"); FAILED audits render an explicit failure panel with localized error code + retry — no score card |
| RC-6 | stale results / stuck UI after "Analisis Ulang" | rerun fetched detail once with no polling; processing audits rendered stale scores | rerun re-enters the load/poll lifecycle; polling stops on terminal state |
| RC-7 | `/audit/[id]` SSR 500 during testing | the `.next` production build had been clobbered by a later dev-mode run (dev manifests deleted the build) — environmental, not source | rebuilt and restarted cleanly |

## Documents

- [REPRODUCTION_AND_TRACES.md](./REPRODUCTION_AND_TRACES.md) — Phase 0 evidence: DB records of the user's failing audits, raw Groq output capture, API traces (pre/post-fix), UI observations
- [TEST_RESULTS.md](./TEST_RESULTS.md) — all suites + new regression tests + browser E2E evidence
