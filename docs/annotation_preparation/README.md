# Annotation Preparation Package — ReqLint INVEST (Task 04)

**Status:** Paket persiapan anotasi siap pakai untuk **dua annotator manusia independen** (bukan implementasi aplikasi, bukan anotasi otomatis).
**Dasar:** `BILINGUAL_DATASET_RECONSTRUCTION_SPEC.md` (Task 03), audit Task 01/02/04A/04B, arsip `docs/dataset_archives/family_b/`.
**Catatan bahasa:** dokumen ditulis Indonesia-primary; istilah teknis (PASS/FAIL/INSUFFICIENT_EVIDENCE, kode rationale) tetap Inggris agar konsisten dengan skema data.

## Isi folder dan fungsi masing-masing dokumen

| # | Dokumen | Fungsi | Pemakai |
|---|---|---|---|
| 1 | `INVEST_ANNOTATION_GUIDELINE.md` | Definisi operasional 6 kriteria; definisi PASS/FAIL/INSUFFICIENT_EVIDENCE; aturan keputusan; edge cases; contoh ID/EN; format evidence span; daftar kode rationale tertutup | Annotator + koordinator |
| 2 | `ANNOTATOR_HANDBOOK.md` | Cara kerja langkah demi langkah: membaca cerita, memberi label, mengisi evidence/rationale, aturan independensi, larangan | Annotator |
| 3 | `ANNOTATION_TEMPLATE.csv` | Template spreadsheet (UTF-8 BOM, terbuka di Excel/Sheets) — 31 kolom: confidence per kriteria (LOW/MEDIUM/HIGH), annotation_round R1/R2; berisi 2 baris `EXAMPLE-*` sebagai contoh pengisian (hapus sebelum dipakai) | Annotator |
| 4 | `ANNOTATION_PROTOCOL.md` | Alur resmi: kalibrasi 30 → (+30 bila perlu) → Round 1 independen → Round 2 re-review → adjudication; penyimpanan label individual + provenance konsensus; metrik Po/κ multiclass (PABAK multiclass per OD-10); usulan ambang (OPEN) | Koordinator + annotator |
| 5 | `ANNOTATION_QC_CHECKLIST.md` | Checklist QC per batch: kelengkapan, validitas span, konsistensi rationale, antarbahasa, duplikasi/ID, red flags, missing values | Koordinator/QC |
| 6 | `HISTORICAL_ANNOTATION_ASSESSMENT.md` | Asesmen 221 label historis: skema biner 0/1, keterbatasan provenance, distribusi terukur, kriteria retensi, apa yang bisa divalidasi vs. butuh konfirmasi | Koordinator |
| 7 | `HISTORICAL_ANNOTATION_VALIDATION_PLAN.md` | Rencana validasi: verifikasi metodologi annotator asli, inspeksi distribusi, pola mencurigakan, perbandingan dgn sampel baru, resolusi perbedaan (tanpa menimpa label) | Koordinator |
| 8 | `HISTORICAL_DATASET_INTEGRATION_SPEC.md` | Cara label historis tervalidasi masuk skema kanonik: blok terpisah `historical_labels` (biner), eligibility train-only, pencegahan leakage ke test/kalibrasi | Koordinator |

## Urutan penggunaan (workflow)

**Fase 0 — Persiapan (koordinator):**
1. Baca Task 03 §7 (kebutuhan anotasi) dan §10 (risiko).
2. Pilih 30 cerita batch kalibrasi (15 EN + 15 ID, ≥5 proyek, stratifikasi kasar — Protocol §1).
3. Salin isi cerita ke salinan `ANNOTATION_TEMPLATE.csv` (kolom identitas terisi, baris `EXAMPLE-*` dihapus).
4. Tetapkan ID annotator (A-01, A-02) dan jawab/bekukan OPEN DECISION yang memblokir (lihat bawah).

