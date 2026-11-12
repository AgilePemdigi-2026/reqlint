# Annotation Protocol — ReqLint INVEST (v1.1-draft)

**Peran:** Koordinator (perancang batch, QC, statistik — bukan annotator utama), Annotator A-01, Annotator A-02.
**Prinsip induk:** independensi penuh di Round 1; label individual **tidak pernah** ditimpa; konsensus hanya menghasilkan kolom terpisah; semua keputusan metodologis yang belum disetujui ditandai **[OPEN DECISION]**.
**Registry lengkap keputusan terbuka:** tabel §8 (protokol) + `README.md` folder ini.

---

## 1. Fase kalibrasi (pilot 30)

1. **Batch kalibrasi = 30 User Story baru** yang dipilih koordinator dari korpus mentah (Task 02) dengan komposisi: 15 EN + 15 ID, mencakup ≥ 5 proyek berbeda, dan **stratifikasi kasar** cerita yang tampak sehat vs. bermasalah (target: minimal 5 cerita per "kriteria bermasalah" berbeda agar tiap kriteria punya contoh FAIL). Cerita dengan pasangan terjemahan disertakan bila tersedia, agar konsistensi antarbahasa dapat diuji.
   - Pilot-30 historis (`invest_pilot_30_annotated.json`) **tidak digunakan sebagai batch kalibrasi** — statusnya referensi/arsip. Penggunaan ulangnya: **[OPEN DECISION OD-6]** (opsi arsip / kalibrasi ulang / bagian benchmark — lihat §8).
