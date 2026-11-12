# INVEST Annotation Guideline (v1.1-draft untuk kalibrasi)

**Status:** Draft kalibrasi — **belum tervalidasi penuh**; revisi targeted dari v1.0 (changelog di §11). Bagian yang membutuhkan keputusan manusia ditandai **[OPEN DECISION]**.
**Bahasa kerja:** Indonesia (istilah teknis tetap Inggris). Cerita dianotasi dalam bahasa aslinya.
**Dokumen terkait:** `ANNOTATOR_HANDBOOK.md` (cara kerja), `ANNOTATION_TEMPLATE.csv` (format), `ANNOTATION_PROTOCOL.md` (proses ronde).

---

## 0. Prinsip dasar (wajib dibaca dulu)

1. **Basis penilaian adalah teks User Story itu sendiri.** Jangan menggunakan pengetahuan luar tentang proyek, tim, atau sistem. Jangan mengasumsikan informasi yang tidak tertulis.
2. **Bukan semua cerita harus punya benefit connector** ("so that" / "sehingga") ataupun acceptance criteria. Ketiadaan klausul bukan otomatis kegagalan — lihat aturan per kriteria.
3. **Bedakan dua hal ini secara ketat:**
   - **Ketiadaan bukti (absence of evidence):** teks tidak menyebut apa pun yang relevan → kandidat `INSUFFICIENT_EVIDENCE` bila penilaian butuh asumsi di luar teks.
   - **Bukti kegagalan (evidence of failure):** teks secara eksplisit memuat pola yang melanggar kriteria (kata preskriptif, aksi majemuk, ketergantungan, kualitatif tak terukur, dsb.) → `FAIL`.
4. **Tiga label saling eksklusif** — pilih tepat satu per kriteria:

| Label | Arti operasional | Kapan dipakai |
|---|---|---|
| `PASS` | Teks memuat **bukti positif** bahwa kriteria terpenuhi. | Cerita memenuhi definisi kriteria berdasarkan isinya. |
| `FAIL` | Teks memuat **bukti positif pelanggaran** kriteria (pola terlarang hadir di teks). | Pola pelanggaran dapat dikutip langsung dari teks. |
| `INSUFFICIENT_EVIDENCE` (IE) | Teks **tidak menyediakan informasi yang cukup** untuk menilai kriteria tanpa asumsi di luar teks. | Hanya bila memilih PASS atau FAIL memaksa Anda mengarang informasi. |

   IE **bukan** "mungkin", bukan "agak buruk", dan bukan substitusi aman untuk FAIL. IE digunakan hemat. `PASS` menuntut bukti positif — **jangan beri PASS hanya karena tidak ada bukti buruk.**
5. **Setiap FAIL dan IE wajib** punya `evidence` (rentang karakter) dan `rationale` (kode dari daftar tertutup, boleh + kalimat penjelas). Untuk `PASS`, rationale opsional namun disarankan.
6. Satu cerita boleh FAIL/IE di beberapa kriteria sekaligus; penilaian tiap kriteria independen.
7. Ragu antara dua label? Gunakan aturan tie-breaker di §9.

---

## 1. Independent (I)

**Definisi operasional:** cerita **membawa sendiri** semua yang dibutuhkan untuk dipahami dan dikerjakan — aktor, objek, dan hasilnya disebut di dalam teks — tanpa bergantung pada User Story lain yang eksplisit disebut atau dirujuk.

| | Kapan |
|---|---|
| `PASS` | **Bukti positif self-contained**: setiap rujukan di dalam teks memiliki antecedent di dalam teks itu sendiri (aktor, objek, dan hasil disebut eksplisit), dan tidak ada syarat yang mengikat cerita ini ke story/ticket/fitur lain. |
| `FAIL` | Teks memuat ketergantungan eksplisit: "setelah US-X selesai", "hanya setelah …", "story sebelumnya", "lanjutan dari …", atau kata rujukan ("tersebut", "yang tadi", "si user itu") yang antecedent-nya **berada di luar cerita** sehingga cerita tidak dapat dipahami sendiri. |
| `IE` | Teks mengisyaratkan ketergantungan ("melanjutkan", "upgrade dari fitur lama") tetapi tidak jelas apakah ini ketergantungan nyata pada story lain atau hanya narasi — dan menilainya butuh konteks proyek. |

