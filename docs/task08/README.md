# Task 08 — Coolify Deployment & UI Stabilization

**Tanggal:** 2026-11-15 · **Hasil:** CSS diperbaiki (akar: `outputFileTracing:false`), ISO claims dihapus dari UI (9 titik), i18n diperluas (211 keys parity penuh), selector contrast fixed (≈15:1 AA/AAA), konfigurasi Coolify siap — deployment aktual **BLOCKED** menunggu akses environment dosen.

## Dokumen

| Dokumen | Isi |
|---|---|
| `BASELINE_AND_ENVIRONMENT.md` | Arsitektur, deployment assumptions, i18n architecture, ringkasan diagnosis CSS, prerequisites Coolify, unresolved issues |
| `CSS_LOADING_DIAGNOSIS.md` | **Akar masalah CSS**: eksperimen A/B — `outputFileTracing: false` merusak output build (vendor-chunks hilang → 500; asset CSS 404 → HTML-only); fix + verifikasi live (CSS 200/47 KB) |
| `I18N_COMPLETION_REPORT.md` | Inventarisasi string, 21 key baru (211 total, parity penuh), wiring komponen, sisa terdokumentasi (landing, aria-label mikro) |
| `UI_ACCESSIBILITY_REPORT.md` | Akar kontras (`--paper` tak terdefinisi → teks = background), fix `--btn/--btn-ink`, verifikasi WCAG ≈15.5:1/13.7:1, focus ring, ikon non-warna |
| `COOLIFY_DEPLOYMENT_GUIDE.md` | Keputusan arsitektur (1 Compose app), konfigurasi UI dosen, env template, domain/HTTPS, volume SQLite, health verification, log, rollback; deployment aktual BLOCKED |
| `TEST_RESULTS.md` | pytest 91 ✅, vitest 51 ✅ (+6), tsc clean, build sukses, BDD 32 ✅, live CSS/ISO verification; Docker = BLOCKED |
| `RELEASE_READINESS.md` | Kategorisasi PASS/PARTIAL/BLOCKED/FAIL + checklist pra-deploy |
| `README.md` | Dokumen ini |

## Empat acceptance requirements Task 08

1. **CSS loading** — **PASS**: akar = `outputFileTracing:false` merusak build (A/B experiment); asset CSS 200/47 KB terverifikasi live di 3 halaman.
2. **ISO 29148 claims** — **PASS**: 0 kemunculan di HTML live (landing/editor/login/help/register); sisa hanya nama field API (`iso_29148`), komentar kode, dan dokumen historis.
3. **i18n bilingual** — **PASS (app area) / PARTIAL (landing)**: 211 keys parity penuh + 6 test baru; landing deferred (terdokumentasi).
4. **Selector contrast** — **PASS**: `--btn/--btn-ink` flip per tema ≈13.7–15.5:1 (AA & AAA), ikon centang non-warna, focus ring terlihat.

## Regresi

pytest **91 passed** · Vitest **51 passed** (45 + 6) · tsc **clean** · next build **sukses** · BDD **32 passed** · Docker = **BLOCKED** (tidak terinstal).

## Yang tidak diubah

Dataset, arsip snapshot, label historis, guideline/protokol anotasi, dokumen Task 01–04C, kode ML experiments, Git history — **nol modifikasi** (diverifikasi `git status`).
