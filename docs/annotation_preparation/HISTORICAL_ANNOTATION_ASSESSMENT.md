# Historical Annotation Assessment — Family B (221 baris, commit `236ea51`)

**Status:** Dokumen asesmen (Task 04). Tidak mengubah data apa pun. Dasar: `FAMILY_B_MANUAL_ANNOTATION_RECOVERY_AUDIT.md` (Task 04B), snapshot arsip `docs/dataset_archives/family_b/pre_writeback_236ea51/`.
**Prinsip:** 221 label historis adalah **kandidat anotasi manusia** — bukan ground truth, dan bukan pula sampah yang boleh dibuang. Tugas dokumen ini: memetakan apa yang diketahui, apa yang dapat divalidasi, dan apa yang butuh konfirmasi annotator asli.

---

## 1. Skema anotasi historis (binary 0/1)

| Aspek | Nilai historis |
|---|---|
| Kolom label | `y_I, y_N, y_V, y_E, y_S, y_T` — **biner** `0/1` (di sebagian file tertulis float `0.0/1.0`) |
| Makna konvensional | `1` ≈ kriteria terpenuhi (asumsi kerja) — **makna `0` belum diketahui pasti**: bisa berarti FAIL (pelanggaran terverifikasi), INSUFFICIENT_EVIDENCE (kriteria tak dapat dinilai), atau campuran keduanya; tidak ada kategori ketiga eksplisit (IE tidak dapat direpresentasikan sebagai kolom tersendiri). Konsekuensi langsungnya: pemetaan `0 → FAIL` dibatasi — lihat `HISTORICAL_DATASET_INTEGRATION_SPEC.md` §4 |
| Kolom anotator | `annotator_a` = terisi pada baris berlabel; **terbukti secara forensik = agregat all-six-pass** (aturan `annotator_a == [semua 6 label = 1]` berlaku di 108/108 EN + 113/113 ID baris birth — 0 pengecualian di seluruh blob historis). `annotator_b` **tidak pernah terisi** di versi mana pun |
| Metadata | **Tidak ada**: tanpa evidence span, tanpa rationale, tanpa timestamp, tanpa ID annotator, tanpa catatan ronde |
| Cakupan | 221 baris berlabel lengkap (108 EN + 113 ID) dari total 1,004/1,009 baris; sisanya kosong/NaN |
| Format berkas | CSV heterogen: campuran header 15/16 kolom, encoding utf-8/utf-8-sig/cp1252, nilai float dan int bercampur |

Karena `annotator_a` adalah agregat, **sinyal informasi historis yang sesungguhnya hanya ada di enam kolom `y_*`** — dan sinyal itu tidak dapat dipisahkan dari label tunggal tanpa nama.

## 2. Keterbatasan provenance saat ini

1. **Identitas annotator tidak diketahui.** Commit `236ea51` dibuat oleh `danielpurnomo`, tetapi Git-authorship ≠ kepenulisan label (label bisa diimpor dari pekerjaan luar).
2. **Tidak ada bukti proses manual.** Tidak ada catatan sesi, pedoman yang dirujuk, atau kwitansi kerja. Pedoman anotasi (`pedoman_anotasi_invest.md`) sudah ada sejak 2026-10-19 (sebelum label), tetapi kepatuhannya tak terdokumentasi.
3. **`annotator_a` bermakna ganda.** Bisa jadi penilaian keseluruhan manusia ("story ini layak/tidak") yang kebetulan konsisten dengan semua-enam-1 — atau hasil alat. Keduanya kompatibel dengan data.
4. **Dua snapshot pra-model berbeda.** `dataset-*-label` (earlier-round, ~109/112 baris) vs. `dataset-*-label-final` birth (108/113) **berbeda nilai pada 24 baris** (88/104 + 93/101 agreement ternormalisasi) — menunjukkan ada pass sunting kedua sebelum commit; alasan perubahan tidak terdokumentasi.
5. **Kesepakatan lintas-bahasa 100%.** Untuk 81 pasangan EN↔ID pada birth state, keenam label **identik sempurna** (0 diskrepansi per kriteria) — pola yang konsisten dengan propagasi/sinkronisasi label antar-bahasa, bukan dua penilaian independen. Ini **mengurangi** nilai bukti "dua penilaian" tetapi tidak membuktikan ketiadaan kerja manusia.
6. **Model-assisted expansion datang 29,5 jam kemudian** (`e23701c`) dan menimpa 116 dari 221 baris — label pra-model hanya aman di blob `236ea51` (sudah diarsipkan byte-exact di `docs/dataset_archives/family_b/`).
7. **Makna `0` tidak terkonfirmasi.** Tidak ada dokumentasi apakah `0` berarti FAIL, INSUFFICIENT_EVIDENCE, atau campuran keduanya — ini membatasi langsung pemetaan label historis ke skema tiga-kelas baru (Integration Spec §4).

