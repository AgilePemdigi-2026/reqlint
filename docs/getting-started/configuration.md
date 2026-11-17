# Configuration

All backend variables are read by `backend/app/core/config.py` (pydantic-settings, `case_sensitive`,
`.env` file supported — copy `backend/.env.example` to `backend/.env`). Field name = environment
variable name. Defaults below are the code defaults.

## Core

| Variable | Default | Description |
|---|---|---|
| `ENV` | `dev` | Runtime environment. Anything other than `dev` activates the security guard (below). |
| `DATABASE_URL` | `sqlite+aiosqlite:///./reqlint.db` | SQLAlchemy async URL. Path is relative to the **current working directory**. PostgreSQL example: `postgresql+asyncpg://user:pass@host:5432/reqlint_db` (asyncpg driver required). |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker/backend and the health-check ping target in `celery` mode. |
| `AUDIT_EXECUTION_MODE` | `inline` | `inline` = FastAPI BackgroundTasks (no extra services). `celery` = dispatch to a Celery worker; **the compose files do not start a worker or Redis**, so `inline` is the supported deployment mode. |
| `CORS_ORIGINS` | `["http://localhost:3000", "http://127.0.0.1:3000"]` | Accepts a JSON list or a comma-separated string (validator splits commas). |

## Security

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET` | *(empty)* | HS256 signing secret. Required when `ENV != 'dev'` — see the guard below. |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm. |
| `JWT_EXPIRE_HOURS` | `24` | Access-token lifetime. |
| `BCRYPT_ROUNDS` | `12` | Password hashing cost. |

### Security guard

Implemented at import time in `backend/app/core/config.py` (`validate_security_settings`):

| Condition | Behavior |
|---|---|
| `ENV != 'dev'` and `JWT_SECRET` is empty | `RuntimeError` — the process refuses to start. |
| `ENV != 'dev'` and `JWT_SECRET` equals the published example placeholder (`ganti-ini-dengan-secret-acak-panjang`) | `RuntimeError` — the process refuses to start. |
| `ENV == 'dev'` and `JWT_SECRET` is empty | An ephemeral random secret is generated for the process (logged with a warning). |

Covered by `backend/tests/test_security_config.py`.

## Text and upload limits

| Variable | Default | Description |
|---|---|---|
| `MAX_UPLOAD_MB` | `10` | Rejected with `413 FILE_TOO_LARGE` above this size (`POST /documents/upload`). |
| `MAX_TEXT_CHARS` | `50000` | Drafts/extracted text are truncated or rejected beyond this (`DRAFT_TOO_LONG`, `truncated: true` for PDFs). |
| `TEMP_DIR` | `./storage/cache` | Temporary upload cache (relative to the working directory). |
| `TEMP_TTL_MINUTES` | `60` | Age after which the Celery beat task `cleanup_temp_files` deletes cache files. Nothing runs this task unless you start a Celery beat process yourself. |

## Stage-2 LLM / SLM provider

| Variable | Default | Description |
|---|---|---|
| `SLM_PROVIDER` | `mock` | `mock` \| `ollama` \| `openai_compatible`. |
| `SLM_BASE_URL` | `http://localhost:11434` | Provider base URL (`http://api.groq.com/openai` for Groq). |
| `SLM_MODEL` | `phi3:mini` | Provider chat model (e.g. `llama-3.1-8b-instant` on Groq). |
| `SLM_TIMEOUT_SECONDS` | `20` | Per-request timeout. |
| `GROQ_API_KEY` | *(empty)* | Required for `openai_compatible`; requests fail fast with `LLM_PROVIDER_KEY_MISSING` without it. |

Provider behavior (verified in `backend/app/services/nlp_stage2.py`):

- `mock` — deterministic built-in demo templates; output is explicitly labeled as **not real AI**
  in API responses (`ai_suggestion_source: "mock"`) and in the UI. The LLM evaluator refuses to run
  on this provider.
- `ollama` — HTTP `POST {SLM_BASE_URL}/api/generate`.
- `openai_compatible` — HTTP `POST {SLM_BASE_URL}/v1/chat/completions` with a Bearer token from
  `GROQ_API_KEY`. Used for the Task 09–verified Groq integration.

Failure handling and error codes: [../features/llm-evaluation.md](../features/llm-evaluation.md).

## Email (password reset)

| Variable | Default | Description |
|---|---|---|
| `SMTP_HOST` | *(empty)* | When empty, reset tokens are created but **not delivered** (endpoint still returns 200 — anti-enumeration). |
| `SMTP_PORT` | `587` | SMTP port. |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | *(empty)* | SMTP credentials. |
| `SMTP_FROM` | `reqlint@localhost` | Sender address. |
| `SMTP_USE_TLS` | `true` | STARTTLS toggle. |
| `PUBLIC_BASE_URL` | `http://localhost:3000` | Used when building links inside emails. |

## Frontend

| Variable | Where | Default | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | build/runtime env | `http://localhost:8000/api/v1` | Browser-side API base (`frontend-qa/src/lib/api.ts`). Set to `/api/v1` for same-origin compose deployments. |
| `API_PROXY_TARGET` | **build arg** | `http://backend:8000` | Target of the `/api/*` server-side rewrites in `next.config.js`. Baked at build time. |

## Endpoint/misc

`PROJECT_NAME` (`ReqLint API`), `VERSION` (`1.0.0`, shown by `GET /api/v1/health`), `API_V1_STR`
(`/api/v1`) — rarely changed; listed for completeness.
