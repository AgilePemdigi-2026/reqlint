# RELEASE_READINESS (Task 07)

**Keputusan:** **READY FOR STAGING.** Produksi menunggu 2 verifikasi eksternal (Docker build, SMTP real-email) yang diblokir infrastruktur/kredensial — bukan oleh defect kode.

---

## Kategorisasi

### PASS (diverifikasi lewat eksekusi nyata)
- Backend pytest **91 passed** (71 Task 06 baseline + 20 Task 06 tests; tanpa regresi Task 07).
- Frontend Vitest **45 passed** (38 + 7 export-integrity baru).
- TypeScript clean; `next build` sukses.
- BDD runner **32 passed** (01–08, termasuk ownership SEC-4 & export).
- DB migration idempotent pada **SQLite eksisting** (live startup, health `db: up`).
- Rule-Based evaluator: default, penalty scoring utuh, IE eksplisit, verdict preserved.
- Traditional ML: genuine `predict_proba` inference (6 dimensi), model_version tampil, strict no-fallback.
- LLM evaluator: mock = FAILED eksplisit (tanpa penyamaran); parse/coerce mocked-transport teruji.
- Shared generator: verdict/score preserved (teruji); grounded pada findings; failure terpisah (PARTIAL).
- Export md/json/csv berfungsi; identitas evaluator + advisory terpisah (Task 07).
- Ownership isolation: detail/export/apply/revision/status semuanya user-scoped (404).

### PARTIAL (implementasi lengkap, verifikasi sebagian)
- Password reset: implementasi + mocked SMTP hijau; **real-email delivery unverified** (kredensial).
- LLM Evaluator C: implementasi + mocked-transport test; **live provider unverified** (kredensial).
- Docker deployment: Dockerfile/compose direview statis + bundle path cocok; **build/Compose belum dijalankan** (Docker tak tersedia).
- Frontend UI acceptance: journey statis + build + unit tests; **klik-per-klik di browser produksi** belum dijalankan di lingkungan ini.

### BLOCKED (infrastruktur/kredensial)
- Docker build + Compose smoke + proxy E2E via frontend (Docker tidak terinstal).
- Real LLM provider connectivity (tanpa GROQ_API_KEY/Ollama).
- Single-use/expiry token: single-use ✅ (used_at), **expiry live test** = BLOCKED (butuh menunggu 1 jam / manipulasi DB — logika terverifikasi kode).

### FAIL
- **Tidak ada.** (Dua defect integritas Task 07 — advisory terbalik & export tanpa identitas — sudah diperbaiki + regression test.)

---

## Checklist sebelum production deployment

1. [ ] **Docker build** backend & frontend image di mesin/host ber-Docker (lihat DEPLOYMENT_VALIDATION §1).
2. [ ] **Compose smoke**: `docker compose up`, health check, proxy `/api` OK, migrasi DB fresh.
3. [ ] **SMTP produksi**: isi `SMTP_HOST/PORT/USERNAME/PASSWORD/FROM` + `PUBLIC_BASE_URL` → satu siklus forgot→email→reset→login nyata.
4. [ ] **LLM provider**: `SLM_PROVIDER=openai_compatible` + `GROQ_API_KEY` (atau Ollama) → satu audit evaluator llm nyata.
5. [ ] `JWT_SECRET` kuat + `ENV=production`.
6. [ ] Volume SQLite (`/app/backend/data`) + backup awal.
7. [ ] Tag rilis + publish `TEST_RESULTS.md` sebagai lampiran.

## Risiko terbuka (terdokumentasi, non-blocking)

- ML bundle dilatih dari data historis tak terverifikasi → keluaran ML = "probabilitas model", dilabeli jujur; validasi kualitas ML menunggu jalur anotasi (Task 04C, deferred).
- 10 fitur konteks ML memakai default pada single-story mode (dikontrak di metadata).
- Proxy frontend lokal tidak dapat diuji tanpa rebuild (bukan defect).