**⚠️ PASS bukan default.** Ketiadaan kata "setelah"/"tersebut" **saja tidak cukup** untuk PASS. Periksa aktif: (a) apakah ada kata rujukan yang antecedent-nya di luar teks, (b) apakah cerita menyebut sendiri objek dan hasilnya. PASS diberikan hanya bila kedua pemeriksaan itu lolos.

**Rationale codes:** `EXPLICIT_DEPENDENCY`, `SEQUENTIAL_PREREQUISITE`, `CROSS_REFERENCE`, `REFERENCE_PRONOUN` | pass: `SELF_CONTAINED` | IE: `CONTEXT_DEPENDENT`.

**Contoh:**
- EN **FAIL** — *"Only after User Story US-42 is completed and deployed, as a courier I want …"* → bukti: prefiks dependensi eksplisit. (`EXPLICIT_DEPENDENCY`)
- ID **FAIL** — *"Hanya setelah User Story #US-25 selesai dikerjakan, sebagai kurir saya ingin mengambil foto penerima paket …"* (`EXPLICIT_DEPENDENCY`)
- EN **PASS** — *"As a camp administrator, I want to be able to automatically create nametags for campers, so that I can lower the amount of work I need to do."* → aktor (camp administrator), objek (nametags for campers), dan hasil semuanya disebut di dalam teks; tidak ada rujukan keluar. (`SELF_CONTAINED`)
- ID **IE** — *"Sebagai pengguna, saya ingin fitur laporan yang sudah dibuat kemarin bisa diekspor."* → "yang sudah dibuat kemarin" merujuk artefak di luar teks; tak jelas story mana. (`CONTEXT_DEPENDENT`)

**Edge cases:** frasa "setelah" yang hanya menjelaskan urutan pemakaian (bukan prasyarat pembangunan) bukan pelanggaran I — contoh ID *"Sebagai pasien, saya ingin memilih apotek terdekat setelah dokumen resep selesai diverifikasi"* tetap ditilai dari keseluruhan teks; bila "setelah" hanya narasi alur penggunaan → tidak otomatis FAIL.

---

## 2. Negotiable (N)

**Definisi operasional:** cerita menyatakan **apa** (what) dan **mengapa** (why), tanpa membiaskan **bagaimana** (how) pada tingkat implementasi/solusi internal.

### 2a. Pembedaan wajib: kebutuhan user-facing vs preskripsi implementasi

Bukan semua penyebutan "bentuk konkret" adalah pelanggaran N. Bedakan:

| Jenis | Contoh | Penilaian N |
|---|---|---|
| **Kebutuhan user-facing** — bentuk keluaran/hasil yang diterima pengguna | *"a report exported in CSV"*, *"a PDF resume"*, *"notification via email"* | **PASS** — ini menyatakan *what* (apa yang diterima user), bukan *how* (bagaimana dibangun) |
| **Preskripsi implementasi** — mandat cara membangun/menampilkan di dalam sistem | *"tombol biru 120x40px berfont Arial"*, *"eksekusi SQL INSERT ke tabel orders_v2"*, *"harus pakai framework X"*, *"backend changes for managing enum lists"* | **FAIL** |

Ukuran pembedanya: apakah frasa itu **diterima oleh pengguna sebagai hasil** (user-facing → PASS) atau **menentukan pilihan teknis internal pengembang** (preskripsi → FAIL). Ragu-ragu antara keduanya → `IE` (`DESIGN_INTENT_UNCLEAR`).

### 2b. Tabel keputusan

| | Kapan |
|---|---|
| `PASS` | Cerita menyatakan kebutuhan/hasil — termasuk format keluaran user-facing — tanpa mandat desain atau teknologi internal. |
| `FAIL` | Teks memnormakan detail implementasi internal: ukuran/warna/font/tata letak elemen UI, teknologi wajib di balik layar, alur klik langkah demi langkah, nama tabel/kolom. |
| `IE` | Detail teknis ada tetapi tidak jelas statusnya (ketentuan wajib vs. sekadar contoh) — dan teks tidak memberi petunjuk. |

