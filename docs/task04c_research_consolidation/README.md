# Task 04C — Research Scope Consolidation & Annotation Operations Readiness

**Tanggal:** 2026-11-13 · **Sifat:** dokumentasi & perencanaan (bukan implementasi, bukan anotasi).
**Keputusan inti:** benchmark aktif memakai **tiga evaluator** (A Rule-Based, B Traditional ML, C LLM); pretrained encoder dikeluarkan menjadi future work; shared recommendation engine **bukan** evaluator dan benchmark kualitasnya ditunda; alokasi dataset sementara = **ceiling 120 story** (40 train / 10 val / 40 test / 30 calibration) yang boleh diturunkan, bukan jaminan.

## Deliverables

| Dokumen | Fungsi |
|---|---|
| `THREE_EVALUATOR_BENCHMARK_SPEC.md` | Definisi 3 evaluator, skema keluaran bersama, kebijakan 3-kelas, metrik primer/sekunder/operasional, kondisi evaluasi, batasan |
| `RESEARCH_SCOPE_CHANGELOG.md` | Catatan perubahan scope (C1–C5): encoder keluar, engine bukan evaluator, alokasi 120, validasi historis 60 baris ditunda, konsolidasi dokumentasi |
| `ANNOTATION_OPERATIONS_PLAN.md` | Operasional harian: peran & onboarding, alur kalibrasi→R1→R2→adjudication, batch & submission, immutable files, penamaan/SHA-256, blinding, QC koordinator, pengecualian, status batch, kerahasiaan |
| `ANNOTATION_WORKLOAD_PLAN.md` | Unit kerja (190 pada T1), formula estimasi dgn pilot 10 story, tabel sensitivitas (ilustratif), pemisahan beban, penjadwalan realistis, tier fallback T2/T3 |
| `CALIBRATION_BATCH_SELECTION_SPEC.md` | Prosedur seleksi 30 kalibrasi (15/15, ≥5 proyek): pool, stratifikasi tekstual (bukan label model), pasangan terjemahan, seed reproducible, replacement, manifest, blinding, fallback 20/12 |
| `HISTORICAL_ANNOTATOR_INTERVIEW.md` | Panduan interview annotator asli (7 bagian, netral; memisahkan fakta Git vs yang perlu konfirmasi); tidak memblokir Task 05 |
| `DOCUMENTATION_ALIGNMENT_REPORT.md` | Peta implementasi vs desain riset vs deferred; register kontradiksi (K1–K5) & resolusi |
| `README.md` | Dokumen ini |

## Dependencies

- **Task 04** (selesai + revisi terarah): Guideline v1.1, Handbook, Template 31 kolom, Protocol v1.1, QC — menjadi acuan proses anotasi.
- **Task 04B**: klas provenance A/A'/A''/B/C dan batasan data historis.
- **Task 05** (belum mulai): dataset kanonik — prasyarat seleksi kalibrasi, split manifest, dan benchmark.

## Deferred work (bukan deliverable saat ini)

Full-corpus annotation; double annotation penuh untuk training; validasi historis 60 baris; implementasi/fine-tuning encoder; full-scale tuning; significance testing kompleks; benchmark kualitas recommendation engine; dashboard perbandingan model; ekspansi dokumentasi tambahan.

## Keputusan yang butuh persetujuan manusia

OD-1…OD-10 (lihat Protocol §8 & README Task 04) tetap; ditambah dari paket ini: persetujuan **tier alokasi** (T1/T2/T3) bila kapasitas terbatas, dan **status final pilot-30** (OD-6).

## Urutan eksekusi

Ikuti §11 brief: selesaikan revisi Task 04 (✅) → konsolidasi scope (✅, folder ini) → interview historis (tidak memblokir) → **Task 05** → validasi dataset → split manifest → seleksi kalibrasi → pilot waktu 10 story → finalisasi alokasi. Jendela 1–2 minggu adalah target persiapan, bukan mandat menuntaskan eksperimen downstream — validitas fondasi diutamakan.
