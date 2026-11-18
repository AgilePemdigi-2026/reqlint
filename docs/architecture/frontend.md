# Frontend architecture

The frontend is a Next.js 14 (App Router) + TypeScript + Tailwind CSS application in
`frontend-qa/`. Verified against `bfe72aa`.

## Structure

```
frontend-qa/src/
├── app/
│   ├── page.tsx                  landing page (marketing + interactive demo)
│   ├── login|register|forgot-password|reset-password/   auth pages
│   ├── (app)/                    authenticated workspace (AppShell gate)
│   │   ├── editor/page.tsx       draft editor + evaluator selection
│   │   ├── audit/[id]/page.tsx   audit results
│   │   ├── history/page.tsx      audit history (backend + local)
│   │   ├── help/page.tsx         user guide
│   │   └── contact/page.tsx      contact form (simulated submission)
│   └── api/analyze/route.ts      POST handler running the local rule engine server-side
├── components/                   app-shell, providers, language/theme toggles,
│                                 backend-badge, code-editor, audit/* result components
├── lib/                          api.ts (axios client), auth.ts, i18n.ts, store.ts,
│                                 audits/history/export/pdf helpers, evaluator-options.ts
│   └── analyzer/                 in-browser rule engine (analyze, revise, diff, adapter)
└── types/audit.ts                response types for the legacy /requirements/audit endpoint
```

Redirects in `next.config.js`: `/upload → /editor`, `/signup → /register`, `/audit → /editor`,
`/audit/hasilAudit → /history`. Server-side rewrites proxy `/api/:path*`, `/docs`, `/redoc` to
`API_PROXY_TARGET` (build-time; used by compose deployments).

## Pages

| Route | Purpose |
|---|---|
| `/` | Public landing page with an interactive demo (local analyzer, no backend required) |
| `/editor` | Draft editor (textarea with live squiggle underlines), analysis-language picker (id/en), evaluator selector (Rule-Based / Traditional ML / LLM-SLM), PDF/TXT/MD import, sample templates |
| `/audit/[id]` | Scorecard, category summary, INVEST dimension results (with confidences when the evaluator provides them), findings table, Stage-2 advisory (labeled mock vs provider), 1-click apply, diff view, exports |
| `/history` | Merged backend + local audit history; search, date/grade/language filters, sort, delete (local rows only) |
| `/help` | User guide (steps, grade table, finding categories, writing tips) |
| `/contact` | Contact form — **submission is simulated client-side**; no backend endpoint exists |
| `/login`, `/register`, `/forgot-password`, `/reset-password` | Auth flows; register redirects to login (no auto-login) |

Auth gating: the `(app)` route group is wrapped by `AppShell`, which redirects to `/login` when no
session exists and re-verifies it via `GET /auth/me`.

## State management

No state library — pages use plain axios + custom localStorage stores
(`src/lib/store.ts`, SSR-safe `useSyncExternalStore`, cross-tab sync):

| Key | Content |
|---|---|
| `reqlint.auth_session` | `{ token, user }` (JWT bearer for the axios interceptor) |
| `reqlint.ui_locale` | UI language `'id' | 'en'` |
| `reqlint.audits` / `reqlint.draft` / `reqlint.tip-dismissed` | Local audit history, current draft, editor tip flag |
| `reqlint.theme` | `'light' | 'dark'` (pre-paint script in `layout.tsx` avoids theme flash) |

Only the **draft text** is persisted locally; audit results are recomputed deterministically by the
local engine except for backend-provided scores/status.

## Internationalization

Bilingual UI implemented client-side: a flat dictionary of **501 keys**
(`src/lib/i18n.ts`, each with `id` + `en`), a locale store, a navbar language toggle, and `<html lang>`
sync. UI locale is independent of the **analysis language** of a draft (chosen per draft in the
editor). `scripts/i18n-source-audit.mjs` scans for untranslated user-facing strings.

## Local rule engine vs backend evaluators

- The **landing demo** and the editor's offline fallback run `src/lib/analyzer/` in the browser —
  a deterministic rule engine with five categories: `ambiguity`, `non-testable`, `incomplete`,
  `weak-directive`, `passive-voice`.
- When the backend is reachable, the editor sends the draft to `POST /audits` with the selected
  evaluator. On backend failure, **only Rule-Based falls back to the local engine**; Traditional ML
  and LLM show an explicit error (no silent evaluator swap).
- `src/lib/analyzer/adapter.ts` maps backend payloads to UI shapes, preserving evaluator
  provenance (`requested_evaluator`, `actual_evaluator`, `model_version`, `evaluator_error_code`).

## Backend endpoints called

`POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `POST /auth/forgot-password`,
`POST /auth/reset-password`, `GET /health` (navbar badge, 30 s polling), `POST /documents/upload`,
`POST /audits`, `GET /audits`, `GET /audits/{id}/status`, `GET /audits/{id}`,
`POST /audits/{id}/reanalyze`, `POST /audits/{id}/apply`,
`GET /audits/{id}/export?format=md|json&lang=id|en`.

Endpoint reference: [../api/api-reference.md](../api/api-reference.md).

## Known frontend limitations (verified)

- The UI export menu offers **Markdown / CSV / JSON**; the backend endpoint also supports `pdf`,
  but no PDF option is exposed in the UI. The in-app Help text mentioning PDF export is inaccurate
  on this point.
- The contact form shows "sent" without any backend call.
- `PUT /audits/{id}/revision` (manual revision API) exists in the backend and in `src/lib/api.ts`
  (`apiManualRevision`) but is never called by the UI; the audit page uses `POST /apply` and local
  editing instead.
- The single Cypress spec (`tests-e2e/e2e/editor-audit.spec.ts`) targets selectors and strings from
  a removed legacy editor component — it is stale (see [../development/testing.md](../development/testing.md)).
- A "Backend FastAPI Terhubung" pill on the editor is a static label; the real connectivity
  indicator is the navbar `BackendHealthBadge`. The notifications popover is decorative.
- Legacy dead components remain in the tree (`backend-audit-card.tsx`, `editor/RequirementEditor.tsx`,
  `analysis/*`) — unused by any route.
