# Testing

ReqLint has four test suites plus CI. Counts below were re-verified on `bfe72aa`
(backend: 2026-11-18). **CI does not run any of these suites** — it performs Python syntax
compilation checks (with `|| true`, i.e. non-failing) and frontend lint only
(`.github/workflows/ci.yml`).

## Backend — pytest (`backend/tests/`)

```bash
python -m pytest backend/tests -q          # 119 passed (77 s locally on the reference run)
```

Unit/integration/API tests over the FastAPI app (in-memory SQLite, httpx ASGI transport). Areas:
auth & security config, audits lifecycle, documents, lint, requirements audit, result integrity,
Task-06 evaluators (incl. genuine ML inference and the strict no-fallback error path),
Task-09 provider handling, Task-10 evaluator pipeline provenance. `backend/pytest.ini` defines
markers (`bdd`, `auth`, `audit`, `invest`, `security`, …) for selective runs.

Scope caveat: passing these tests validates application behavior in a controlled in-process
environment — not a full production deployment validation.

## Backend — pytest-bdd suite (`backend/tests/bdd/`)

```bash
python run_bdd.py                           # from repo root; runs pytest tests/bdd in backend/
# or: cd backend && python -m pytest tests/bdd -q
```

**10 feature files / 34 scenarios** (API-level Gherkin in Indonesian, via pytest-bdd): auth (6),
input & audit (4), PDF upload (6 + 1), audit results & scorecard (2), apply & manual revision (3),
history & search (4), export (4), security & data isolation (3), analyze (1). `docs/bdd_testing.md`
documents the original 8-file/32-scenario subset and is slightly stale (see its header note there).

## Frontend — Vitest (`frontend-qa/src/**/*.test.ts`)

```bash
cd frontend-qa
npm test                                    # 74 cases in 8 files
```

Covers the in-browser rule engine (analyze/revise/diff), the backend→UI adapter (evaluator
provenance, FAILED handling), history row semantics, i18n dictionary parity (id/en), export
integrity, and AI-suggestion status labeling.

## Frontend — Cypress (`frontend-qa/tests-e2e/`)

```bash
cd frontend-qa
npm run test:e2e                            # opens Cypress (needs the app on :3000)
```

⚠️ **Stale**: the single spec (`editor-audit.spec.ts`, 3 scenarios) targets `#user-story-input`
and UI strings from a removed legacy editor component. It does not match the current UI and needs
a rewrite before it can gate anything.

## Behave live-web suite (`features/`)

```bash
python -m behave                            # uses behave.ini; needs backend :8000 + frontend :3000
python -m behave -D headless=false          # default opens a real browser (Selenium)
```

**7 feature files / 48 scenarios** (health, auth, PDF upload, lint+audit, audit lifecycle & export,
frontend UI, Sprint-3 features). The harness mixes an in-process backend stub with Selenium-driven
real web pages (`features/bdd_support/`). Not wired into CI; useful as a local full-stack smoke test.

## What is *not* covered

- No CI execution of any test suite (see above).
- No load/performance tests.
- No automated accessibility tests (Task 08's accessibility review was manual).
- The deployed Coolify environment is validated manually (checklists in
  [DEPLOY_COOLIFY.md](../../DEPLOY_COOLIFY.md) / [DEPLOY_COOLIFY_COMPOSE.md](../../DEPLOY_COOLIFY_COMPOSE.md)).
