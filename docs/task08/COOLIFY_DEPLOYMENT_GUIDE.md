# COOLIFY_DEPLOYMENT_GUIDE (Task 08 Phase 5)

**Target:** Coolify dosen (akun/akses milik dosen — **tidak diminta dan tidak tersedia di sesi ini**). Semua langkah lokal sudah disiapkan; deployment aktual = **BLOCKED** sampai akses diberikan.

## 1. Keputusan arsitektur deployment

**Satu Docker Compose application** (`docker-compose.coolify.yml` yang sudah ada di repo): frontend (Next.js :3000, satu-satunya service ber-domains) + backend (FastAPI :8000, internal `expose`) + SQLite volume (`/app/backend/data`) + **bundle ML ikut image backend** (Task 06).

**Rationale:** satu domain publik, frontend mem-proxy `/api/*` ke `backend:8000` (rewrite build-time), tanpa port internal terekspos, tanpa service DB terpisah (SQLite di volume), dan sesuai pola compose yang sudah diverifikasi pada Task 06/07. Memecah menjadi 2 Coolify app menambah reverse-proxy manual tanpa manfaat untuk demo kelas.

## 2. Persiapan repo (sebelum deploy)

1. Commit & push branch kerja (Task 06/07/08) → merge ke `main` (Tag `v1.0.0-rc1` disarankan).
2. Pastikan `docker-compose.coolify.yml` = file compose sumber di Coolify.
3. `backend/Dockerfile` sudah men-COPY bundle ML; `requirements.txt` sudah pinned `scikit-learn==1.7.2`.

## 3. Konfigurasi Coolify (langkah di UI dosen)

1. **New Resource → Docker Compose** → pilih repo + branch `main`.
2. **Docker Compose file**: `docker-compose.coolify.yml`.
3. **Domains**: attach ke service `frontend` saja, port **3000**. Backend tanpa domain.
4. **Environment variables** (service `backend`):

```
ENV=production
JWT_SECRET=<random 32-byte hex>
DATABASE_URL=sqlite+aiosqlite:///./data/reqlint.db
SLM_PROVIDER=openai_compatible        # opsi; default mock
SLM_BASE_URL=https://api.groq.com/openai
SLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=<key>
# Password reset email (Task 06) — wajib agar alur reset berfungsi
SMTP_HOST=…                SMTP_PORT=587
SMTP_USERNAME=…            SMTP_PASSWORD=…
SMTP_FROM=reqlint@…        SMTP_USE_TLS=true
PUBLIC_BASE_URL=https://<domain-frontend>
```

5. **Persistent storage**: volume `backend-data` → mount `/app/backend/data` (SQLite).
6. **Deploy** → tunggu build (backend ± beberapa menit: spaCy + sklearn 1.7.2 + COPY bundle ML).

## 4. Health verification (pasca-deploy)

1. `GET https://<domain>/` → 200 **dengan CSS termuat** (hash `/_next/static/css/*.css` → 200).
2. `GET https://<domain>/api/v1/health` → `{"db":"up","slm":"mock|up",…}`.
3. Register → login → buat audit (tiap evaluator) → polling → detail → export.
4. Evaluator `traditional_ml` → pastikan log backend **tidak** memuat `ML_EVALUATOR_UNAVAILABLE` (bundle ter-load) dan detail memuat `model_version=2.1.0-srs-hybrid`.
5. Evaluator `llm` tanpa provider → FAILED eksplisit `LLM_EVALUATOR_UNAVAILABLE` (per desain).
6. Forgot-password → email tiba (butuh SMTP kredensial) → reset → login.
7. Landing & editor: **tanpa teks "ISO 29148"**; selector terbaca.

## 5. Log inspection

- Coolify → service backend → Logs: awasi `ML_EVALUATOR_UNAVAILABLE`, `LLM_EVALUATOR_UNAVAILABLE`, `GENERATION_FAILED`, `SMTP not configured`.
- Frontend → Logs: build time (CSS emission) + runtime (tanpa 404 `/_next/static/css`).

## 6. Rollback

- Coolify **Redeploy** ke commit/tag sebelumnya (build per commit, immutable).
- DB SQLite bertahan di volume → rollback kode tidak menghapus data; migrasi kolom Task 06 idempotent (aman diulang).

## 7. Status

- Semua persiapan lokal: **PASS** (build lokal, test, smoke API, asset CSS terverifikasi).
- Deployment aktual ke Coolify dosen: **BLOCKED** — menunggu akses/undangan ke environment dosen (jangan minta kredensial; minta **undangan member/invite** ke workspace Coolify).
