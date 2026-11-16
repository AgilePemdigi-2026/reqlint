# Research Scope Changelog (Task 04C)

**Tanggal:** 2026-11-13 · **Keputusan oleh:** project owner (Task 04C) · **Berlaku untuk:** benchmark aktif ReqLint.

## Perubahan scope

### C1. Pretrained Encoder dikeluarkan dari evaluator aktif
- **Sebelumnya:** Task 03 §8 mendefinisikan empat evaluator (Rule-based, Traditional ML, Pretrained Encoder, LLM).
- **Kini:** tiga evaluator (A/B/C — lihat `THREE_EVALUATOR_BENCHMARK_SPEC.md`). Encoder menjadi **future work**.
- **Alasan:** tidak ada implementasi/artefak encoder (hanya flag `USE_E5_EMBEDDING=False` yang tak pernah aktif); jendela persiapan 1–2 minggu; kompleksitas fine-tuning multilingual tidak sebanding dgn nilai benchmark saat data anotasi masih kecil.
- **Dampak:** dokumen benchmark hanya membandingkan A/B/C; tidak ada hasil encoder baru; artefak historis tidak dihapus.

### C2. Shared recommendation engine bukan evaluator
- Engine rekomendasi LLM (Stage-2 `nlp_stage2.py` → `ai_rewrite`) terpisah dari benchmark klasifikasi; penilaian kualitasnya **ditunda**. Tidak dihitung sebagai evaluator keempat.

### C3. Alokasi dataset diturunkan menjadi ceiling sementara 120 story
- **Sebelumnya:** `INVEST_DATASET_AUDIT.md` §8 (rekomendasi rekonstruksi #3) menargetkan ~300–1.000 story berlabel baru; Task 03 §6.2 mencatat val ~300 pada split level-proyek.
- **Kini:** target sementara: train 40 (1 annotator), val 10 (1), test 40 (2 annotator), calibration 30 (2) = 120 — **ceiling planning, bukan jaminan**; penurunan lebih diutamakan daripada menurunkan kualitas anotasi. Detail: `ANNOTATION_WORKLOAD_PLAN.md`.

### C4. Validasi historis 60 baris ditunda
- Exercise perbandingan 60 baris historis (Task 04, Validation Plan Fase V4) **bukan pekerjaan wajib**; dapat diaktifkan kembali bila kapasitas ada. 221 label historis tetap kandidat dengan jalur sendiri (`HISTORICAL_*` docs).

### C5. Konsolidasi dokumentasi
- Banner scope ditambahkan ke `BILINGUAL_DATASET_RECONSTRUCTION_SPEC.md` (header, §8, §10.3) tanpa menulis ulang isi historis — lihat `DOCUMENTATION_ALIGNMENT_REPORT.md`.
- Dokumen Task 04 (guideline v1.1, handbook, template 31 kolom, protocol v1.1, QC) sudah direvisi pada revisi Task 04 sebelumnya dan tetap menjadi acuan.

## Yang TIDAK berubah

- Enam kriteria INVEST; tiga label (PASS/FAIL/INSUFFICIENT_EVIDENCE); IE first-class.
- Skema kanonik Task 03 §3; project-level split + `split_group_key` + freeze test (Task 03 §6).
- Isolasi label historis (tidak masuk test/val); pilot-30 tetap referensi.
- Individual annotation immutable; Round 1 independen; Round 2 hanya konflik; adjudication terpisah.

## Urutan eksekusi aktif (§11 brief)

1. Revisi dokumentasi Task 04 — ✅ selesai.
2. Konsolidasi scope ke tiga evaluator — ✅ dokumen ini.
3. Interview singkat annotator historis (`HISTORICAL_ANNOTATOR_INTERVIEW.md`) — **tidak memblokir Task 05**.
4. Task 05 rekonstruksi dataset kanonik → validasi identitas/provenance/bahasa/pasangan/duplikat → manifest split level-proyek → seleksi kalibrasi reproducible → pilot waktu 10 story → reassess kapasitas & finalisasi alokasi.
