# Documentation Alignment Report (Task 04C)

**Tujuan:** memetakan dokumen mana yang mendefinisikan scope riset aktif, mana yang catatan historis, dan menutup kontradiksi antara desain lama (4 evaluator) dan scope baru (3 evaluator) — **tanpa menulis ulang bukti historis**.

## 1. Dokumen yang diperiksa

| Dokumen | Peran | Status | Tindakan |
|---|---|---|---|
| `BILINGUAL_DATASET_RECONSTRUCTION_SPEC.md` (Task 03) | **Mendefinisikan scope riset** (evaluator, skema, split) | Kontradiksi dgn scope baru (4 evaluator) | **Banner scope ditambahkan** (header, §8) — isi historis dipertahankan — isi historis dipertahankan |
| `INVEST_DATASET_AUDIT.md`, `TXT_CORPUS_DISCOVERY_AUDIT.md`, audit forensik (Task 01/02/04A/04B) | **Catatan historis** (bukti forensik) | Sah — tidak kontradiksi dgn scope baru | Tidak diubah; tetap sumber kebenaran forensik |
| Task 04 package (`annotation_preparation/`) | **Mendefinisikan proses anotasi aktif** | Sudah direvisi (guideline v1.1, protocol v1.1, template 31 kolom) | Rujukan silang diperbarui saat revisi terarah sebelumnya |
| `docs/arsitektur_dan_integrasi.md`, `docs/laporan_proyek.md`, `docs/srs_spesifikasi_kebutuhan.md`, `docs/pitch_deck.md` | **Deskripsi implementasi/promosi historis** | Menyebut "ML Evaluator"/pipeline lama | **Tidak diubah** — catatan implementasi historis; dipetakan di §3 |
| `POST_MERGE_DEPLOYMENT_AUDIT.md`, audit deployment | Catatan operasional | Tidak relevan dgn scope riset | Tidak diubah |
| `ai-engine/benchmarks/evaluate.py`, `invest_annotation_experiment.py` | Implementasi benchmark lama (4 kasus; κ/PABAK biner) | Tidak dipakai benchmark baru | Tidak diubah; status "legacy, bukan alat benchmark aktif" |

## 2. Peta: implementasi vs desain riset vs deferred

| Komponen | Implementasi saat ini | Desain riset aktif (Task 04C) | Deferred |
|---|---|---|---|
| Rule-based INVEST | Ada (`nlp_stage1`, lexicon; fallback di `invest_ml_service`) | **Evaluator A** (dibekukan aturan IE-nya sebelum benchmark) | — |
| Traditional ML | Bundle lama tidak ter-load di produksi; training script legacy | **Evaluator B** (TF-IDF + LogReg/SVM, OvR) — di atas data anotasi baru | — |
| LLM | `nlp_stage2` live (mock/Groq) untuk **rewrite** | **Evaluator C** (klasifikasi 3-label, prompt terpisah) | — |
| Pretrained Encoder | **Tidak ada** (flag e5 False) | **Bukan evaluator** — future work | Fine-tuning & benchmark encoder |
| Recommendation engine | `nlp_stage2` `ai_rewrite` | **Bukan evaluator** — di luar benchmark | Benchmark kualitas rekomendasi |
| Dataset | `invest_corpus_1000` (sintetis) + raw TXT | Dataset kanonik baru (Task 05) dgn benchmark 120-ceiling | Full-corpus annotation |

## 3. Register kontradiksi & resolusi

| # | Kontradiksi | Lokasi | Resolusi |
|---|---|---|---|
| K1 | "four independent evaluators" vs 3 evaluator | Task 03 header/§8/§10; BILINGUAL spec L5/L19/L262 | Banner Task 04C ditambahkan ke Task 03 (header, §8, §10.3); spesifikasi baru `THREE_EVALUATOR_BENCHMARK_SPEC.md` menjadi acuan aktif. Teks lama dipertahankan sebagai catatan desain saat itu. |
| K2 | Rekomendasi volume ~300–1.000 story vs ceiling 120 | `INVEST_DATASET_AUDIT.md` §8 (rekomendasi #3) — **catatan audit historis, tidak dibanner** | Superseded oleh Task 04C: target sementara 120 ceiling (`ANNOTATION_WORKLOAD_PLAN.md`); rekomendasi 300–1.000 tetap berlaku sebagai rekomendasi jangka panjang bila kapasitas terbukti. |
| K3 | "ML Evaluator" pada pipeline produksi lama vs evaluator ML benchmark | `docs/arsitektur_dan_integrasi.md` §140, `laporan_proyek.md` | Dipertahankan sebagai deskripsi implementasi historis; laporan benchmark baru memakai terminologi A/B/C. |
| K4 | PABAK biner vs 3 kelas | Protocol v1.1 §5.2 (sudah diperbaiki); `invest_annotation_experiment.py` (legacy, biner) | Protocol memakai Po + κ multiclass (PABAK multiclass = OD-10); skrip legacy tidak dipakai benchmark baru. |
| K5 | Pilot-30 historis: referensi vs kalibrasi | Task 03 §7.9 / OD-6 | Opsi terdefinisi (arsip/kalibrasi ulang/benchmark) — Protocol §8; belum diputuskan. |

## 4. Sisa ketidakselarasan yang disengaja (tidak diperbaiki di sini)

- Deliverable lama di dokumen audit yang menyinggung "4 evaluator" dibiarkan apa adanya (catatan historis).
- `docs/mockup_data.md`, `pitch_deck.md` — materi promosi; di luar scope dokumentasi riset aktif.
- Jika suatu saat Task 03 ditulis ulang menyeluruh, banner K1 harus dilebur ke teks utama — bukan ditumpuk lagi. K2 tertangani lewat changelog, tanpa banner di dokumen audit.

## 5. Verifikasi akhir

- Semua dokumen Task 04C konsisten menyebut **3 evaluator aktif** (A/B/C); encoder selalu berlabel *removed/future work*; recommendation engine selalu *bukan evaluator*; alokasi 120 selalu berlabel *provisional ceiling*; data historis selalu *isolated*.
- Referensi silang diperiksa: Protocol v1.1 (§1, §2, §4, §5.2, §8), Task 03 (§3, §6, §6.1, §7.9, §10), Guideline v1.1, Handbook, QC — tidak ada nomor section yang menunjuk bagian yang sudah bergeser.