2. Kedua annotator membaca `INVEST_ANNOTATION_GUIDELINE.md` + `ANNOTATOR_HANDBOOK.md`, lalu menganotasi 30 cerita **secara independen** (Round 1) memakai template.
3. Koordinator menghitung agreement per kriteria per bahasa (observed agreement + Cohen's κ, §5) dan mengumpulkan semua `notes` berlabel `POLA-BARU:`.
4. **Revisi guideline (saat ini v1.1-draft)** untuk pola ambigu yang ditemukan. Bila revisi material, uji revisi dengan **batch tambahan 30 cerita** (prosedur sama): **[OPEN DECISION OD-8]** — jumlah dan pemilihannya.
5. Kalibrasi dinyatakan lulus hanya setelah ambang agreement disetujui terpenuhi (**[OPEN DECISION OD-1]**; usulan di §5.3). Label Round 1 kalibrasi **tidak** menjadi data benchmark — fungsinya validasi guideline & annotator.
6. **Batas ukuran sampel (baca dulu):** 30 cerita adalah **pilot operasional** — tujuannya menguji keterbacaan guideline, menemukan pola ketidaksepakatan, dan mengkalibrasi alur kerja. Dengan n=30, estimasi κ memiliki ketidakpastian besar (interval kepercayaan lebar), sehingga hasil kalibrasi **bukan** dasar statistik yang kuat untuk klaim reliabilitas annotator — angka dipakai sebagai **trigger tindakan** (revisi guideline / tambah batch), bukan sebagai vonis reliabilitas.

## 2. Round 1 — anotasi independen

1. Koordinator membagi batch produksi menjadi **batch koheren per proyek** (story satu proyek tidak dipecah antar-annotator pada file berbeda) dengan ukuran ± 20–30 cerita.
2. Kedua annotator menganotasi **seluruh batch yang sama** secara independen, masing-masing pada filenya sendiri (`ANNOTATION_TEMPLATE_A-01.csv`, `ANNOTATION_TEMPLATE_A-02.csv`).
3. Distribusi bahasa per annotator: **[OPEN DECISION OD-4]** — konsekuensi tiap opsi:
   - **Opsi (a)** — kedua annotator menilai **kedua bahasa** untuk semua data: memungkinkan analisis konsistensi antarbahasa dan cek ganda penuh; biaya anotasi 2×.
   - **Opsi (b)** — split EN/ID **hanya untuk train/validation**: penghematan kapasitas, dengan **konsekuensi yang wajib dicatat sebagai keterbatasan**: inter-annotator agreement untuk data tersebut hanya intra-bahasa (perbedaan kualitas antarbahasa tidak terdeteksi oleh dua penilaian independen).
   - **Yang wajib apa pun opsinya:** **test set dan calibration set selalu dinilai kedua annotator pada kedua bahasa** — gate kualitas benchmark tidak boleh di-split.
4. Tidak ada komunikasi substansi antar-annotator (lihat Handbook §2).
5. Label individual disimpan apa adanya; **tidak ada penggabungan file** selain untuk perhitungan agreement oleh koordinator.

## 3. Round 2 — re-review kasus tidak sepakat

1. Koordinator menggabungkan (read-only) kedua file dan menandai **per kriteria** semua sel yang labelnya berbeda antar-annotator (contoh: A-01 `FAIL`, A-02 `IE` pada `valuable` story X). Kasus sepakat tidak disentuh.
2. Setiap annotator menerima daftar konflik miliknya **tanpa melihat label pasangannya** dan mereview ulang hanya kriteria-kriteria konflik tersebut, lalu mengumpulkan **Round 2** pada file terpisah (`*_R2.csv`). Label Round 1 tidak diubah — versi Round 2 adalah record baru.
3. Setelah Round 2, koordinator menghitung **dua ukuran yang berbeda** (jangan dicampur):
   - **Round 1 agreement** — agreement pada seluruh data berdasarkan label Round 1 (baseline sebelum review).
   - **Post-review agreement** — agreement pada dataset hibrida: kriteria yang **direview** memakai label **Round 2**; kriteria yang **tidak direview** memakai label **Round 1** (karena sepakat sejak awal).
4. Tambahkan metrik **tingkat penyelesaian konflik**: jumlah dan persentase konflik Round 1 yang menjadi sepakat di Round 2, per kriteria dan per bahasa. Interpretasi: tingkat penyelesaian rendah = konflik substantif (bukan salah baca) → kandidat adjudication banyak dan guideline perlu ditinjau; tingkat penyelesaian tinggi → sebagian besar konflik bersifat administratif/persepsi sekilas.
5. Kasus yang tetap tidak sepakat setelah Round 2 masuk **adjudication** (§4).

## 4. Adjudication

1. Mode: **[OPEN DECISION OD-3]** — opsi (a) **annotator ketiga** (A-03, baru, buta terhadap kedua label) menilai cerita-kriteria konflik, atau (b) **diskusi terstruktur** difasilitasi koordinator dengan aturan ketat: kedua annotator menyampaikan evidence + rationale masing-masing sebelum melihat label lawan, lalu usulan label bersama.
2. Hasil adjudication dicatat sebagai `final_source = adjudicated` dengan keputusan final per kriteria; label individual kedua ronde **tetap tersimpan utuh** di file individual.
3. Konsensus (kasus sepakat) dicatat sebagai `final_source = consensus`; **provenance konsensus dibedakan** — lihat §6.3.
4. Bila adjudication menghasilkan `INSUFFICIENT_EVIDENCE`, itu adalah hasil final yang sah — IE tidak boleh "diangkat" menjadi PASS demi kelengkapan data.

## 5. Agreement: metrik utama dan pelaporan

### 5.1 Metrik utama (per kriteria, per bahasa, per ronde)

- **Observed agreement (Po)** = proporsi cerita yang dilabeli sama oleh kedua annotator.
- **Cohen's κ multiclass** = (Po − Pe) / (1 − Pe), dengan Pe = kesepakatan kebetulan dari distribusi marginal kedua annotator pada tabel k×k (k = 3: PASS/FAIL/INSUFFICIENT_EVIDENCE). Ini **metrik utama** bersama Po.

### 5.2 PABAK — status dan batasan

- Rumus `PABAK = 2·Po − 1` adalah **bentuk biner (k=2)**. ReqLint memakai **tiga kelas nominal**; rumus biner tersebut **tidak boleh** dipakai sebagai "PABAK tiga kelas".
- **Generalisasi multiclass** (dua rater, k kategori nominal) yang dikenal: **PABAK(k) = (k·Po − 1) / (k − 1)** — untuk k=2 tepat kembali ke 2·Po−1. Definisi: kesepakatan yang dikoreksi terhadap asumsi kesepakatan-kebetulan uniform 1/k. **Asumsi/asumsi-asumsinya:** dua rater, kategori nominal, marginal dianggap uniform sebagai baseline koreksi; ia mengabaikan pola diskrepansi spesifik dan distribusi kelas nyata — sehingga **bukan pengganti κ** dan bisa menyesatkan bila kelas sangat timpang.
- **Keputusan penggunaannya sebagai metrik gate: [OPEN DECISION OD-10].** Default tanpa keputusan: laporkan **Po dan κ multiclass saja**; PABAK multiclass hanya dilaporkan sebagai angka sekunder bila OD-10 disetujui, dan selalu dicantumkan bersama Po + κ.

### 5.3 Ambang agreement — **[OPEN DECISION OD-1]**

Usulan (perlu disetujui sebelum dipakai sebagai gate):
- **Lulus kalibrasi:** per kriteria per bahasa: κ ≥ 0.60 **dan** Po ≥ 0.80, atau Po ≥ 0.90 dengan κ ≥ 0.40 disertai tinjauan manual matriks konfusi (karena efek prevalensi).
- **Di bawah ambang:** revisi guideline → batch uji tambahan (OD-8) → ulangi.
- **Interpretasi hati-hati (ikuti §1.6):** dengan n=30 estimasi κ tidak presisi — ambang ini adalah **trigger tindakan** untuk memperbaiki guideline, bukan pengukuran reliabilitas final; klaim reliabilitas hanya layak dibuat dari volume produksi yang lebih besar.
- Untuk produksi: konflik ronde-1 pada kriteria tertentu → kriteria itu mendapat fokus revisi guideline; tidak membatalkan batch.

### 5.4 IE dalam perhitungan

IE diperlakukan sebagai kategori sah (bukan missing). Selain κ 3-kelas, laporkan **tingkat IE per kriteria** — bila IE melewati ambang tertentu dianggap sinyal guideline kurang operasional: **[OPEN DECISION OD-5]** (usulan: > 25% IE per kriteria per batch memicu review guideline).

### 5.5 Metrik Round 1 vs post-review (baru)

Dilaporkan terpisah, per kriteria × bahasa:

| Metrik | Definisi |
|---|---|
| `r1_agreement` | Po/κ pada **seluruh data** dari label Round 1 |
| `post_review_agreement` | Po/κ pada dataset hibrida (label R2 utk kriteria yang direview; label R1 utk yang tidak) |
| `conflicts_r1` | jumlah sel konflik Round 1 (per kriteria/bahasa) |
| `conflict_resolution_rate` | konflik yang sepakat di R2 ÷ `conflicts_r1` (jumlah + persen) |

Semua angka dilaporkan berdampingan dengan label individual tetap sebagai sumber kebenaran.

## 6. Penyimpanan & integritas label

### 6.1 File individual immutable

File per annotator per ronde (`ANNOTATION_TEMPLATE_{A-01,A-02}_{R1,R2}.csv`) adalah **rekaman tulis-sekali** — setelah dikumpulkan, tidak diedit. Semua file berpindah tangan via salinan (bukan edit bersama); koordinator menyimpan salinan ber-stempel waktu. Waktu anotasi (`annotated_at`) dicatat koordinator sebagai **metadata pengumpulan file** (waktu terima salinan per ronde) — annotator **tidak** mengisi timestamp secara manual.

### 6.2 Provenance konsensus — dua jenis kesepakatan

Per kriteria, koordinator mencatat **kedua field ini** secara terpisah (pemetaan ke skema kanonik memakai ketentuan additional-fields Task 03 §3.2):

| Field | Nilai | Makna |
|---|---|---|
| `initial_agreement` | true/false | kedua annotator **sudah sepakat sejak Round 1** pada kriteria tersebut |
| `post_review_agreement` | true/false | sepakat **setelah Round 2** (kriteria direview dan label R2 keduanya kembali sama) — untuk kriteria tak direview, nilainya identik dengan `initial_agreement` |

- Kesepakatan sejak Round 1 → `final_source = consensus`, `initial_agreement = true`, `post_review_agreement = true` (identik).
- Kesepakatan baru setelah Round 2 → `final_source = consensus`, `initial_agreement = false`, `post_review_agreement = true`.
- Kasus ke adjudication → `final_source = adjudicated` (kedua field tetap menyimpan apa yang terjadi sebelum adjudication).

### 6.3 Aturan mutlak

Konsensus/adjudication ditulis ke struktur terpisah (Task 03 §3.3: blok `final` terpisah dari `annotations`) — **tidak ada label individual yang ditimpa**, dan konsensus **selalu membawa provenance** jenis kesepakatannya (§6.2) sehingga analisis nanti dapat membedakan sepakat-alami vs. sepakat-pasca-review.

## 7. Produksi (setelah kalibrasi lulus)

1. Batch produksi disusun koheren-per-proyek dengan stratifikasi: bahasa, proyek, dan (sebisa mungkin sebelum anotasi) prediksi keragaman kriteria dari ciri tekstual — **tanpa melihat label historis**.
2. Alokasi ke train/val/test mengikuti Task 03 §6 — **test set dianotasi penuh dua annotator pada kedua bahasa dan dibekukan**; tidak ada story historis yang masuk test.
3. Target volume dan stratifikasi per kriteria ditetapkan koordinator setelah kalibrasi (mengukur berapa FAIL/IE alami per kriteria).
4. Bila OD-4 memilih split bahasa untuk train/val, keterbatasan inter-annotator tersebut **wajib** dicatat di laporan dataset (§2.3).

## 8. Daftar keputusan terbuka (rekap protokol; registry lengkap di README.md)

| ID | Keputusan | Usulan | Status |
|---|---|---|---|
| OD-1 | Ambang agreement (κ/Po) untuk lulus kalibrasi | κ ≥ 0.60 & Po ≥ 0.80 (baca hati-hati, §5.3) | **OPEN** |
| OD-2 | Akses konteks story lain untuk I/S | Default teks-saja | **OPEN** |
| OD-3 | Mode adjudication | Annotator ketiga disarankan | **OPEN** |
| OD-4 | Distribusi bahasa per annotator | Kalibrasi/test: kedua bahasa wajib; train/val boleh split dgn keterbatasan tercatat | **OPEN** |
| OD-5 | Batas IE per kriteria/batch | > 25% memicu review guideline | **OPEN** |
| OD-6 | Status penggunaan pilot-30: (a) arsip saja, (b) kalibrasi ulang di bawah skema baru, (c) bagian benchmark | Usulan: (b) dgn provenance dipertahankan; (c) keputusan terpisah | **OPEN** |
| OD-7 | Pemetaan label historis biner→three-class saat konsumsi (1→PASS, 0→FAIL) | Tercatat di `HISTORICAL_DATASET_INTEGRATION_SPEC.md` §4 — **bukan bagian protokol ini** | **OPEN** |
| OD-8 | Batch kalibrasi tambahan (+30) bila perlu | Ya, seleksi stratifikasi sama | **OPEN** |
| OD-10 | Penggunaan PABAK multiclass `(k·Po−1)/(k−1)` sebagai metrik gate selain Po+κ | Default: Po+κ saja; PABAK multiclass sekunder bila disetujui | **OPEN** |