## 3. Distribusi label historis (terukur, birth state `236ea51`)

Dari 221 baris berlabel (hitungan langsung dari blob arsip):

| Kriteria | EN (n=108) `1` | EN `0` | ID (n=113) `1` | ID `0` | Gabungan %`1` |
|---|---:|---:|---:|---:|---:|
| y_I | 60 | 48 | 67 | 46 | 57.5% |
| y_N | 100 | 8 | 102 | 11 | 91.4% |
| y_V | 106 | 2 | 111 | 2 | 98.2% |
| y_E | 75 | 33 | 83 | 30 | 71.5% |
| y_S | 74 | 34 | 79 | 34 | 69.2% |
| y_T | 71 | 37 | 81 | 32 | 68.8% |

Pola yang layak dicatat (untuk validasi, bukan vonis):
- **y_V hampir selalu 1** (hanya 4/221 = 1.8% `0`) → sinyal operasional V yang sangat longgar ATAU korpus memang sehat — tidak bisa dibedakan tanpa konfirmasi.
- **y_I paling banyak 0** (~42%) → konsisten dengan banyak cerita berteknikal/masih dependen; pola ini justru terlihat "berpikir kritis".
- **Keseimbangan EN vs ID hampir identik** untuk setiap kriteria (selisih ≤ 3.9 poin) — selaras dengan propagasi label lintas-bahasa.
- `annotator_a == all-pass` 100% di kedua bahasa.

### 3.1 Lima baris badcamp-EN earlier-round — status terverifikasi (jangan dicampur ke hitungan 221)

Verifikasi komputasional terhadap blob `236ea51` (baris berlabel lengkap di `dataset-english-label/badcamp-english.csv`):

1. **Lima baris tersebut adalah** `badcamp_001`–`badcamp_005`, keenam kriteria semuanya `1` (all-pass), dalam `dataset-english-label/badcamp-english.csv` @ `236ea51` (blob `974e38e437`).
2. **Story-nya sudah termasuk dalam 221** — bukan tambahan story: `badcamp_001`–`005` hadir dan **berlabel** di sisi ID pada birth state (`dataset-indo-label-final/badcamp.csv`, 15 baris berlabel — termasuk kelima source_id ini, semuanya all-pass). `dataset-eng-label-final` saat birth **tidak memiliki** file badcamp (file itu baru muncul di `e23701c`).
3. Kesimpulan hitungan: **221 tetap 221** (108 EN + 113 ID birth records; 221 story berlabel). Kelima baris EN adalah **5 rekord label bahasa-Inggris tambahan** untuk story yang sudah terhitung via pasangan ID-nya — bukan 5 story baru, dan tidak boleh dijumlahkan ke 221.
4. **Survival di HEAD:** `dataset-english-label/badcamp-english.csv` @ HEAD masih memuat kelima label tersebut **identik** dengan birth state (lolos dari writeback tanpa perubahan nilai).
5. Status: rekord tambahan dengan provenance sama seperti 221 (kandidat, tanpa metadata) — penanganannya mengikuti `HISTORICAL_DATASET_INTEGRATION_SPEC.md` §1 (baris terpisah, status menunggu verifikasi record-level).

## 4. Kriteria mempertahankan label historis (retention)

Label historis **dipertahankan sebagai kandidat** dan boleh naik kelas bila SEMUA syarat berikut terpenuhi:

