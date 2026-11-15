# BASELINE_AND_ENVIRONMENT (Task 08)

**Tanggal:** 2026-11-15 · **HEAD:** `4d6f53c` (`fix/frontend-docker-npm-ci`) · Task 06/07 berupa perubahan working tree (belum di-commit — dipertahankan).

## 1. Arsitektur aplikasi

- **Backend**: FastAPI (`app.main`) — routers: health, auth (register/login/me/forgot/reset), documents (PDF upload), audits (create/list/status/detail/reanalyze/apply/revision/export), lint, requirements (legacy). DB: SQLite (SQLAlchemy async) + kolom baru Task 06 (`evaluator`, `model_version`) via migrasi ringan idempotent.
- **Frontend**: Next.js 14.2.35 App Router (`frontend-qa/src/app`): `/` landing, `/login`, `/register`, `/forgot-password`, `/reset-password`, `/editor`, `/audit/[id]`, `/history`, `/help`, `/contact`.
- **Three evaluators** (Task 06): rule_based / traditional_ml / llm — kontrak bersama `evaluation_contract.py`; shared generator `nlp_stage2.generate_response` (verdict-preserving).

## 2. Deployment assumptions

- Compose single-domain (`docker-compose.coolify.yml`): frontend :3000 (proxy `/api/*` → backend :8000 internal), backend expose-only, SQLite volume, ML bundle di-COPY ke image.
- `next.config.js`: `outputFileTracing: false` (DIDUGA terkait CSS — lihat CSS_LOADING_DIAGNOSIS), rewrites build-time ke `http://backend:8000`.
- Frontend build via `npm ci` + `next build` (Dockerfile), `npm start` produksi.

## 3. i18n architecture (existing)

- `lib/i18n.ts`: store locale persist `reqlint.ui_locale` (default `id`), kamus `translations` (key → {id, en}), `t()` + `useT()`.
- Pengguna: help page, sebagian history. Banyak string Task 06/07 baru masih hardcoded ID (diinventarisasi Phase 3).

## 4. CSS loading diagnosis — RINGKASAN (lengkap di CSS_LOADING_DIAGNOSIS.md)

- **Terverifikasi empiris:** request asset CSS → **HTTP 404** (server mengirim HTML), dan `next start` pada `.next` terbaru gagal `MODULE_NOT_FOUND: ./vendor-chunks/next.js` → halaman tampil tanpa CSS.
- **Akar (eksperimen A/B):** `outputFileTracing: false` di `next.config.js` membuat output build server **kehilangan vendor-chunks** dan asset CSS tidak ter-emit konsisten. Setelah flag dihapus + clean rebuild: CSS 200 (47 KB, berisi `:root` vars + utilities), halaman 200 semua.
- **Faktor pemicu kejadian user:** server `next start` lama yang tetap berjalan saat `.next` dibangun ulang → HTML in-memory merujuk asset lama yang tak ada di disk.

## 5. Coolify prerequisites

- Deploy sebagai **satu Docker Compose application** (paling sederhana & cocok repo — lihat COOLIFY_DEPLOYMENT_GUIDE.md §1).
- Env: JWT_SECRET, ENV, SMTP_*, PUBLIC_BASE_URL, SLM_PROVIDER/GROQ_API_KEY (opsional), DATABASE_URL (default SQLite volume).
- Tanpa kredensial Coolify → deployment aktual **BLOCKED**; semua persiapan lokal selesai.

## 6. Unresolved issues (masuk Task 08)

1. CSS 404 → **fixed** (Phase 1).
2. ISO 29148 di UI → **fixed** (Phase 2 sweep, 9 titik).
3. i18n bilingual belum lengkap → **diperluas** (Phase 3; 190→211 keys, parity test baru; sisa terdokumentasi).
4. Kontras selector → **fixed** (Phase 4; pasangan `--btn/--btn-ink` flip per tema, ≈15:1).