**Rationale codes:** `PRESCRIPTIVE_UI`, `PRESCRIPTIVE_TECH`, `IMPLEMENTATION_MANDATE` | pass: `WHAT_NOT_HOW` | IE: `DESIGN_INTENT_UNCLEAR`.

**Contoh:**
- EN **FAIL** — *"As an OlderPerson, I want to use only well-visible buttons."* → memnormakan elemen UI spesifik. (`PRESCRIPTIVE_UI`)
- EN **FAIL** — *"As a user, I want backend changes for managing enum lists."* → mandat lapisan implementasi. (`PRESCRIPTIVE_TECH`)
- ID **FAIL** — *"Sebagai pengguna, saya ingin mengunggah dokumen dengan mengklik tombol biru 120x40px berlabel SUBMIT berfont Arial 11pt …"* (`PRESCRIPTIVE_UI`)
- EN **PASS** — *"As an admin, I want a report exported in CSV."* → **format keluaran yang diterima user** (user-facing requirement); tidak menentukan bagaimana ekspor diimplementasikan. (`WHAT_NOT_HOW`)
- ID **PASS** — *"Sebagai pemilik toko, saya ingin melihat ringkasan omzet penjualan harian pada dashboard pemilik, sehingga saya dapat memantau perputaran kas usaha."* → "dashboard pemilik" menyatakan lokasi/what, bukan mandat desain detil. (`WHAT_NOT_HOW`)
- ID **IE** — *"Sebagai pengguna, saya ingin menerima notifikasi (email atau SMS, mana saja yang bisa)."* → kanal disebut tetapi teks sendiri menyatakan fleksibilitas; status ketentuan vs. contoh tidak dapat dipastikan. (`DESIGN_INTENT_UNCLEAR`)

**Edge cases:** menyebut teknologi sebagai **konstrain yang dinyatakan pemilik kebutuhan** (mis. "harus tetap kompatibel dengan LDAP yang sudah ada") berbeda dengan mandat solusi; bila konstrain bisnis eksplisit dan berdampak pada penerimaan → cenderung PASS dengan rationale menjelaskan. Angka pada *domain* (nominal Rp 500.000, kuota 75%) bukan preskriptif UI — itu data kebutuhan (berdampak ke E/T, bukan N).

---

## 3. Valuable (V)

**Definisi operasional:** cerita menyatakan **nilai/manfaat** bagi peran — eksplisit (klausul manfaat) atau sebagai **konsekuensi langsung** dari kapabilitas yang diminta.

### 3a. Batas manfaat turunan (derived value) — wajib

| Boleh dihitung sebagai manfaat | Tidak boleh |
|---|---|
| **Konsekuensi langsung** dari kapabilitas yang diminta, sebagaimana tersurat dalam teks: artefak diterima (PDF resume), data tampil, status berubah, penerima mendapat sesuatu. | **Manfaat yang lebih luas tanpa teks**: dampak bisnis (efisiensi organisasi, KPI), psikologis (motivasi, kepuasan, rasa aman), atau reputasi/kepatuhan. |
| Contoh: *"mengunduh resume medis dalam format PDF"* → konsekuensi langsung: pasien memiliki arsip PDF — tersurat dari objeknya. | Contoh terlarang (bila tidak tertulis): "…sehingga kepuasan pelanggan meningkat", "agar pegawai lebih termotivasi" — mengarang dampak yang tidak ada di teks. |

Manfaat yang **ditulis eksplisit** di teks selalu boleh dipakai apa pun bentuknya (termasuk dampak bisnis) — batas ini hanya mengikat **penurunan** manfaat saat klausul manfaat tidak ada.

### 3b. Tabel keputusan

| | Kapan |
|---|---|
| `PASS` | Ada klausul manfaat eksplisit ("so that…", "sehingga…") **atau** konsekuensi langsung kapabilitas tersurat di teks (objek/hasil yang diterima disebut). |
| `FAIL` | Tidak ada klausul manfaat **dan** satu-satunya "konsekuensi" yang bisa diturunkan hanyalah pengulangan aksi itu sendiri (tautologis), atau manfaat hanya dapat ditebak dari pengetahuan domain. Bukti positifnya: ketiadaan total klausul/manfaat pada cerita yang strukturnya lengkap — kutip seluruh teks. |
| `IE` | Cerita terpotong/tidak lengkap sehingga menilai manfaat butuh mengarang konteks. |

