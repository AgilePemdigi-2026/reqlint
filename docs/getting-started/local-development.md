# Local development

## Run the backend

From the repository root (a virtualenv with the backend dependencies installed):

```bash
uvicorn app.main:app --app-dir backend --reload --port 8000
```

- Swagger UI: <http://localhost:8000/docs> — OpenAPI is generated from the live FastAPI app.
- On startup the app runs `Base.metadata.create_all` plus an idempotent column patch
  (`backend/app/db/init_db.py`), then loads spaCy and the bilingual lexicons
  (`backend/app/lexicon/`). No ML bundle preload happens — it is loaded lazily on first use.
- **SQLite path is relative to the current working directory.** With the command above the
  database file is `./reqlint.db` at the repository root; when started from `backend/` it is
  `backend/reqlint.db`. Both are gitignored. Set `DATABASE_URL` to control this explicitly.
- The INVEST ML bundle is loaded from `pm-docs/rubrics/reqlint_invest_models.pkl` relative to the
  repository root — run the server from the repo root (or a Docker image, where the path is baked)
  so the Traditional ML evaluator is available.

## Run the frontend

```bash
cd frontend-qa
npm run dev          # http://localhost:3000
```

By default the frontend calls `http://localhost:8000/api/v1` directly (`NEXT_PUBLIC_API_URL`
default in `frontend-qa/src/lib/api.ts`). The landing-page demo and the editor's offline fallback
run a local rule engine **in the browser**, so the landing page works even without the backend.

A demo account is available via **Log in → Gunakan akun demo**; the frontend auto-registers
`demo@reqlint.app` / `demo12345` on the backend if it does not exist. This is a development
convenience — remove it before any real deployment.

## Frontend ↔ backend wiring

| Mode | Mechanism |
|---|---|
| `npm run dev` (default) | Browser calls `NEXT_PUBLIC_API_URL` directly (default `http://localhost:8000/api/v1`). |
| Production build without compose | Set `NEXT_PUBLIC_API_URL` at build time to the absolute backend URL. |
| Docker Compose / Coolify compose | Browser uses same-origin `/api/v1`; Next.js rewrites `/api/*` to `API_PROXY_TARGET` (build-time, `http://backend:8000`). |

The rewrites are resolved **at build time** (baked into the routes manifest), so changing
`API_PROXY_TARGET` requires a rebuild. See [../deployment/docker.md](../deployment/docker.md).

## Project structure

```
backend/
  app/api/v1/         routers (auth, audits, documents, lint, requirements, health)
  app/services/       pipeline services (stage 1, stage 2, evaluators, export, auth, pdf)
  app/core/           config, security, database, errors, responses
  app/db/             ORM models (app/db/models.py), init_db
  app/lexicon/        bilingual term lists for Stage 1
  app/workers/        Celery app + tasks (dormant unless AUDIT_EXECUTION_MODE=celery)
  tests/              pytest suite (119 tests) + pytest-bdd suite (34 scenarios)
frontend-qa/
  src/app/            Next.js App Router pages (+ POST /api/analyze route handler)
  src/lib/            api client, auth, i18n (501 keys), localStorage stores
  src/lib/analyzer/   in-browser rule engine (used by landing demo + offline fallback)
  tests-e2e/          Cypress specs (1 spec, currently stale — see testing.md)
ai-engine/            training corpora + pipelines + experiments (not a runtime service)
pm-docs/              rubrics, annotation datasets, trained model bundle
features/             Behave E2E suite (Selenium, 48 scenarios) for full-stack runs
```

## Common development workflows

| Task | Command |
|---|---|
| Backend tests | `python -m pytest backend/tests -q` |
| pytest-bdd API suite (34 scenarios) | `python run_bdd.py` (shells into `backend/` and runs pytest) |
| Behave live-web suite (48 scenarios, Selenium) | `python -m behave` (uses `behave.ini`; needs frontend+backend running) |
| Frontend unit tests | `cd frontend-qa && npm test` |
| Frontend lint | `cd frontend-qa && npm run lint` |
| Check for untranslated UI strings | `cd frontend-qa && node scripts/i18n-source-audit.mjs` |
| Regenerate sprint burndown chart | `python pm-docs/generate_burndown_chart.py` |

See [../development/testing.md](../development/testing.md) for scope and caveats of each suite.

## Troubleshooting

See [../development/troubleshooting.md](../development/troubleshooting.md) for the common failure
modes (ERESOLVE on `npm ci`, the JWT security guard, missing ML bundle, spaCy model fallback,
compose port conflicts).
