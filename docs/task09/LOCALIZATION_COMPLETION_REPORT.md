# LOCALIZATION COMPLETION REPORT — Task 09

**Mechanism (unchanged):** `frontend-qa/src/lib/i18n.ts` — `createLocalStore('reqlint.ui_locale', 'id')`,
exported `translations` dictionary, `t()` / `useT()` with `{placeholder}` interpolation, fallback id → raw key.
No new i18n library introduced. Dictionary grew **211 → 383 keys**, ID/EN parity 100% (test-enforced).

## 1. Route-by-route coverage (after Task 09)

| Route / surface | Before | After | Notes |
|---|---|---|---|
| `/` landing (banner, hero, features, how-it-works, standards, privacy, FAQ, final CTA) | ❌ ID-only (server components) | ✅ full ID/EN | converted to client components on the existing store; SSR-safe (server snapshot = `id`), no new hydration mismatch class |
| `/` landing nav + footer + demo card | ❌ ID-only | ✅ full ID/EN | demo-card toasts/labels/aria included |
| `/login` | ❌ ignored `useT()` despite existing `login.*` keys | ✅ full | incl. demo toast, reset-help toast, JWT footer |
| `/register` | ❌ hardcoded | ✅ full | incl. terms toast, validation messages (locale-aware zod) |
| `/forgot-password` | ✅ (Task 08) | ✅ | no change needed |
| `/reset-password` | ⚠️ 2 hardcoded messages | ✅ | `reset.min_chars`, `reset.mismatch` |
| `/editor` | ⚠️ partial | ✅ full | header, backend pill, upload/extract strings, template menu, evaluator aria, 3 live hints, clause/word counts, autosave, CTA, tips card, editor aria/placeholder (via new `CodeEditor` props) |
| `/history` | ⚠️ partial (keys existed but unused) | ✅ full | wired existing `history.*` keys + new filter aria/sort/status keys; confirm dialogs + toasts localized; grade/category labels locale-aware |
| `/audit/[id]` | ⚠️ partial | ✅ full | polling stages, loading card, header, all 10 toasts, privacy note; advisory strings now use the previously-dead `audit.flagged` / `audit.passed_llm` / `audit.unknown_val` keys; evaluator names via `evaluator.*` |
| `/help`, `/contact` | ✅ (Task 08) | ✅ | no change needed |
| App shell (navbar/footer) | ⚠️ `startsWith` hack + hardcoded footer | ✅ | new `nav.help` / `nav.contact` keys replace the fragile prefix hack; `nav.main_nav_aria`, `nav.architecture` |
| Auth shell + password fields | ❌ / ❌ aria | ✅ | `auth.back_workspace`, `fields.show_password` / `fields.hide_password` |
| Backend health badge | ❌ | ✅ | titles + visible labels |
| Language toggle | ✅ | ✅ | aria pattern kept (targets the *other* language in its own language) |
| `<html lang>` | static `id` | ✅ dynamic | new `LocaleHtmlSync` client component (root layout); updates `document.documentElement.lang` on locale change; SSR renders `id` default, no hydration mismatch |

## 2. Library-level localization (UI chrome vs. content)

| Module | Change |
|---|---|
| `lib/format.ts` | `categoryLabel(cat, locale)`, `categoryLabelT(cat, t)`, `gradeLabel`, `gradeTagline`, `formatDate(iso, locale)` (id-ID / en-GB). Legacy static maps removed; all call sites migrated. |
| `lib/ai-status.ts` | `resolveAiSuggestionStatus(detail, locale)` — mock/provider/unavailable/none labels + explanations bilingual. |
| `lib/validation.ts` | schemas became locale-aware factories (`loginSchema(locale?)`, `registerSchema(locale?)`, `analyzeRequestSchema(locale?)`), defaulting to the current UI locale at call time. 13 message keys. |
| `lib/analyzer/adapter.ts` | INVEST note strings (`adapter.invest_unknown` / `adapter.invest_verified`) read from the dictionary. |
| `lib/api.ts` | `extractApiError` fallbacks localized (server error / timeout / unreachable / unexpected); `apiDownloadExport(id, format, lang)` forwards the UI locale; filename corrected to `reqlint-audit-{id}.{ext}` matching the backend `Content-Disposition`. |
| `lib/export.ts` | Markdown labels already bilingual; **`meta.locale` now carries the UI locale** (audit page passes `useUILocale()`, NOT the story language); CSV headers localized; grade/category labels in exports locale-aware. User-authored text and analysis content are never translated. |
| Backend `ExportService` | bilingual label map (`_labels(lang)`), `render_markdown`/`render_pdf` accept `lang`; export endpoint accepts `lang` query (`id` default = backward compatible; `fr` → 422 `UNSUPPORTED_LANG`). |

Analysis content (findings text, recommendations, LLM rationales, rewrites) intentionally follows the
**story language** — that is content, not UI chrome. The UI locale controls every label, heading, verdict
description, toast, filter, aria-label and export metadata label.

## 3. Locale persistence & switching (rendered verification)

Verified in a real browser against the production build (`next start`, port 3100):

- Landing ID (default): hero/features/CTA/nav all Indonesian; `lang="id"`; no EN leakage.
- `localStorage['reqlint.ui_locale'] = '"en"'` + reload: landing fully English; `lang="en"`; no ID leakage in
  checked strings; login page fully English incl. aria ("Show password").
- Switch back to ID: login fully Indonesian; no EN leakage; `lang` returns to `id`.
- Screenshot of EN landing: layout intact (client-conversion caused no visual regression). Demo-card textarea
  content correctly follows the *analysis-language* tab (content, not chrome).

Store behavior unchanged: `useSyncExternalStore` + localStorage persistence; navigation never resets locale;
no SSR/client hydration mismatch introduced.

## 4. Remaining strings (documented, not silently deferred)

1. **Legacy unrendered components** (`components/analysis/AuditScorecard.tsx`, `SmellList.tsx`,
   `audit/backend-audit-card.tsx`, `editor/RequirementEditor.tsx`) still contain Indonesian strings. They are
   imported by **no route** (verified by import scan) — they are dead code preserved untouched per the
   no-deletion safety rule. Listed in the source-audit script's `KNOWN_DEAD`.
2. Root-layout `<title>`/`description` metadata stays Indonesian (build-time metadata; the product title).
3. Technical terms intentionally not translated: Rule-Based, Traditional ML, LLM/SLM, INVEST, User Story,
   Acceptance Criteria, Given/When/Then, BDD, Quality Scorecard, Diff Viewer, model names, API, error codes.

## 5. Completeness tests & tooling

- `src/lib/i18n-task09.test.ts` (11 tests): dictionary non-empty parity per namespace; ~70 required keys
  enumerated across every surface; locale-switch spot checks; ai-status/category/grade/tagline/date locale
  behavior; locale-aware zod messages; markdown/CSV export locale behavior (EN headings, ID backward-compat default).
- `src/lib/i18n.test.ts` (Task 08) unchanged and still green — it now covers all 383 keys for parity.
- `scripts/i18n-source-audit.mjs`: heuristic scanner for hardcoded user-facing strings (JSX text, aria/placeholder/
  title attributes, toast/confirm literals) with explicit allow-lists for CSS classes, keys/routes, technical
  tokens, and identifiers. Result after Task 09: **0 flags on rendered surfaces**; all remaining flags are in
  `KNOWN_DEAD` legacy files. The script itself documents that it is an aid — rendered-page verification (§3)
  is the acceptance evidence.
- Evaluator selector contrast and CSS production-build verification from Task 08 remain intact (build re-verified).