**Rationale codes:** `MISSING_BENEFIT`, `TAUTOLOGICAL_BENEFIT`, `BENEFIT_UNCLEAR` | pass: `EXPLICIT_BENEFIT`, `DERIVED_VALUE` | IE: `STORY_INCOMPLETE`.

**Contoh:**
- EN **PASS** — *"As a pilot, I want to receive real-time weather radar updates, so that I can navigate around severe storm cells."* (`EXPLICIT_BENEFIT`)
- ID **PASS** — *"Sebagai pasien, saya ingin mengunduh resume medis rawat jalan dalam format PDF."* → konsekuensi langsung tersurat: pasien memperoleh arsip PDF. (`DERIVED_VALUE`)
- ID **PASS** — *"Sebagai kasir toko, saya ingin memindai barcode produk belanjaan dengan pemindai laser, sehingga harga barang langsung muncul pada struk pembayaran."* (`EXPLICIT_BENEFIT`)
- EN **FAIL** — *"As a user, I want to access the raw agency published files from FABS via USAspending."* → tidak ada klausul manfaat; satu-satunya konsekuensi yang bisa diturunkan ("user dapat mengakses file") adalah pengulangan aksinya sendiri — tidak ada nilai di luar aksi yang tersurat. (`MISSING_BENEFIT`)
- ID **FAIL** — *"Sebagai pengguna, saya ingin melihat daftar produk, sehingga saya dapat melihat daftar produk."* → tautologis. (`TAUTOLOGICAL_BENEFIT`)
- EN **IE** — fragmen *"… upload the export settings."* tanpa peran maupun konteks → `STORY_INCOMPLETE`.

**Edge case penting:** cerita tanpa "so that" tetapi dengan konsekuensi langsung tersurat — ID *"Sebagai pasien, saya ingin mengunduh resume medis rawat jalan dalam format PDF."* → **PASS** `DERIVED_VALUE` (artefak yang diterima disebut). Bandingkan: ID *"Sebagai OlderPerson, saya ingin menggunakan hanya tombol-tombol yang terlihat jelas."* → tidak ada konsekuensi langsung yang dinyatakan (kemudahan pakai hanya tebakan) → **FAIL** `MISSING_BENEFIT`, evidence = seluruh teks. Dua contoh ini adalah garis batasnya.

---

## 4. Estimable (E)

**Definisi operasional:** berdasarkan teksnya, tim dapat **memperkirakan ukuran pekerjaan**. Dua kegagalan estimasi berbeda dan harus dipilah:

1. **Cakupan terbuka (open-ended)** — teks membuka lingkup tanpa batas jelas → **FAIL** (bukti positif: kuantifier terlarang dikutip).
2. **Cakupan tertutup tetapi tak tertakar (bounded but unquantified)** — lingkupnya jelas dan berhingga ("seluruh data yang ada"), namun **besarnya tidak dapat ditakar dari teks** → **IE** `EXTERNAL_INFO_NEEDED` (butuh data di luar teks, bukan pelanggaran).

### 4b. Tabel keputusan

| | Kapan |
|---|---|
| `PASS` | Objek, sumber, dan lingkup terdefinisi **dan** tertakar dari teks; tidak ada kuantifier terbuka. |
| `FAIL` | Kuantifier kabur/hampir tak terbatas hadir di teks: "banyak", "berbagai macam", "dll", "as needed", "various", "many open-ended options" — cakupan membuka diri tanpa batas. |
| `IE` | Cakupan **tertutup** (semua X yang ada, satu laporan, satu formulir) tetapi ukurannya tidak bisa ditakar tanpa data di luar teks. |

**Rationale codes:** `VAGUE_QUANTIFIER`, `OPEN_ENDED_SCOPE` | pass: `CONCRETE_OBJECTS`, `BOUNDED_SCOPE` | IE: `EXTERNAL_INFO_NEEDED`.