**Fase 1 — Kalibrasi:** annotator baca (1)+(2) → anotasi 30 cerita independen → QC checklist → hitung Po/κ multiclass (PABAK multiclass hanya bila OD-10 disetujui) → revisi guideline bila perlu → (opsional +30, OD-8) → ulangi hingga ambang disetujui terpenuhi.

**Fase 2 — Produksi Round 1:** bagi batch koheren-per-proyek → dua annotator bekerja independen → QC per batch.

**Fase 3 — Round 2 + Adjudication:** koordinator tandai konflik → re-review → adjudication kasus tersisa → konsensus ditulis ke struktur `final` terpisah (label individual tak tersentuh).

**Fase 4 — Jalur historis (paralel, koordinator):** jalankan `HISTORICAL_ANNOTATION_VALIDATION_PLAN.md` (V1 interview → V2–V3 komputasional → V4 overlay sampel → V5 resolusi) → putuskan integrasi menurut `HISTORICAL_DATASET_INTEGRATION_SPEC.md`.

## Keputusan metodologis yang masih OPEN (butuh persetujuan manusia)

| ID | Keputusan | Usulan di dokumen |
|---|---|---|
| OD-1 | Ambang agreement (κ/Po) untuk lulus kalibrasi | Protocol §5.3 (κ≥0.60 & Po≥0.80; n kecil = trigger tindakan, bukan klaim reliabilitas) |
| OD-2 | Apakah annotator boleh melihat story lain dalam batch untuk konteks I/S | Guideline §10 (default: teks-saja) |
| OD-3 | Mode adjudication: annotator ketiga vs diskusi terstruktur | Protocol §4 |
| OD-4 | Distribusi bahasa per annotator (dua-duanya vs split EN/ID) | Protocol §2.3 |
| OD-5 | Batas IE per kriteria/batch yang memicu review | Protocol §5.4 (usulan >25%) |
| OD-6 | Status penggunaan pilot-30: arsip / kalibrasi ulang / bagian benchmark | Protocol §1.1 & §8; Task 03 §10.9 |
| OD-7 | Pemetaan label historis biner→three-class saat konsumsi | Integration Spec §4 (1→PASS, 0→FAIL, tanpa IE) |
| OD-8 | Jumlah/pemilihan batch kalibrasi tambahan | Protocol §1.4 |
| OD-9 | Persetujuan final integrasi 221 label historis sebagai train data | Integration Spec §3–§6 |
| OD-10 | Penggunaan PABAK multiclass sebagai metrik gate selain Po+κ | Protocol §5.2 (default: Po+κ saja) |

## Validasi paket (sudah dilakukan saat penyusunan)

- Semua kolom template ≡ kolom yang disyaratkan; nilai label hanya `PASS`/`FAIL`/`INSUFFICIENT_EVIDENCE`; baris contoh memakai format evidence `start-end` yang sudah diverifikasi round-trip terhadap teksnya.
- Definisi enam kriteria saling eksklusif dengan tabel keputusan umum (Guideline §0.4, §9) — tidak ada kriteria yang mendefinisikan label yang sama.
- Konsisten dengan Task 03: tiga-kelas (IE first-class), evidence span karakter pada `original_text`, label individual tulis-sekali terpisah dari konsensus, test set bebas data historis, IE tidak pernah ditimpa.
- Konsisten dengan forensik Task 04B: 221 baris = birth `236ea51`; 116 ditimpa; 85 selamat; `annotator_a` = agregat; `annotator_b` kosong; distribusi per kriteria dihitung dari blob arsip.
- Tidak ada label historis yang dianggap ground truth di dokumen mana pun; tidak ada anotasi otomatis yang dilakukan; tidak ada file dataset/kode yang diubah.

## Yang TIDAK termasuk dalam paket ini

- Implementasi aplikasi annotasi (UI/tools) — Task berikutnya.
- Daftar cerita batch kalibrasi konkret (koordinator memilih dari korpus mentah setelah OD ditetapkan).
- Penarikan statistik agreement (dijalankan setelah Round 1 ada datanya).
