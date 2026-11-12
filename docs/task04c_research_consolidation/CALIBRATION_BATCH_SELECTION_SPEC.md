# Calibration Batch Selection Specification (v1.0)

**Target sementara:** 30 cerita — 15 ID + 15 EN — dari **≥ 5 proyek berbeda**.
**Prasyarat:** seleksi baru dilakukan **setelah Task 05** menghasilkan dataset kanonik (story_id stabil, provenance, pasangan terjemahan terverifikasi). Dokumen ini menetapkan prosedurnya, bukan ceritanya.

## 1. Candidate pool

- Pool = seluruh story kanonik yang valid (universe Task 05), **tanpa** melihat label historis atau prediksi model.
- **Inclusion:** story dengan `original_text` utuh, `story_id` valid, provenance lengkap (arsip/Task 05).
- **Exclusion:** story rusak/terpotong tanpa nilai; story yang sudah ditetapkan masuk test (kalibrasi harus di luar train/val/test — Task 03 §6; Task 04C §4); duplikat persis dalam batch kecuali sengaja diuji; story yang menuntut konteks di luar teks untuk bisa dipahami.

## 2. Stratifikasi kualitas (berbasis sinyal tekstual — BUKAN label model)

Sebar 30 cerita melintasi pola-pola berikut (kuota kasar, dihitung dari sinyal teks):

| Strata | Sinyal tekstual (contoh) | Kuota kasar |
|---|---|---:|
| Cerita sehat lengkap | peran+aksi+manfaat eksplisit, objek konkret | ~6 |
| Tanpa klausul manfaat | tidak ada "so that/sehingga" | ~4–5 (uji V) |
| Aksi majemuk | "dan juga/serta" multi-aksi | ~3–4 (uji S) |
| Preskriptif | detail UI/teknis internal | ~3–4 (uji N) |
| Kuantifier kabur | "banyak/beberapa/dll/various" | ~3–4 (uji E) |
| Dependensi/rujukan | "setelah", "tersebut", "US-x" | ~2–3 (uji I) |
| Subjektif tak terukur | "cepat/mudah/user-friendly" | ~3–4 (uji T) |
| Cerita pertanyaan/pengetahuan | "saya ingin tahu …" | ~2 (edge case) |

Kuota adalah panduan penyebaran, bukan kerangka kaku; yang diwajibkan: **setiap kriteria INVEST punya ≥ 2 cerita yang secara tekstual menyentuh pola pelanggarannya**.

## 3. Translation pairs

- Sertakan **6–8 pasangan EN–ID terverifikasi** (dari `translation_pair_id`) — untuk mengukur konsistensi antarbahasa.
- Sisanya single-language (terutama EN dari proyek yang tak punya terjemahan) — agar batch juga merepresentasikan cerita tanpa pasangan.

## 4. Reproducibility

1. Susun daftar kandidat per strata (urut `story_id`).
2. Gunakan RNG ber-seed (`random.Random(<seed>)`, seed dicatat di manifest, disarankan seed tetap per rilis dataset).
3. Pilih sesuai kuota; tulis urutan seleksi ke manifest sehingga seleksi dapat diulang byte-identik.
4. **Dilarang memilih cerita berdasarkan label model/prediksi/heuristik.** Sinyal tekstual di §2 boleh (itu bagian dari desain cakupan), tetapi keputusan akhir harus reproducible dari seed.

## 5. Replacement rules

Kandidat terpilih dapat diganti **hanya** bila: (a) terbukti duplikat/korup saat verifikasi ID; (b) melanggar batasan split (mis. proyeknya sudah penuh kuota); (c) annotator menemukan teks tak bisa dianotasi. Pengganti = kandidat berikutnya dalam urutan seeded pada strata yang sama; setiap penggantian dicatat di manifest (`replaced_from`, `reason`).

## 6. Manifest & provenance

`calibration_manifest.json` per seleksi berisi: seed, tanggal, versi dataset sumber, daftar 30 baris (`story_id`, `project_id`, `language`, `source_file/line`, `translation_pair_id`, strata), daftar pengganti + alasan, dan SHA-256 file sumber. Manifest ini yang memastikan kalibrasi **terlacak dan tidak bocor** ke train/val/test.

## 7. Blinding

Manifest seleksi dibuat **sebelum** kontak dgn label historis/model dan tidak menyertakan label apa pun. Annotator menerima cerita tanpa tahu strata/kriteria yang diuji.

## 8. Verifikasi

Setiap `story_id` di manifest harus ada di dataset kanonik (Task 05) dengan `original_text` byte-identik terhadap sumbernya. Verifikasi otomatis dijalankan saat batch dibagikan.

## 9. Alternatif bila 30 tidak praktis

| Alternatif | Komposisi | Keterbatasan |
|---|---|---|
| 20 cerita | 10 ID + 10 EN, ≥ 4 proyek, semua strata dipertahankan dgn kuota lebih kecil | cakupan per pola menipis; κ/Po ber-IC lebih lebar |
| 12 cerita (minimum) | 6 ID + 6 EN, ≥ 3 proyek | hanya menguji operasionalitas dasar; tidak cukup untuk menilai reliabilitas per kriteria — guideline perlu uji lanjutan di produksi |

Penurunan didokumentasikan + alasan; ambang agreement tetap **[OPEN DECISION OD-1]**.
