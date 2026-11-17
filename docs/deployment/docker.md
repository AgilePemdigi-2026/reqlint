# Docker deployment

How the Docker images are built and what they contain. Verified against `bfe72aa`
(with the `.dockerignore` fix from PR #25).

## Images

| Image | Dockerfile | Build context | Contents |
|---|---|---|---|
| Backend | `backend/Dockerfile` | **repository root** | Python 3.11-slim; installs `backend/requirements.txt` + `ai-engine/requirements-ai.txt`; downloads spaCy `en_core_web_sm`; copies `backend/`, `ai-engine/`, and the trained ML bundle; runs uvicorn as non-root `appuser` on :8000 |
| Frontend | `frontend-qa/Dockerfile` | **repository root** | Node 18-alpine; `npm ci --legacy-peer-deps` (Cypress binary skipped); `next build` with build args; `npm start` on :3000 |

Both Dockerfiles use the **repository root** as build context; the root `.dockerignore` therefore
applies to both. There are no per-Dockerfile ignore files.

## The Traditional ML bundle and the build context

`backend/Dockerfile` contains:

```dockerfile
COPY pm-docs/rubrics/reqlint_invest_models.pkl /app/pm-docs/rubrics/reqlint_invest_models.pkl
```

`InvestMLService` loads exactly that path inside the container. The file is git-tracked (≈15 KB),
but it lives under `pm-docs/`, which the `.dockerignore` historically excluded wholesale — causing
the Coolify build failure `"/pm-docs/rubrics/reqlint_invest_models.pkl": not found`
(BuildKit computes checksums over the filtered context, so a git-tracked file that is ignored is
still "not found").

**Fix (PR #25):** the broad `pm-docs` exclusion is replaced by a scoped rule set that keeps
datasets, training scripts, and documentation out of the context but re-includes exactly the one
model bundle:

```dockerignore
pm-docs/*
!pm-docs/rubrics
pm-docs/rubrics/*
!pm-docs/rubrics/reqlint_invest_models.pkl
```

(The intermediate re-include of the parent directory is required — a file cannot be re-included
while a parent directory is excluded.) If you ever add another runtime artifact under `pm-docs/`,
add an explicit `!` rule for it.

## Health checks

| Service | Check |
|---|---|
| Backend | Docker `HEALTHCHECK` (Python urllib against `/api/v1/health`; interval 30 s, start-period 90 s — covers spaCy loading) |
| Frontend (compose) | `node -e fetch('http://127.0.0.1:3000/')…` (interval 30 s, start-period 30 s) |

## Compose files

| File | Services | Purpose |
|---|---|---|
| `docker-compose.yml` | `backend`, `frontend`, `db` (postgres:15), `redis` (redis:7) | Full local stack; **publishes host ports 8000, 3000, 5432, 6379** — avoid on shared servers. Backend requires `JWT_SECRET` (compose fails hard without it via `${JWT_SECRET:?}`). |
| `docker-compose.coolify.yml` | `backend`, `frontend` | Single-domain deployment: no DB/Redis (SQLite on the `reqlint_data` volume, inline audit mode), no published ports (Coolify proxy → frontend:3000), frontend proxies `/api/*` to the backend. Build args: `NEXT_PUBLIC_API_URL=/api/v1`, `API_PROXY_TARGET=http://backend:8000`. |

```bash
docker compose up --build                # root compose (dev stack)
docker compose -f docker-compose.coolify.yml up --build   # single-domain variant
```

## Common build/deploy failure scenarios

| Symptom | Cause / fix |
|---|---|
| Backend build: `"/pm-docs/rubrics/…pkl": not found` | `.dockerignore` missing the scoped exception (see above) |
| Backend container exits immediately: `JWT_SECRET is required…` | `ENV != 'dev'` without `JWT_SECRET`; set it in the environment (compose hard-fails earlier via `${JWT_SECRET:?}`) |
| Frontend builds fine but calls the wrong API | `NEXT_PUBLIC_API_URL` / `API_PROXY_TARGET` are **build-time** values — rebuild without cache after changing them |
| Slow first backend build | spaCy model download (~50 MB) is baked into the image; expect a few minutes |
| Data resets on redeploy | SQLite is in-container unless a volume is mounted at `/app/backend/data` |

Image-size expectation for the backend is roughly 1.3–1.6 GB (spaCy + scikit-learn + reportlab +
PyMuPDF). Coolify-specific procedures and checklists: [DEPLOY_COOLIFY.md](../../DEPLOY_COOLIFY.md)
(two applications) and [DEPLOY_COOLIFY_COMPOSE.md](../../DEPLOY_COOLIFY_COMPOSE.md)
(single-domain compose).
