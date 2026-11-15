# DEPLOYMENT_VALIDATION (Task 07)

## 1. Docker build & Compose — **BLOCKED (infrastructure)**

`docker` **tidak terinstal** di mesin ini (`which docker` → tidak ada). Sesuai aturan Task 07, **tidak ada klaim build Docker** — inspeksi statis berikut adalah review, bukan pengganti build:

| Pemeriksaan statis | Hasil |
|---|---|
| Bundle ML ikut image backend | ✅ `Dockerfile`: `COPY pm-docs/rubrics/reqlint_invest_models.pkl /app/pm-docs/rubrics/…` — **cocok dengan path kandidat #1 loader** `InvestMLService` (`/app/pm-docs/rubrics/`) |
| sklearn pin = versi bundle | ✅ `requirements.txt`: `scikit-learn==1.7.2` (bundle tertulis 1.7.2); catatan: lingkungan dev lokal 1.8.0 memicu warning (fungsional) |
| joblib | ✅ `joblib>=1.3.0` |
| Frontend build deps | ✅ `npm ci` + `next build` sukses lokal (Node 24) |
| Compose `evaluator` flow | ✅ tidak ada config compose yang menghalangi dispatch evaluator (semua di backend) |
| Variabel env baru (SMTP/PUBLIC_BASE_URL) | ✅ terdokumentasi di `backend/.env.example` + `IMPLEMENTATION_REPORT.md` |
| Compose validation (`docker compose config`) | ❌ **BLOCKED** — butuh Docker |

**Yang harus dijalankan saat Docker tersedia:** build backend & frontend image → verify pkl di image (`docker run --rm <img> ls /app/pm-docs/rubrics/`) → compose up → health check → migrasi DB fresh & existing → smoke 3 evaluator via proxy frontend.

## 2. Migrasi database — ✅ terverifikasi LIVE (bukan statis)

- Backend dijalankan langsung terhadap **SQLite eksisting** (`backend/reqlint.db`, dibuat sebelum kolom baru ada).
- `init_db` `create_all` + migrasi ringan idempotent menambahkan `audit_kebutuhan.evaluator` & `model_version` tanpa error → `GET /health` = `{"db":"up"}` → audit baru sukses ditulis dengan kolom baru.
- Aman untuk DB eksisting: migrasi hanya ADD COLUMN (tidak drop/rename), PostgreSQL memakai ALTER + exception-guard.

## 3. Konfigurasi deployment (review .env.example & secrets)

| Item | Status |
|---|---|
| `.env.example` SMTP + PUBLIC_BASE_URL | ✅ terdokumentasi (`backend/.env.example`), `SMTP_HOST` kosong = delivery dimatikan dengan warning |
| Secret handling | ✅ SMTP_PASSWORD/GROQ_API_KEY hanya env backend; **tidak ada** `NEXT_PUBLIC_*` yang membawa secret; GROQ key hanya dibaca backend (`nlp_stage2._call_provider` header) |
| Kebocoran secret via API/log | ✅ token reset tidak pernah muncul di respons/log (hanya info "delivered"); `error_message` internal tidak diekspos (coded `evaluator_error` saja) |
| CORS & API base | ✅ tidak berubah pada Task 06/07 |
| LLM provider config | ✅ `SLM_PROVIDER/SLM_BASE_URL/SLM_MODEL/GROQ_API_KEY` — mock default → LLM evaluator FAILED eksplisit (per desain) |

## 4. Environment variables untuk produksi (checklist)

```
# Wajib
JWT_SECRET=<random>            ENV=production
# Email (Task 06/07)
SMTP_HOST=…                    SMTP_PORT=587
SMTP_USERNAME=…                SMTP_PASSWORD=…
SMTP_FROM=reqlint@…            SMTP_USE_TLS=true
PUBLIC_BASE_URL=https://<domain>
# LLM evaluator C (opsional — tanpa ini evaluator llm = FAILED eksplisit)
SLM_PROVIDER=openai_compatible SLM_BASE_URL=https://api.groq.com/openai
SLM_MODEL=llama-3.1-8b-instant GROQ_API_KEY=…
# DB (opsional; default SQLite di image)
DATABASE_URL=…
```
