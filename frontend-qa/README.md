# ReqLint Frontend + QA Workspace

This folder contains the Next.js 14 (App Router) web UI and the frontend QA suites. It is part of
the ReqLint monorepo and requires the FastAPI backend (see `../backend/`) for all authenticated
features — the landing-page demo runs a local in-browser rule engine and works without the backend.

## Responsibilities
1. **Frontend**: draft editor with live linting, audit results (scorecard, findings, INVEST
   dimensions with confidences, evaluator provenance), history, exports, bilingual ID/EN UI.
2. **QA**: Vitest unit tests (`src/**/*.test.ts`, 74 cases) and Cypress E2E specs
   (`tests-e2e/`) — note the current E2E spec is stale (targets a removed legacy editor) and
   needs a rewrite before it can gate anything.

## Quickstart

1. **Install Dependencies** (pinned peer-deps conflict requires the legacy flag):
   ```bash
   npm ci --legacy-peer-deps
   ```

2. **Start Dev Server** (with the backend running on :8000):
   ```bash
   npm run dev
   ```
   Access application at `http://localhost:3000`. The API base URL defaults to
   `http://localhost:8000/api/v1` (`NEXT_PUBLIC_API_URL`, see `src/lib/api.ts` and
   `.env.example`).

3. **Run Tests**:
   ```bash
   npm test          # Vitest unit tests
   npm run lint      # ESLint (runs in CI)
   npm run test:e2e  # Cypress (interactive; spec currently stale)
   ```

Details: [../docs/architecture/frontend.md](../docs/architecture/frontend.md) ·
[../docs/development/testing.md](../docs/development/testing.md)
