# Historical Annotation Validation Plan — Family B (221 baris pra-model)

**Status:** Rencana (Task 04). Tidak mengeksekusi anotasi apa pun; tidak menimpa/mengubah label historis.
**Objek:** 221 baris berlabel pada blob `236ea51` (arsip `docs/dataset_archives/family_b/pre_writeback_236ea51/`).
**Tujuan:** memutuskan — dengan bukti — baris historis mana yang layak diintegrasikan (kelas apa), mana yang perlu re-annotasi selektif, mana yang hanya jadi pembanding.

---

## Fase V1 — Verifikasi metodologi annotator asli (interview terstruktur)

Tanyakan tertulis kepada annotator asli (daftar lengkap pertanyaan di `HISTORICAL_ANNOTATION_ASSESSMENT.md` §6). Keluaran yang dibutuhkan:

1. Pernyataan tertulis: baris mana (jika bisa diingat) / apakah seluruh 221 dikerjakan manual.
2. Definisi yang ia pakai per kriteria + apakah ia membaca `pedoman_anotasi_invest.md`.
3. Kapan sesi dilakukan, berapa lama, dengan alat apa (Excel? langsung CSV?).
4. Status `annotator_a` (verdict keseluruhan vs. turunan).
5. Penjelasan 24 perbedaan nilai antara dua snapshot pra-model.
6. Penjelasan kesepakatan EN↔ID 100% (dikerjakan sekali & disalin? atau dua pass?).
7. Persetujuan penggunaan (attribusi + lisensi).

**Gate:** tanpa jawaban (1) dan (7), seluruh 221 label tetap berstatus Class-B "potential" dan tidak boleh diintegrasikan sebagai label.

## Fase V2 — Inspeksi distribusi per kriteria (komputasional; sebagian selesai)

Nilai terukur (lihat tabel lengkap di Assessment §3):

| Kriteria | EN `1`/`0` (n=108) | ID `1`/`0` (n=113) | Gabungan `1` |
|---|---|---|---:|
| y_I | 60/48 | 67/46 | 57.5% |
| y_N | 100/8 | 102/11 | 91.4% |
| y_V | 106/2 | 111/2 | 98.2% |
| y_E | 75/33 | 83/30 | 71.5% |
| y_S | 74/34 | 79/34 | 69.2% |
| y_T | 71/37 | 81/32 | 68.8% |

Pemeriksaan yang harus dijalankan (skrip read-only, tanpa mengubah data):

1. **Distribusi vs. ukuran kelas:** y_V 98.2% positif → uji: apakah cerita berlabel `y_V=0` memang tidak punya klausul manfaat (cek tekstual), dan apakah cerita `y_V=1` tanpa "so that" punya manfaat tersurat (sampling manual).
2. **Konsistensi antar-bahasa:** ✅ 81/81 pasangan identik — dicatat sebagai pola propagasi, bukan bukti dua penilaian.
3. **Konsistensi dua snapshot:** 24 baris berbeda nilai antara earlier-round dan final-birth → identifikasi barisnya dan minta penjelasan (V1).
4. **Konsistensi internal baris:** baris `y_I=0` seharusnya punya indikator dependensi di teks; baris `y_N=0` indikator preskriptif; dst. → hitung korelasi label ↔ kehadiran pola teks (indikatif).
5. **Deteksi pola mencurigakan** (lihat Fase V3).

## Fase V3 — Pola mencurigakan & inkonsistensi

| Pola | Ciri | Tindakan |
|---|---|---|
| Label `1` seragam pada kriteria (y_V 98%) | distribusi sangat timpang | sampling manual 20 baris; bila semua jelas sah → ok; bila tidak → tandai kriteria "kurang dapat diandalkan" |
| Propagasi lintas-bahasa 100% | 81/81 identik | tidak fatal, tapi label EN dan ID **bukan** dua penilaian independen — jangan dihitung sebagai dua suara |
| Perbedaan antar-snapshot 24 baris | nilai berubah tanpa dokumentasi | minta penjelasan (V1); baris yang berubah diberi flag `SNAPSHOT-DISAGREE` |
| Label cocok persis dgn resep perturbasi/kata pola model | mis. pola "dan juga … serta" selalu `y_S=0` | wajar bila cerita memang begitu; bahaya bila label mengikuti pola regex alih-alih makna — sampling |
| Baris all-pass `annotator_a=1` melimpah | cek frekuensi all-pass vs. sebaran | bandingkan dgn distribusi 6-kriteria |
| Cerita duplikat dgn label berbeda | join teks ternormalisasi | flag `DUP-DISAGREE` |

## Fase V4 — Historical validation batch (terpisah dari batch kalibrasi)

**V4 adalah batch tersendiri, independen dari batch kalibrasi 30 cerita baru (Protocol §1).** Mekanismenya identik (guideline v1.1, template sama, dua annotator independen, dua ronde bila perlu) tetapi batch, jadwal, dan statistiknya **dipisahkan** — statistik overlay historis tidak boleh dicampur ke statistik kalibrasi guideline, dan sebaliknya.

### V4.1 Desain sampling — target 60 baris unik dari universe 221

Semua angka di bawah terukur dari blob `236ea51`:

