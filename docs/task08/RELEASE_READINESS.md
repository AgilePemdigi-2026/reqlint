# RELEASE_READINESS (Task 08)

**Keputusan:** **READY FOR STAGING DEPLOYMENT** ke Coolify dosen — menunggu akses environment (BLOCKED eksternal) dan 1 verifikasi email nyata.

---

## Kategorisasi requirement Task 08

| Requirement | Status | Bukti |
|---|---|---|
| CSS dimuat dengan benar | **PASS** | asset CSS 200 (47 KB, vars+utilities) di 3 halaman; akar `outputFileTracing:false` dihapus; server fresh hijau |
| Build produksi memuat CSS | **PASS** | clean rebuild 2×; CSS hashed ter-emit (`6ac90280…`) |
| ISO 29148 claims dihapus dari UI | **PASS** | 9 titik diperbaiki (hero, features, standards card, footer, metadata, editor subtitle, register, i18n ×2, summary meter); live HTML sweep 0 kemunculan di 5 halaman |
| Fitur evaluasi tetap utuh | **PASS** | pytest 91, vitest 51, BDD 32 — tanpa regresi |
| i18n bilingual (app area) | **PASS** | 211 keys parity penuh; Task 06/07 strings terkabel; test parity baru |
| i18n bilingual (landing) | **PARTIAL** | copy marketing masih ID; toggle bahasa di app shell (tidak memunculkan UI campuran); deferred |
| ~18 string mikro tanpa i18n | **PARTIAL** | aria-label & label mikro; prioritas berikutnya |
| Evaluator selector kontras | **PASS** | pasangan `--btn/--btn-ink` ≈15.5:1 (light) & ≈13.7:1 (dark) — lolos AA/AAA; ikon centang non-warna; focus ring |
| Selector → payload benar | **PASS** | test vitest (options/default) + live smoke sebelumnya (3 evaluator) |
| Docker build & compose smoke | **BLOCKED** | Docker tidak terinstal; review statis lengkap (bundle path, pin sklearn) |
| SMTP real-email | **BLOCKED** | kredensial tidak ada; implementasi + mocked tests lengkap |
| LLM provider nyata | **BLOCKED** | kredensial tidak ada; mocked-transport tests hijau |
| Coolify deployment aktual | **BLOCKED** | akses environment dosen tidak tersedia (guide lengkap tersedia) |

---

## Checklist pra-deploy di Coolify (untuk user)

1. Commit & push branch + merge ke `main` (Task 06/07/08 changes).
2. Coolify → New Resource → **Docker Compose** → repo `AgilePemdigi-2026/reqlint` branch `main` → compose file `docker-compose.coolify.yml`.
3. Domain → service `frontend` (port 3000) + HTTPS.
4. Env backend: `ENV=production`, `JWT_SECRET=<random>`, `DATABASE_URL=sqlite+aiosqlite:///./data/reqlint.db`, `PUBLIC_BASE_URL=https://<domain>`, SMTP_* (wajib utk reset password), `SLM_PROVIDER/GROQ_API_KEY` (opsional).
5. Volume: `/app/backend/data` (SQLite persisten).
6. Deploy → tunggu build → jalankan checklist verifikasi (COOLIFY_DEPLOYMENT_GUIDE §4).
7. Rollback: Redeploy commit/tag sebelumnya; data aman di volume.

## Risiko tersisa (non-blocking, terdokumentasi)

- Docker build belum pernah dijalankan di mesin mana pun untuk Task 06-07 changes (bundle COPY path + pin sklearn diverifikasi statis) — jalankan di host Coolify.
- Landing page copy masih ID (language toggle di app shell) — deferred.
- ~18 string mikro + aria-label ID — deferred.
- Traditional ML: keluaran = probabilitas model dari data historis tak terverifikasi — dilabeli jujur di UI; validasi menunggu jalur anotasi.