1. **R1 — Baris berasal dari state pra-model yang terverifikasi**: baris teridentifikasi di blob `236ea51` (atau file yang tak tersentuh writeback, 85 baris). Kelas A/A'/A'' pada Task 04B.
2. **R2 — Konfirmasi annotator** (lihat §5) menyatakan baris tersebut dikerjakan manual olehnya, dengan pemahaman kriteria yang dijelaskan kembali.
3. **R3 — Lolos pemeriksaan komputasional** (§4 Validation Plan): distribusi wajar, tidak termasuk pola mencurigakan berat.
4. **R4 — Persetujuan integrasi**: keputusan **[OPEN DECISION OD-7/OD-9]** bahwa label biner boleh dipakai (train-only) dan bagaimana pemetaannya.

Tanpa R2, semua 221 baris tetap berstatus "kandidat tanpa provenance penuh" — boleh dipertahankan sebagai data pembanding, tidak boleh jadi ground truth.

## 5. Yang dapat divalidasi secara komputasional (tanpa annotator)

| Pemeriksaan | Cara | Sudah diketahui |
|---|---|---|
| Kelengkapan & bineritas label | parse blob arsip | ✅ 221 baris, semua 0/1 |
| Konsistensi `annotator_a` | banding dgn all-pass | ✅ 100% (semua versi) |
| Kesepakatan lintas-bahasa | join `source_id` EN↔ID | ✅ 81/81 pasangan identik (pola propagasi) |
| Kesepakatan dua snapshot pra-model | earlier-round vs final-birth | ✅ 181/205 identik; 24 beda nilai |
| Distribusi per kriteria/bahasa | hitung frekuensi | ✅ tabel §3 |
| Outlier label | cerita dgn kombinasi label tidak lazim | dapat dihitung |
| Kesepakatan dgn snapshot baru (sampling) | overlay ke batch anotasi baru | rencana — lihat Validation Plan |
| Kedalaman berbasis pola teks | cek apakah `0` pada y_N berbarengan dengan kata preskriptif di teks, dst. | dapat dihitung (indikatif, bukan pembuktian) |

## 6. Yang membutuhkan konfirmasi dari annotator asli

1. **Apakah 221 baris tersebut dikerjakan manual** olehnya (dan kapan/berapa lama)?
2. **Definisi yang ia pakai** untuk tiap kriteria — apakah sesuai `pedoman_anotasi_invest.md` atau versi pribadi?
3. **Status `annotator_a`**: penilaian keseluruhan mandiri, atau dihitung dari enam label?
4. **Alasan 24 perbedaan nilai** antara dua snapshot pra-model (revisi sadar vs. salah salin)?
5. **Status sinkronisasi EN↔ID 100%**: label dikerjakan sekali lalu disalin, atau dinilai dua kali dengan hasil identik?
6. **Apakah ada baris tambahan** yang dikerjakan manual tetapi tidak pernah di-commit (Task 04B menetapkan 221 adalah batas yang bisa dibuktikan Git, bukan batas pasti kerja manual)?
7. **Izin penggunaan**: apakah labelnya boleh dipakai untuk benchmark (attribution, lisensi)?

## 7. Pembedaan historis vs model-expanded

| | Historical (birth `236ea51`) | Model-expanded (pasca `e23701c`) |
|---|---|---|
| Baris berlabel | 221 | ~959 (+733 isi, 116 timpa, 69 baru) |
| Asal nilai | pra-alat (tidak ada model di repo saat commit) | `coba`/`coba 2.py` + model bundle di commit yang sama |
| Kelas Task 04B | A (85 selamat di HEAD), A' (116 ditimpa — nilai asli dari blob), A'' (20 identik) | C |
| Kelayakan | **kandidat** — butuh R1–R4 | **bukan ground truth**; hanya pembanding pasca-hoc |

Pembedaan teknis di level data: label historis **biner 0/1** dan disimpan terpisah (`historical_labels` + `provenance_class`), tidak pernah digabung ke kolom `final` tiga-kelas — rinciannya di `HISTORICAL_DATASET_INTEGRATION_SPEC.md`.

---

## 8. Kesimpulan asesmen

- 221 label **layak dipertahankan** sebagai kandidat berprovenance penuh (blob terverifikasi, arsip ada) — dengan status "potential human annotation, provenance incompleteness".
- Tidak ada dasar untuk menganggapnya ground truth, dan tidak ada dasar untuk membuangnya.
- Jalur ke depan: validasi komputasional (sudah sebagian besar selesai) → konfirmasi annotator (§6) → keputusan integrasi (OD-7/OD-9) → hanya training-eligible, tanpa test.
