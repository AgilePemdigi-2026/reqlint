# RELEASE_READINESS (Task 06)

## Status: RELEASE-READY dengan 1 prasyarat deployment + 2 keterbatasan terdokumentasi

| Area | Status |
|---|---|
| Tiga evaluator selectable + kontrak bersama | ✅ selesai + teruji |
| Traditional ML genuine inference (bundle shipped, sklearn pinned) | ✅ kode + test; build Docker menunggu lingkungan Docker |
| Shared generator verdict-preserving | ✅ (teruji: skor identik sebelum/sesudah generation) |
| Frontend selector + provenance + error eksplisit | ✅ (tsc clean, build sukses, vitest 38) |
| Reset password email delivery | ✅ implementasi + test mocked; **real-email pending SMTP credentials** |
| ISO labeling jujur | ✅ (meter direname, landing dilunakkan) |
| Regresi | ✅ pytest 91, vitest 38, BDD 32 — semua hijau |
| Docker build aktual | ⚠️ menunggu lingkungan Docker (verifikasi statis selesai) |
| Smoke via proxy frontend lokal | ⚠️ keterbatasan build-time target (bukan regresi) |

## Yang harus disiapkan saat deployment (env)

```
SMTP_HOST=…            SMTP_PORT=587       SMTP_USERNAME=…      SMTP_PASSWORD=…
SMTP_FROM=reqlint@…    SMTP_USE_TLS=true   PUBLIC_BASE_URL=https://<domain>
SLM_PROVIDER=…         GROQ_API_KEY=…      (opsional; mock → LLM evaluator = FAILED eksplisit)
```

## Checklist rilis

1. [x] 3 evaluator selectable, kontrak bersama, verdict preservation — kode + test.
2. [x] ML bundle dikirim ke image (Dockerfile COPY) + sklearn/joblib pinned.
3. [x] Reset password end-to-end (mocked SMTP) + tanpa kebocoran token.
4. [x] ISO labeling jujur; tanpa meter menyesatkan.
5. [x] Regresi hijau (pytest 91, vitest 38, BDD 32).
6. [ ] Docker build + compose smoke — **jalankan di lingkungan Docker** (satu perintah, tanpa perubahan kode).
7. [ ] Konfigurasi SMTP produksi + satu pengiriman email nyata sebagai smoke.
8. [ ] (Opsional) GROQ_API_KEY untuk Evaluator C di produksi.
