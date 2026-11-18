# Troubleshooting

Verified failure modes and fixes. If a problem isn't here, check the backend logs first — most
failure paths log a stable error code.

## Frontend / Node

**`npm ci` fails with `ERESOLVE`** — `vitest@5` declares a peer `@types/node ^22 || >=24` while
the project pins `@types/node@20`. Install with `npm ci --legacy-peer-deps` (same as CI and the
Dockerfile).

**Landing page demo works, editor audits fail** — the demo runs the in-browser rule engine; audits
need the backend. Check the navbar health badge (`GET /health`, 30 s polling) and that
`NEXT_PUBLIC_API_URL` points at a reachable API.

**401 on every API call** — expired/invalid session. The JWT expires after `JWT_EXPIRE_HOURS`
(default 24); log in again. Sessions are per-browser (`localStorage['reqlint.auth_session']`).

## Backend startup

**`RuntimeError: JWT_SECRET is required when ENV is not 'dev'.`** — set `JWT_SECRET` to a long
random string (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`), or use
`ENV=dev` for local development (an ephemeral secret is generated). The published placeholder
value from `.env.example` is also rejected when `ENV != 'dev'`.

**`RuntimeError` mentioning the published example secret** — you copied `.env.example` verbatim;
replace `JWT_SECRET` with a real random value.

**spaCy warning about fallback model** — `en_core_web_sm` could not be loaded; the app continues
with `spacy.blank("en")` and English passive-voice detection degrades. Fix:
`python -m spacy download en_core_web_sm`.

**Two backend processes see different data** — the SQLite path is relative to the **current
working directory** (`./reqlint.db`). Start the server consistently (e.g. always with
`uvicorn app.main:app --app-dir backend` from the repo root) or set an absolute `DATABASE_URL`.

## Traditional ML evaluator

**`ML_EVALUATOR_UNAVAILABLE` on a Traditional ML audit** — the model bundle was not found or is
corrupt. The service probes `pm-docs/rubrics/reqlint_invest_models.pkl` (then `models/` subdir,
then cwd-relative copies). Run the backend from the repository root, or in Docker use an image
built with the bundle included (see [../deployment/docker.md](../deployment/docker.md)).

**`InconsistentVersionWarning` / unpickling errors** — the bundle requires `scikit-learn==1.7.2`
(pinned in `backend/requirements.txt`). Install exactly that version.

**ML verdicts look weak for some criteria** — expected: embedded training F1 ranges ≈ 0.49–0.90
per criterion/language (see [../features/traditional-ml.md](../features/traditional-ml.md)).

## LLM / Stage 2

**Audit status `PARTIAL`** — evaluation succeeded but Stage-2 generation failed
(`stage2_status=FAILED`). Check provider config (`SLM_*`, `GROQ_API_KEY`) and reachability;
`reanalyze` reruns the pipeline.

**`LLM_PROVIDER_KEY_MISSING`** — `SLM_PROVIDER=openai_compatible` without `GROQ_API_KEY`.

**Audit `FAILED` with `LLM_EVALUATOR_UNAVAILABLE` while using the mock provider** — by design:
the LLM evaluator refuses mock output. Configure a real provider or switch evaluator.

**Multiple `SLM_*` variables fight each other** — python-dotenv lets the **last** assignment in
`.env` win; define each `SLM_*` variable exactly once (Task 09 incident, documented in
`backend/.env.example`).

## Docker / Compose

**Backend build fails with `"/pm-docs/rubrics/reqlint_invest_models.pkl": not found`** — the build
context excluded `pm-docs/`. Fixed by the scoped `.dockerignore` exception
([../deployment/docker.md](../deployment/docker.md), PR #25); ensure your checkout includes it.

**Compose port conflicts (5432/6379)** — the root `docker-compose.yml` publishes PostgreSQL and
Redis host ports; on shared servers use `docker-compose.coolify.yml` (no published ports).

**Data disappears after redeploy** — SQLite lives in the container unless a volume is mounted
(`/app/backend/data` with `DATABASE_URL=sqlite+aiosqlite:///./data/reqlint.db`); the Coolify
compose file declares the `reqlint_data` volume for this.

**Frontend reaches a stale backend URL** — `NEXT_PUBLIC_API_URL` and `API_PROXY_TARGET` are
**build-time** values; rebuild the frontend image after changing them.

## Repository hygiene notes (known, not fixed here)

- `backend/alembic/versions/` has a single initial migration predating the `evaluator` /
  `model_version` columns; startup's `create_all` + column patch is the supported schema path.
- A few unused artifacts remain in the tree (dead health route file, unused schemas, a dead
  `TemuanCacat.kriteria_penerimaan` column, six identical tracked PDFs in
  `backend/storage/cache/`, a stub root `package-lock.json`). None affect runtime behavior.