**Contoh:**
- EN **FAIL** — *"As a warehouse worker, I want to update inventory including some various transaction metrics, several data items, and many open-ended options etc."* → "various/many/etc." membuka cakupan. (`VAGUE_QUANTIFIER`, `OPEN_ENDED_SCOPE`)
- ID **FAIL** — *"Sebagai admin, saya ingin mencatat berbagai macam transaksi dan banyak data lainnya dll."* → "berbagai macam … dll." = cakupan terbuka. (`VAGUE_QUANTIFIER`, `OPEN_ENDED_SCOPE`)
- EN **PASS** — *"As an OlderPerson, I want to have ALFRED on a bracelet or a necklace, so that I can always wear him with me."* → objek konkret, lingkup terbatas dan tertakar. (`CONCRETE_OBJECTS`)
- ID **IE (contoh revisi)** — *"Sebagai admin, saya ingin memigrasikan seluruh data lama ke sistem baru."* → "seluruh data lama" adalah cakupan **tertutup** (berhingga: semua data yang ada) tetapi volumenya tak tertakar dari teks → bukan FAIL, melainkan **IE** `EXTERNAL_INFO_NEEDED` (butuh data volume di luar teks).

---

## 5. Testable (T)

**Definisi operasional:** teks menyatakan hasil yang **dapat diverifikasi** — ada perubahan keadaan/aksi observabel atau kondisi terukur yang bisa diperiksa penerima cerita tanpa mendefinisikan ulang makna kata-katanya.

| | Kapan |
|---|---|
| `PASS` | Hasil observabel/terukur tersirat jelas dari aksi (laporan masuk dan terlihat, file dihasilkan, saldo ter-update, tolak input A). |
| `FAIL` | Kualitatif subjektif tanpa kriteria terukur: "cepat", "mudah", "user-friendly", "bagus", "jelas", "nyaman"; atau tidak ada hasil yang bisa diverifikasi sama sekali. |
| `IE` | Hasil verifikasi bergantung pada definisi yang harus datang dari pemilik kebutuhan dan teks tidak memberinya (mis. "secure" — butuh definisi ancaman). |

**Rationale codes:** `SUBJECTIVE_ADJECTIVE`, `UNMEASURABLE_OUTCOME`, `NO_VERIFIABLE_OUTCOME` | pass: `VERIFIABLE_OUTCOME`, `MEASURABLE_CONDITION` | IE: `CRITERIA_UNDEFINED`.

**Contoh:**
- ID **FAIL** — *"Sebagai user, saya ingin proses login berjalan dengan cepat dan mudah."* → "cepat dan mudah" tanpa ukuran. (`SUBJECTIVE_ADJECTIVE`)
- EN **FAIL** — *"As an OlderPerson, I want to use only well-visible buttons."* → "well-visible" tak terukur dari teks. (`UNMEASURABLE_OUTCOME`)
- EN **PASS (contoh baru)** — *"As a citizen, I want to report pothole road hazards through the public works portal, so that repair crews can be scheduled."* → hasil observabel dan dapat diperiksa: laporan masuk ke portal dan jadwal perbaikan terbentuk/terlihat. (`VERIFIABLE_OUTCOME`)
- ID **PASS** — *"Sebagai pembeli, saya ingin melacak posisi paket berdasarkan nomor resi, sehingga saya mengetahui tahapan perjalanan pesanan."* → verifikasi: masukkan resi → posisi tampil. (`VERIFIABLE_OUTCOME`)
- ID **IE** — *"Sebagai admin, saya ingin sistem lebih aman dari sebelumnya."* → "aman" butuh definisi ancaman dari pemilik kebutuhan. (`CRITERIA_UNDEFINED`)

**Edge case (menggantikan contoh lama):** verb proses kabur seperti *"processed"*, *"handled"*, *"synced"* tanpa definisi keadaan akhir (apa yang berubah, kapan, terlihat di mana) membuat verifikasi bergantung definisi pihak lain → nilai `IE` `CRITERIA_UNDEFINED`, kecuali teks menyebut sendiri keadaan akhir yang observabel.

