# ReqLint — Coolify Single-Domain Compose Deployment

One Coolify resource, one public domain, no PostgreSQL, no Redis, no published
backend port. The Next.js frontend receives all public traffic and reverse-proxies
`/api/*` to the FastAPI backend over Docker's internal network.

This complements (does not replace) the two-application flow in
[DEPLOY_COOLIFY.md](DEPLOY_COOLIFY.md). Use this stack when you want a single
domain and a single Coolify resource. Branch: `deploy/coolify-preview`.

## Architecture

```
Browser ──▶ Coolify proxy ──▶ frontend (Next.js, internal :3000)
                                │  /                    → Next.js pages
                                │  /api/analyze         → Next.js route (local analyzer)
                                │  /api/:path*          → proxied to http://backend:8000
                                │  /docs, /redoc        → proxied to http://backend:8000
                                └─▶ backend (FastAPI, internal :8000)
                                      └─ SQLite on named volume (reqlint_data)
                                         mounted at /app/backend/data
```

- Routing is implemented with Next.js `rewrites()` in `frontend-qa/next.config.js`,
  resolved **server-side** (the browser never talks to the backend directly).
  The proxy target is the build arg `API_PROXY_TARGET` (default `http://backend:8000`,
  matching the compose service name) — rewrites are baked at build time.
- The browser bundle uses the same-origin base `NEXT_PUBLIC_API_URL=/api/v1`
  (relative), set as a build arg by the compose file.
- Auth is JWT Bearer in browser localStorage — no cookies — so proxying needs no
  cookie/CORS handling. Same-origin requests bypass CORS entirely.

## Coolify configuration

1. **New Resource → Docker Compose** build pack, source `farhanAkbar91/reqlint`,
   branch `deploy/coolify-preview`, **Docker Compose file**:
   `docker-compose.coolify.yml`.
2. **Environment Variables** (UI):

   | Variable | Required | Value |
   |---|---|---|
   | `JWT_SECRET` | **Yes** (deploy fails without it) | long random string, e.g. `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `SLM_PROVIDER` | no | `openai_compatible` for Groq; omit for the built-in mock |
   | `SLM_BASE_URL` | no | `https://api.groq.com/openai` |
   | `SLM_MODEL` | no | e.g. `llama-3.1-8b-instant` |
   | `SLM_TIMEOUT_SECONDS` | no | `8` (default 4 can be tight for Groq) |
   | `GROQ_API_KEY` | no | required only if `SLM_PROVIDER=openai_compatible` |
   | `CORS_ORIGINS` | no | unnecessary here (same-origin flow); only for direct cross-origin API consumers |
   | `AUDIT_EXECUTION_MODE` | no | keep `inline` (default). `celery` would require Redis, which this stack does not provide |

   No build-arg configuration is needed in the UI: the compose file passes
   `NEXT_PUBLIC_API_URL=/api/v1` and `API_PROXY_TARGET=http://backend:8000`
   itself. If you change the backend service name, change `API_PROXY_TARGET` too.
3. **Domains**: attach the public domain to the **`frontend`** service **only**
   (port 3000). Leave `backend` without a domain — it is reachable only on the
   internal Docker network (`expose`, no `ports`).
4. **Persistent Storage**: already declared in the compose file as the named
   volume `reqlint_data` mounted at `/app/backend/data` — no extra UI config needed.
5. Deploy. First build takes a while (backend bakes spaCy `en_core_web_sm`).

## Ports & conflicts

Neither service publishes host ports (`expose` only), so nothing can conflict
with other groups on the shared server. Coolify's proxy reaches the frontend
through the internal network.

## Verification checklist

1. `https://<domain>/` loads the app; `/api/v1/health` returns
   `{"status":"success",...}` through the same domain.
2. `https://<domain>/docs` shows FastAPI Swagger UI.
3. Register + login (rows land in the SQLite volume).
4. Editor audit flow; PDF upload (≤10 MB) and export (PDF/MD/JSON).
5. `docker compose -p <project> ps` shows both services healthy
   (`docker inspect` → `Health: healthy`).

## Known limitations

- SQLite is single-writer: fine for a preview, not for multi-instance production.
- `NEXT_PUBLIC_API_URL`/`API_PROXY_TARGET` are build-time values: changing them
  requires a rebuild (redeploy without cache).
- If the backend is temporarily down, proxied API calls return 500s from the
  proxy; the UI shows its own connection-error messaging.
- The INVEST ML bundle stays unloaded (rule-based fallback), matching current
  behavior on this branch (see DEPLOY_COOLIFY.md §6).
