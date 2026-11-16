# Task 07 — Release Candidate Validation & Product Readiness

**Tanggal:** 2026-11-15 · **Sifat:** validasi, hardening terukur, dan kesiapan rilis — dibangun di atas working tree Task 06 (HEAD `4d6f53c`, perubahan Task 06 tidak di-commit, dipertahankan).
**Keputusan:** **READY FOR STAGING** — produksi menunggu 2 verifikasi eksternal (Docker build, SMTP real-email).

## Dokumen

| Dokumen | Isi |
|---|---|
| `BASELINE_AND_CHANGE_INVENTORY.md` | Git/HEAD, 21 file modified + untracked, status Task 06 diverifikasi ulang, blockers, inkonsistensi (5 temuan) |
| `THREE_EVALUATOR_ACCEPTANCE.md` | Acceptance live: **cerita sama × 3 evaluator** — tabel side-by-side, penjelasan perbedaan (bukan disamarkan), checklist per evaluator |
| `DEPLOYMENT_VALIDATION.md` | Docker **BLOCKED** (tidak terinstal — tanpa klaim palsu), review statis Dockerfile/compose/bundle-path, migrasi DB terverifikasi live, checklist env produksi |
| `SECURITY_REVIEW.md` | Token single-use/expiry, ownership 404 (termasuk export), SQLi, log/respons leakage, env exposure, migrasi safety |
| `TEST_RESULTS.md` | Semua eksekusi nyata: pytest 91, vitest 45 (+7 export-integrity baru), tsc/build, BDD 32, live smoke 3 evaluator; defect Task 07 yang diperbaiki |
| `RELEASE_READINESS.md` | Kategorisasi PASS/PARTIAL/BLOCKED/FAIL + checklist pra-produksi |
| `README.md` | Dokumen ini |

## Ringkasan validasi

- **PASS:** pytest 91 (71 baseline + 20 Task 06, tanpa regresi), vitest 45 (38 + 7 baru), tsc clean, next build sukses, BDD 32, migrasi DB live pada SQLite eksisting, ownership isolation (detail/export/apply/revision), token reset single-use + anti-enumeration + no-token-leak, verdict preservation live (skor 95.0 rule_based tak terpotong LLM), ML genuine inference live (6 dimensi berprobabilitas), LLM mock = FAILED eksplisit, export integrity (identitas evaluator + model + advisory terpisah), ISO labeling jujur.
- **Diperbaiki Task 07:** (1) advisory `ai_invest_notes` ter-render terbalik di UI/export; (2) export tidak membawa identitas evaluator/model/advisory → `ExportMeta` + 7 regression test; (3) adapter return-type diperluas; (4) fixture `seq`.
- **PARTIAL:** SMTP real-email; LLM live provider; Docker deployment; UI click-through produksi.
- **BLOCKED:** Docker build/compose (infrastruktur), SMTP kredensial, LLM kredensial, expiry-token live test.
- **FAIL:** tidak ada.

## Artefak riset

Task 01–04C, arsip `docs/dataset_archives/family_b/`, template/guideline, kode eksperimen ML: **nol modifikasi** (diverifikasi via `git status` — perubahan hanya di file implementasi Task 06/07).

## Langkah menuju produksi

1. Jalankan Docker build + compose smoke di mesin ber-Docker (DEPLOYMENT_VALIDATION §1).
2. Konfigurasi SMTP produksi + 1 email nyata (checklist RELEASE_READINESS).
3. Konfigurasi LLM provider untuk Evaluator C (opsional).
4. Tag rilis; Task 05-dataset (rekonstruksi kanonik) tetap deferred sebagai jalur riset.
