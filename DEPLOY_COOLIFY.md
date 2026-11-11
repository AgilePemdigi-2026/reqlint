# ReqLint — Coolify Preview Deployment Guide

This guide deploys ReqLint as a **preview/development deployment** on a shared
Coolify server. It uses the branch `deploy/coolify-preview`.

Deployment model: **two separate Coolify applications** (backend + frontend).
No PostgreSQL and no Redis are required for the preview — the backend defaults
to a local SQLite file and `AUDIT_EXECUTION_MODE=inline`.

> Alternative single-domain setup (one Coolify resource, frontend proxies
> `/api/*` to the backend internally): see
> [DEPLOY_COOLIFY_COMPOSE.md](DEPLOY_COOLIFY_COMPOSE.md) which uses
> `docker-compose.coolify.yml`.

### Changes included on the `deploy/coolify-preview` branch

| File | Change | Why |
|---|---|---|
| `.dockerignore` | new | Keeps `node_modules`, `.git`, local `*.db` files, upload caches, and `.env` files out of the Docker build context |
| `backend/Dockerfile` | added healthcheck, non-root user, pre-created `storage/cache` + `data` dirs | Reliable startup & shared-server hygiene; runtime behavior unchanged |
| `frontend-qa/Dockerfile` | `npm run dev` → `npm ci && npm run build && npm start`, added `NEXT_PUBLIC_API_URL` build arg | Dev server is unfit for a hosted preview; the API URL must be baked at build time |
| `backend/app/core/config.py` | `CORS_ORIGINS: List[str]` → `Union[List[str], str]` | With current `pydantic-settings`, a plain comma-separated `CORS_ORIGINS` env value (the format documented in `.env.example`) crashed startup; the existing `mode="before"` validator already handles comma strings, so the fix only removes the crash path. Validated result is still a list. |
| `backend/.env.example` | documented SQLite default, Groq (`openai_compatible`) option, `GROQ_API_KEY` | Template only, no real values |
| `frontend-qa/.env.example` | new | Documents `NEXT_PUBLIC_API_URL` |
| `DEPLOY_COOLIFY.md` | new | This guide |

> ⚠️ Do NOT deploy via the repository-root `docker-compose.yml` on the shared
> server: it binds host ports `5432`/`6379` (conflict risk with other groups)
> and provisions heavier services than the preview needs.

---

## 0. Prerequisites

- Coolify project with two empty applications to be created (one for backend, one for frontend).
- Source: GitHub `AgilePemdigi-2026/reqlint` (canonical; the old `farhanAkbar91/reqlint` URL redirects here), branch `deploy/coolify-preview`.
- A Groq API key if you want real LLM Stage-2 rewrites (optional — the app runs without it using the built-in mock provider).

---

## 1. Backend application (deploy FIRST)

| Coolify setting | Value |
|---|---|
| Build Pack | Dockerfile |
| Dockerfile Location | `backend/Dockerfile` |
| Port | `8000` |
| Health Check Path | `/api/v1/health` |

### Environment variables (Coolify → Environment Variables)

| Variable | Value | Notes |
|---|---|---|
| `JWT_SECRET` | *long random string* (REQUIRED) | e.g. `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CORS_ORIGINS` | `https://<frontend-domain>,http://localhost:3000` | set after the frontend domain exists |
| `SLM_PROVIDER` | `openai_compatible` | optional; omit for mock |
| `SLM_BASE_URL` | `https://api.groq.com/openai` | optional |
| `SLM_MODEL` | `llama-3.1-8b-instant` | any Groq chat model |
| `SLM_TIMEOUT_SECONDS` | `8` | optional; default 4 can be tight for Groq |
| `GROQ_API_KEY` | *your Groq key* | REQUIRED if using Groq |
| `DATABASE_URL` | *(unset)* | defaults to SQLite inside the container |

Optional persistent SQLite: add a Coolify **Persistent Storage** volume mounted at
`/app/backend/data`, and set `DATABASE_URL=sqlite+aiosqlite:///./data/reqlint.db`.
Without it, user accounts and audit history reset on redeploy (acceptable for preview).

### Notes

- The container listens on `0.0.0.0:8000`, runs as non-root user `appuser`, and has
  a Docker `HEALTHCHECK` hitting `/api/v1/health`.
- After the first deploy, Coolify assigns a domain (e.g. `https://<backend-domain>`).
  The API docs are then at `https://<backend-domain>/docs`.

---

## 2. Frontend application (deploy SECOND)

| Coolify setting | Value |
|---|---|
| Build Pack | Dockerfile |
| Dockerfile Location | `frontend-qa/Dockerfile` |
| Port | `3000` |
| Health Check Path | `/` |

### Build-time variable (Coolify → Environment Variables → mark as **Build Variable**)

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<backend-domain>/api/v1` |

`NEXT_PUBLIC_*` variables are inlined into the client bundle **at build time** —
changing it later requires a rebuild (Redeploy with cache disabled or "Rebuild").

### Runtime environment variables

None required.

---

## 3. Deploy order & CORS

1. Deploy **backend** (without `CORS_ORIGINS` yet, or with a placeholder).
2. Note the backend domain → set `NEXT_PUBLIC_API_URL` on the frontend → deploy frontend.
3. Note the frontend domain → update backend `CORS_ORIGINS` to include it → redeploy backend.

---

## 4. Resource expectations (shared-server friendly)

| Aspect | Value |
|---|---|
| Backend image size | ~1.3–1.6 GB (spaCy model baked in) |
| Backend runtime RAM | ~300–500 MB (spaCy + FastAPI, single worker) |
| Frontend build RAM | ~1–1.5 GB peak during `next build` |
| Frontend runtime RAM | ~80–150 MB |
| No DB / Redis containers | SQLite file + inline background tasks |

Build artifacts (Cypress binary) are intentionally skipped in the image build.

---

## 5. Post-deployment verification checklist

1. Backend health: `curl https://<backend-domain>/api/v1/health` → `{"status":"healthy",...}`
2. API docs: open `https://<backend-domain>/docs`
3. Register + login through the frontend UI (creates rows in SQLite)
4. Submit a user story in the editor → Stage-1 lint + audit result appears
   (Stage-2 AI rewrite is mock output unless Groq is configured)
5. PDF upload (≤10 MB) → parsed requirements listed
6. Export audit as PDF/Markdown/JSON
7. Backend logs in Coolify: no repeated tracebacks

---

## 6. Known limitations of this preview

- The INVEST ML model bundle (`pm-docs/rubrics/reqlint_invest_models.pkl`) is not
  loaded in the container (`joblib`/`scikit-learn` are not in the requirements); the
  backend automatically falls back to rule-based heuristics. This matches current
  behavior and is preserved as-is.
- Only the `en_core_web_sm` spaCy model is baked in; Indonesian analysis uses the
  lexicon/regex rules (graceful fallback, unchanged behavior).
- SQLite inside the container is single-writer — fine for a preview, not for
  production multi-instance usage.
- Auth/audit data resets on redeploy unless the optional `/app/backend/data`
  volume is configured.