---

## 6. Small (S)

**Definisi operasional:** cerita mencakup **satu kapabilitas koheren** yang wajar diselesaikan dalam satu iterasi tim kecil — dinilai dari jumlah aksi/keputusan desain yang diimplikasikan teks.

| | Kapan |
|---|---|
| `PASS` | Satu aksi utama + satu hasil. |
| `FAIL` | Aksi majemuk eksplisit ("dan juga …", "serta …", "sekalian …"), gabungan beberapa fitur, cakupan epik ("semua", "seluruh sistem", "end-to-end"), atau cerita mengikat banyak keputusan desain besar. |
| `IE` | Tunggal vs. epik tidak dapat dipastikan tanpa konteks proyek (mis. "kelola akun" bisa kecil atau epik tergantung sistem). |

**Rationale codes:** `COMPOUND_ACTION`, `EPIC_SCOPE`, `MULTI_OUTCOME` | pass: `SINGLE_CAPABILITY` | IE: `SCOPE_UNCLEAR`.

**Contoh:**
- ID **FAIL** — *"Sebagai admin gudang, saya ingin mencetak label barcode dan juga memperbarui stok barang serta mengirim notifikasi ke supplier, sehingga pengiriman siap."* → tiga aksi berbeda dalam satu cerita. (`COMPOUND_ACTION`)
- EN **FAIL** — *"As a user, I want to manage all user accounts, roles, and permissions across the entire system."* → cakupan epik lintas subsistem. (`EPIC_SCOPE`)
- EN **PASS** — *"As an OlderPerson, I want to have ALFRED on a bracelet or a necklace, so that I can always wear him with me."* → satu kapabilitas (bentuk perangkat yang dapat dipakai). (`SINGLE_CAPABILITY`)
- ID **IE** — *"Sebagai manager HR, saya ingin mengelola cuti karyawan."* → "mengelola cuti" bisa satu fitur pengajuan sederhana atau bundel besar (pengajuan+approval+kuota+laporan); teks tak menentukan. (`SCOPE_UNCLEAR`)

**Edge case:** dua aksi yang **satu rantai** (mengunggah lalu memverifikasi hasil unggahan) umumnya masih satu kapabilitas; yang dihukum adalah aksi **tak sejenis** yang digabung (cetak label + update stok + kirim notifikasi). Gunakan §9 bila bertabrakan dengan E.

---

## 7. Kesalahan umum yang harus dihindari

1. Memberi PASS karena "tidak ada yang salah terlihat" — PASS butuh bukti positif (terutama I: periksa rujukan aktif, lihat §1).
2. Menganggap ketiadaan "so that" otomatis FAIL V — lihat aturan V: konsekuensi **langsung** yang tersurat masih PASS; yang gagal adalah cerita tanpa manfaat dan tanpa konsekuensi langsung selain pengulangan aksi.
3. Menganggap angka di teks otomatis membuat E/T PASS — angka harus relevan dengan ukuran/verifikasi.
4. Menghukum N karena menyebut **format keluaran user-facing** (CSV, PDF, email) — itu kebutuhan what, bukan mandat bagaimana; yang dihukum adalah preskripsi internal (tabel, framework, ukuran tombol). Lihat §2a.
5. IE sebagai "zonanya aman" — IE hanya bila PASS/FAIL sama-sama memaksa asumsi; cakupan tertutup-tak-tertakar (E) adalah IE, cakupan terbuka adalah FAIL (§4).
6. Menilai I dari keberadaan story lain di batch — basisnya tetap teks; rujukan eksplisit di teks yang dihukum.
7. Menilai S "secara perasaan" — S FAIL harus ada aksi majemuk/epik yang bisa dikutip.

## 8. Format evidence span

- `evidence` = posisi karakter dalam `original_text`, **1-based, inklusif**: `start-end` (contoh: `18-46`).
- Lebih dari satu bukti: pisah dengan `;` (contoh: `18-46;77-103`).
- **FAIL berbasis ketiadaan** (mis. `MISSING_BENEFIT`): gunakan `1-N` dengan N = panjang `original_text` (seluruh teks) — bukan `0-(N-1)` — agar konvensi koordinat tetap 1-based dan keabsahan bukti tetap dapat diperiksa otomatis.
- Validasi otomatis span: `1 ≤ start ≤ end ≤ N`. Jangan mengutip teks di kolom evidence — kutipan pendek boleh di `rationale` setelah kode.

