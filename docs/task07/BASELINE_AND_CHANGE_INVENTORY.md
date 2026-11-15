# BASELINE_AND_CHANGE_INVENTORY (Task 07)

**Tanggal:** 2026-11-15 · **Branch:** `fix/frontend-docker-npm-ci` · **HEAD:** `4d6f53c` (Task 06 tidak di-commit — sesuai instruksi; seluruh perubahan Task 06 berada di working tree).

## 1. Status Git

- **Tracked modified: 21 file** (11 backend + 10 frontend-qa) = implementasi Task 06 — daftar lengkap di `docs/task06/IMPLEMENTATION_REPORT.md`.
- **Untracked baru:** `backend/tests/test_task06_evaluators.py` (20 test), `docs/task06/` (6 dokumen), `docs/task07/` (paket ini), ditambah artefak sebelumnya yang dipertahankan (Task 01–04C docs, `docs/annotation_preparation/`, `docs/dataset_archives/family_b/`, 20+ laporan audit root).
- **Insidental:** `frontend-qa/tsconfig.tsbuildinfo` berubah karena build (byproduct, dibiarkan).
- `git diff --stat`: 21 files, +844/−73 — sesuai implementasi Task 06, tanpa perubahan di luar daftar.

## 2. Status implementasi Task 06 (diverifikasi ulang, bukan diasumsikan)

| Komponen | Verifikasi Task 07 |
|---|---|
| Rule-Based evaluator | ✅ pipeline + scoring internal utuh; dimensi V/T genuin, I/N/E/S = IE (`EVALUATOR_UNSUPPORTED_DIMENSION`) |
| Traditional ML | ✅ genuine inference di live server (model_version `2.1.0-srs-hybrid`, 6 dimensi ber-probabilitas); strict error tanpa fallback regex |
| LLM/SLM | ✅ dengan mock = FAILED eksplisit `LLM_EVALUATOR_UNAVAILABLE`; provider nyata = pending kredensial |
| Shared generator | ✅ verdict-preserving (teruji: skor identik sebelum/sesudah generation); grounded pada findings |
| Evaluator selector frontend | ✅ 3 opsi, default Rule-Based; fallback browser hanya Rule-Based |
| Migration DB | ✅ kolom `evaluator/model_version` ditambah idempotent pada DB SQLite eksisting saat startup live (health `db: up`) |
| Reset password SMTP | ✅ implementasi + test mocked SMTP; **real-email unverified** (tidak ada kredensial) |

## 3. Deployment blockers saat ini

1. **Docker build & compose smoke** — Docker tidak terinstal di mesin ini → BLOCKED (bukan FAIL; konfigurasi direview statis).
2. **SMTP credentials** — real-email delivery unverified (test mocked SMTP 20/20 hijau).
3. **LLM provider credentials** (GROQ_API_KEY/Ollama) — klasifikasi LLM live unverified (mock transport test hijau).

## 4. Inkonsistensi implementasi ↔ dokumentasi ↔ kode (ditemukan & ditangani)

| # | Temuan | Status |
|---|---|---|
| 1 | Advisory `ai_invest_notes` ter-render **terbalik** di halaman hasil & export (flag `false` = gagal menurut LLM, tapi UI menulis "lolos") | **DEFECT — FIXED Task 07** + 7 regression test export |
| 2 | Export (md/json) tidak membawa identitas evaluator/model_version/advisory | **DEFECT — FIXED Task 07** (ExportMeta + 7 test) |
| 3 | UI belum menampilkan dimensi PASS/FAIL/IE per kriteria untuk audit ML/LLM | Diperbaiki via kontrak `evaluation` di detail (frontend menampilkan evaluator identity; kartu dimensi = P1, lihat README) |
| 4 | `INVEST_DATASET_AUDIT.md` §8 (Task 01) merekomendasikan 300–1.000 story vs ceiling 120 (Task 04C) | Catatan historis dipertahankan — terdokumentasi di Task 04C Alignment Report K2 |
| 5 | `tsconfig.tsbuildinfo` berubah oleh build | Byproduct build (insidental), dibiarkan |

## 5. Perintah eksekusi (baseline)

```
python -m pytest backend/tests -q        # backend (termasuk pytest-bdd 01–08)
cd frontend-qa && npx vitest run         # frontend
cd frontend-qa && npx tsc --noEmit       # typescript
cd frontend-qa && npx next build         # production build
python run_bdd.py                        # BDD runner
```