| Komponen | Jumlah | Catatan |
|---|---:|---|
| Wajib: semua baris `SNAPSHOT-DISAGREE` (earlier-round ≠ final-birth) | **24** | 16 EN + 8 ID |
| Wajib: semua baris `y_V=0` | **4** | 2 EN + 2 ID (`rac_dam_003`, `rac_dam_004` di kedua bahasa) — jumlahnya kecil sehingga **seluruhnya diambil** |
| Overlap dua set wajib | 0 | union = **28 baris** |
| Pengisi acak deterministik (urut `language, source_id`) dari sisa universe | **32** | sampai tepat 60 baris unik |
| **Total sampel** | **60 unik** | dari universe 221 |

**Strata per kriteria mengikuti jumlah label yang benar-benar tersedia** (baris `y_c=0` di universe 221):

| Kriteria | Baris `y_c=0` (EN/ID) | Tercakup dalam sampel 60 |
|---|---|---:|
| y_I | 94 (48/46) | 27 |
| y_N | 19 (8/11) | 3 |
| y_V | **4 (2/2)** | **4/4 — semua** |
| y_E | 63 (33/30) | 21 |
| y_S | 68 (34/34) | 16 |
| y_T | 69 (37/32) | 24 |
| all-pass (6×`1`) | 65 | 14 |

**Overlap antar-strata terdokumentasi:** satu baris bisa masuk beberapa strata-0 sekaligus (distribusi baris sampel berdasarkan jumlah strata-0 yang dicakup: 1 strata ×19, 2 strata ×10, 3 strata ×12, 4 strata ×5) — strata **bukan partisi**; pelaporan cakupan per kriteria tetap dilakukan terpisah. Label historis **tidak diperlihatkan** ke annotator.

### V4.2 Pelaksanaan

1. 60 baris disusun sebagai batch anotasi (kolom identitas dari arsip; baris `EXAMPLE-*` tidak ada).
2. A-01 dan A-02 menganotasi independen mengikuti aturan Protocol §2 (independensi dan penyimpanan yang sama).
3. Setelah Round 1, koordinator membandingkan (overlay, read-only):
   - label historis biner `{0,1}` dipetakan sementara `1→PASS`, `0→FAIL` **hanya untuk analisis kesepakatan** — pemetaan ini bukan pengakuan makna `0` (lihat Integration Spec §4);
   - hitung agreement per kriteria; simpan matriks.

### V4.3 Interpretasi — semantic concordance, bukan bukti provenance

- Agreement tinggi antara label historis dan anotasi baru hanya menunjukkan **kesesuaian semantik (semantic concordance)** — bahwa dua skema membaca cerita yang sama dengan cara yang mirip. Ia **bukan bukti provenance manusia**; provenance tetap hanya bisa dipastikan lewat konfirmasi annotator asli (Fase V1).
- Karena itu, kesepakatan (mis. tingkat ≥80% per kriteria) **tidak pernah** menjadi dasar tunggal pengesahan kelas provenance — kenaikan kelas menuntut konfirmasi V1 + gate G1–G3 (Integration Spec §3); kesepakatan hanya bukti pendukung (G4).
- Agreement rendah → dua kemungkinan: definisi lama berbeda dari pedoman baru, atau label tidak manual → jelaskan via V1; tanpa penjelasan, kelas turun menjadi B/D.
- **Tidak ada label historis yang diubah** dalam proses ini — overlay hanya untuk laporan.

## Fase V5 — Pencatatan perbedaan historis (terpisah dari adjudication baru)

**Adjudication baru (Protocol §4) hanya menyelesaikan konflik antara A-01 dan A-02** pada anotasi baru. Perbedaan yang bersifat historis **tidak dikirim ke adjudication baru** dan dicatat terpisah:

1. **`SNAPSHOT-DISAGREE` (24 baris)** — perbedaan earlier-round vs final-birth: dicatat sebagai temuan validasi historis dan ditanyakan ke annotator asli (Fase V1 item 5). Bila barisnya ikut re-annotasi (V6), anotasi baru menjadi final untuk baris tersebut dan label historis tetap tersimpan dengan flag `SNAPSHOT-DISAGREE`.
2. **Perbedaan historis vs anotasi baru (hasil V4)** — dicatat sebagai statistik semantic concordance + daftar `HISTORICAL-NEW-DIFF` per story_id. Tidak ada "adjudication" yang menggabungkan label historis dengan label baru.
3. Bila baris historis dianotasi ulang penuh (V6), anotasi baru yang menjadi `final` untuk baris tersebut; label historis tetap tersimpan di blok `historical_labels` dengan flag `SUPERSEDED_BY_NEW_ANNOTATION`.
4. Statistik resolusi dilaporkan (berapa historis sejalan / berbeda / tak diputuskan) — sebagai laporan validasi, bukan keputusan label.

## Fase V6 — Re-annotasi selektif (bukan re-annotasi penuh)

Prioritas re-annotasi penuh dua-annotator (di luar sampel V4):
1. Semua baris `SNAPSHOT-DISAGREE` (maks 24).
2. Baris pada proyek yang terpilih sebagai **test set** — karena historis tidak boleh masuk test, baris test-eligible harus berlabel baru.
3. Baris dengan pola mencurigakan Fase V3 yang tidak terjelaskan.
Sisanya (mayoritas 221) tidak wajib re-annotasi — cukup validasi V1–V4.

## Aturan mutlak

- Label historis **tidak pernah ditimpa, tidak pernah digabung** ke file anotasi baru.
- Semua perbandingan dilakukan sebagai overlay read-only.
- Keputusan integrasi final = **[OPEN DECISION OD-7/OD-9]** setelah Fase V1–V5.