## 9. Tie-breaker & konsistensi

- IE vs FAIL: bila pola pelanggaran **dapat dikutip** → FAIL; bila penilaian butuh asumsi → IE. Untuk E, terapkan pembedaan §4: cakupan terbuka = FAIL, cakupan tertutup-tak-tertakar = IE.
- IE vs PASS: PASS butuh bukti positif; tanpanya, IE.
- S vs E: keduanya menilai "ukuran" dari sudut berbeda (S = jumlah kapabilitas; E = keterukaran lingkup). Bila satu cerita jelas majemuk **dan** terbuka, keduanya boleh FAIL dengan kode masing-masing; bila hanya satu pola terbaca, pilih yang paling langsung dan gunakan kode yang menjelaskan. Contoh yang sudah terpilah: *"memigrasikan seluruh data lama"* → S tetap dipertanyakan (`SCOPE_UNCLEAR` bila ragu) sementara E sudah terpilah ke IE (§4).
- Bila dua pola pelanggaran sama-sama jelas untuk satu kriteria, tetap satu label FAIL; sebutkan kedua kode (pisah `;`).

## 10. Hal yang secara sengaja TIDAK ditentukan di dokumen ini

- Ambang agreement antar-annotator → **[OPEN DECISION OD-1]** (lihat `ANNOTATION_PROTOCOL.md`).
- Kebijakan batas penggunaan IE per batch → **[OPEN DECISION OD-5]**.
- Izin melihat story lain dalam batch untuk konteks I/S → **[OPEN DECISION OD-2]** (default dokumen ini: teks-saja).

## 11. Changelog revisi (v1.0 → v1.1)

| # | Lokasi | Perubahan |
|---|---|---|
| 1 | §1 | PASS Independent kini menuntut bukti positif self-contained (rujukan ter-resolve internal); ketiadaan kata dependensi saja tidak otomatis PASS. |
| 2 | §2 | Baru §2a: pembedaan kebutuhan user-facing vs preskripsi implementasi; contoh CSV export dipindah dari IE ke **PASS**; contoh IE baru (kanal notifikasi ambigu); perbaikan pitfall #7.4. |
| 3 | §3 | Baru §3a: batas manfaat turunan — hanya konsekuensi langsung tersurat; manfaat bisnis/psikologis/organisasi tak boleh diarang; contoh `DERIVED_VALUE` baru (resume PDF); contoh FABS diperjelas (tautologis). |
| 4 | §4 | Ambigu FAIL-vs-IE diselesaikan: cakupan terbuka = FAIL; cakupan tertutup-tak-tertakar = IE; contoh migrasi "seluruh data lama" direvisi menjadi **IE** `EXTERNAL_INFO_NEEDED`. |
| 5 | §6 | Contoh PASS "12-19-2017 deletions processed" diganti dgn contoh observabel baru (report potholes → portal); verb proses kabur ("processed/handled/synced") masuk edge case → IE bila keadaan akhir tak didefinisikan. |
| 6 | §8 | Konvensi koordinat dikonsistenkan: 1-based inklusif; FAIL berbasis ketiadaan memakai **`1-N`** (sebelumnya `0-(N-1)`); instruksi validasi span diperbarui. |
| 7 | §7, §9 | Pitfall #1/#2/#4/#5 dan tie-breaker §9 diselaraskan dengan perubahan di atas. |

**Sisa ambiguitas yang diakui (untuk kalibrasi):** (a) garis batas N untuk frasa bentuk-perangkat ("bracelet or a necklace" — bentuk produk vs kebutuhan wearable); (b) E pada "seluruh X" yang bisa dibaca cakupan terbuka oleh sebagian annotator — tie-breaker §9 berlaku; (c) batas IE pada verb proses kabur. Ketiganya disengaja dibiarkan untuk diuji di ronde kalibrasi; tidak ada keputusan final di sini.
