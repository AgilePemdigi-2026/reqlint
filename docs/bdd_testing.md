# 🧪 Dokumentasi Pengujian BDD (Behavior-Driven Development) ReqLint

> **Standar Acuan**: ISO/IEC/IEEE 29148:2018 & INVEST Criteria  
> **Framework**: `pytest-bdd` (Python 3.14+), `Gherkin`, `pytest-asyncio`, `httpx`  
> **Status Suite**: ✅ **32 Scenarios Passed (100% Passing)**

---

## 📌 1. Pendahuluan & Filosofi BDD

Behavior-Driven Development (BDD) pada proyek **ReqLint** dirancang untuk menjembatani komunikasi antara *System Analyst*, *Product Manager*, *Developer*, dan *QA Engineer*. Setiap skenario pengujian ditulis dalam bahasa natural terstruktur menggunakan sintaks **Gherkin** (*Given - When - Then*), merepresentasikan perilaku nyata pengguna (*user behavior*) sesuai dokumen spesifikasi:
1. [**SRS Spesifikasi Kebutuhan**](file:///d:/portfolio/AI/reqlint/docs/srs_spesifikasi_kebutuhan.md) (`UTS_I4_REQLINT_SRS`)
2. [**Data Uji Coba & Mockup**](file:///d:/portfolio/AI/reqlint/docs/mockup_data.md) (`UTS_I4_REQLINT_DATA`)
3. [**Arsitektur & Integrasi Teknis**](file:///d:/portfolio/AI/reqlint/docs/arsitektur_dan_integrasi.md)
4. [**Pedoman Anotasi INVEST**](file:///d:/portfolio/AI/reqlint/docs/pedoman_anotasi_invest.md)

---

## 🏗️ 2. Struktur Direktori Suite Pengujian BDD

Suite pengujian BDD diletakkan secara terstruktur dan modular di dalam direktori `backend/tests/bdd/`:

```
backend/
├── run_bdd.py                               # Runner CLI pengujian BDD mandiri
├── pytest.ini                               # Konfigurasi runner & register custom markers
├── requirements.txt                         # Dependensi (fastapi, pytest, pytest-bdd, dll.)
└── tests/
    └── bdd/
        ├── conftest.py                      # Fixture bersama, konteks skenario, & step umum
        ├── features/                        # Berkas spesifikasi Gherkin (.feature)
        │   ├── 01_auth.feature              # FEAT-6 & FEAT-7: Registrasi & Login JWT
        │   ├── 02_input_story_audit.feature # FEAT-1: Input User Story & Connextra
        │   ├── 03_pdf_document_upload.feature # FEAT-2: Ekstraksi Berkas PDF & Validasi
        │   ├── 04_audit_results_and_scorecard.feature # FEAT-4: Scorecard, Smells, & AC
        │   ├── 05_apply_and_manual_revision.feature   # FEAT-4: 1-Click Apply & Edit Manual
        │   ├── 06_history_and_search.feature# FEAT-3: Riwayat Audit & Filter Pencarian
        │   ├── 07_export_report.feature     # FEAT-5: Ekspor Dokumen JSON, MD, PDF
        │   └── 08_security_and_data_isolation.feature # SEC-4 & NFR-06: Isolasi Antar-Akun
        ├── test_01_auth_bdd.py              # Step Definitions Autentikasi
        ├── test_02_input_story_bdd.py       # Step Definitions Input & Audit
        ├── test_03_pdf_upload_bdd.py        # Step Definitions Upload Dokumen PDF
        ├── test_04_audit_results_bdd.py     # Step Definitions Scorecard & Temuan
        ├── test_05_revision_bdd.py          # Step Definitions Revisi Draf
        ├── test_06_history_bdd.py           # Step Definitions Riwayat Audit
        ├── test_07_export_bdd.py            # Step Definitions Ekspor Laporan
        └── test_08_security_bdd.py          # Step Definitions Keamanan & Isolasi
```

---

## 📋 3. Matriks Cakupan Fitur & 32 Skenario Pengujian

| Kode Fitur | Nama Fitur SRS | Berkas Feature | Jumlah Skenario | Kode Status HTTP yang Diverifikasi |
|---|---|---|:---:|:---:|
| **FEAT-6 & 7** | Registrasi & Login Pengguna | `01_auth.feature` | 6 | `201`, `200`, `401`, `409`, `422` |
| **FEAT-1** | Input Teks User Story & Heuristik | `02_input_story_audit.feature` | 4 | `200`, `202`, `422` |
| **FEAT-2** | Upload & Ekstraksi Dokumen PDF | `03_pdf_document_upload.feature` | 6 | `200`, `413`, `422` |
| **FEAT-4** | Scorecard, INVEST, & AI Recommendation | `04_audit_results_and_scorecard.feature` | 2 | `200` |
| **FEAT-4** | 1-Click Apply & Penyuntingan Manual | `05_apply_and_manual_revision.feature` | 3 | `200`, `422` |
| **FEAT-3** | Riwayat Audit & Pencarian Log | `06_history_and_search.feature` | 4 | `200` |
| **FEAT-5** | Ekspor Laporan Multi-Format | `07_export_report.feature` | 4 | `200`, `422` |
| **SEC-4 / NFR**| Keamanan & Isolasi Akses Pengguna | `08_security_and_data_isolation.feature` | 3 | `401`, `404` |
| **TOTAL** | **8 Kategori Fitur Inti** | **8 Feature Files** | **32 Skenario** | **100% Lulus (Pass)** |

---

## 🔍 4. Rincian Skenario Per Fitur

### 4.1 Feature 1: Autentikasi dan Manajemen Sesi (`01_auth.feature`)
* **Skenario 1.1**: Pendaftaran akun baru berhasil dengan data valid (`201 Created`, envelope standard, password hash tidak diekspos).
* **Skenario 1.2**: Pendaftaran gagal jika konfirmasi kata sandi tidak cocok (`422`, pesan: *"Format sandi tidak valid atau konfirmasi sandi tidak cocok"*).
* **Skenario 1.3**: Pendaftaran gagal jika kata sandi kurang dari 8 karakter (`422`).
* **Skenario 1.4**: Pendaftaran gagal jika email duplikat (`409 Conflict`, error: `EMAIL_TAKEN`, pesan: *"Email sudah terdaftar"*).
* **Skenario 1.5**: Login akun terdaftar mengembalikan token JWT bertipe `bearer` (`200 OK`).
* **Skenario 1.6**: Login gagal dengan kata sandi salah (`401 Unauthorized`, error: `INVALID_CREDENTIALS`, pesan: *"Kredensial tidak valid"*).

### 4.2 Feature 2: Input Teks User Story & Pipeline Audit (`02_input_story_audit.feature`)
* **Skenario 2.1**: Penolakan draf kebutuhan kosong atau whitespace (`422`, error: `EMPTY_DRAFT`, pesan: *"Draf kebutuhan tidak boleh kosong"*).
* **Skenario 2.2**: Penerimaan draf kebutuhan valid Connextra (`202 Accepted`, menerbitkan `id_audit` dan `poll_url`).
* **Skenario 2.3**: Eksekusi pipeline audit 2-tahap selesai hingga status `COMPLETED` dan stage2 bernilai `DONE`.
* **Skenario 2.4**: Audit langsung klausul via endpoint heuristik dwibahasa (`/api/v1/requirements/audit`) mendeteksi bahasa `id`, skor kualitas, daftar smells, dan rekomendasi INVEST.

### 4.3 Feature 3: Ekstraksi Dokumen PDF (`03_pdf_document_upload.feature`)
* **Skenario 3.1**: Ekstraksi teks berhasil dari PDF digital valid via PyMuPDF (`200 OK`, teks diekstrak, `id_dokumen` diterbitkan).
* **Skenario 3.2**: Pengguna tamu (guest mode) dapat mengunggah PDF tanpa token (`200 OK`, `id_dokumen` bernilai `null`).
* **Skenario 3.3**: Penolakan berkas berekstensi bukan `.pdf` (`422`, error: `INVALID_FILE_FORMAT`, pesan: *"Format file tidak valid, harap unggah dokumen .pdf"*).
* **Skenario 3.4**: Penolakan berkas PDF korup/rusak (`422`).
* **Skenario 3.5**: Penolakan berkas PDF hasil scan tanpa lapisan teks digital (`422`, error: `EMPTY_PDF_TEXT`, pesan: *"PDF tidak memuat lapisan teks (hasil pemindaian), harap unggah dokumen digital"*).
* **Skenario 3.6**: Penolakan berkas melebihi batas 10 MB (`413 Content Too Large`, pesan: *"Ukuran file melebihi batas 10 MB"*).

### 4.4 Feature 4: Scorecard, Smells, & Rekomendasi AI (`04_audit_results_and_scorecard.feature`)
* **Skenario 4.1 (Mockup Kasus 1)**: Evaluasi User Story bermasalah:
  > *"Sebagai user, saya ingin proses login sistem berjalan dengan sangat cepat dan user-friendly agar tidak membuang waktu."*
  * Skor berada di bawah 85, mendeteksi temuan ambiguitas leksikal (*"sangat cepat"*), menghasilkan usulan `ai_rewrite`, dan kriteria penerimaan otomatis format *Given-When-Then*.
* **Skenario 4.2 (Mockup Kasus 2)**: Evaluasi User Story ideal:
  > *"Sebagai System Analyst, saya ingin melihat riwayat audit pada tabel log sehingga saya mengetahui perkembangan revisi draf kebutuhan."*
  * Skor kualitas mencapai minimal 85, **0 temuan cacat**, dan seluruh dimensi kepatuhan INVEST terpenuhi.

### 4.5 Feature 5: Penerapan Rekomendasi 1-Click & Revisi Manual (`05_apply_and_manual_revision.feature`)
* **Skenario 5.1**: Penerapan instan 1-Click Apply memperbarui draf (`200 OK`, pesan: *"Draf berhasil diperbarui"*, status revisi: `"SUDAH_DIREVISI"`, label: *"Skor Kualitas Terkini"*).
* **Skenario 5.2**: Penyuntingan revisi manual dengan teks kuantitatif baru (`200 OK`, skor kualitas baru terhitung otomatis).
* **Skenario 5.3**: Penolakan penyimpanan revisi manual kosong (`422`, pesan: *"Draf kebutuhan tidak boleh kosong"*).

### 4.6 Feature 6: Riwayat Audit & Pencarian Log (`06_history_and_search.feature`)
* **Skenario 6.1**: Pengguna baru melihat daftar riwayat audit kosong (`has_any_history` false, pesan: *"Belum ada riwayat audit yang tersedia"*).
* **Skenario 6.2**: Pengguna dengan beberapa audit melihat daftar log audit terurut (`has_any_history` true, panjang riwayat >= 2).
* **Skenario 6.3**: Pencarian riwayat berdasarkan kata kunci (misal: `"Login"`) mengembalikan baris yang cocok.
* **Skenario 6.4**: Pencarian dengan kata kunci yang tidak ada mengembalikan daftar kosong dengan pesan *"Tidak ada riwayat yang cocok dengan pencarian"*.

### 4.7 Feature 7: Ekspor Dokumen Laporan Multi-Format (`07_export_report.feature`)
* **Skenario 7.1**: Ekspor hasil audit ke format **JSON** (`application/json`, header content-disposition `reqlint-audit`).
* **Skenario 7.2**: Ekspor hasil audit ke format **Markdown** (`text/markdown`).
* **Skenario 7.3**: Ekspor hasil audit ke format **PDF** (`application/pdf`).
* **Skenario 7.4**: Penolakan format ekspor yang tidak didukung (misal `.docx`) mengembalikan `422` (*"Format tidak didukung"*).

### 4.8 Feature 8: Keamanan & Isolasi Akses Lintas Pengguna (`08_security_and_data_isolation.feature`)
* **Skenario 8.1 (SEC-4 Compliance)**: Pengguna B mengakses ID audit milik Pengguna A mengembalikan **`404 Not Found`** (*"Data audit tidak ditemukan"*), bukan `403 Forbidden`, untuk mencegah kebocoran informasi (*information leakage*).
* **Skenario 8.2**: Pengguna B mengekspor audit milik Pengguna A mengembalikan `404 Not Found`.
* **Skenario 8.3**: Akses endpoint terproteksi tanpa header Authorization ditolak dengan `401 Unauthorized` (*"Sesi tidak valid atau telah berakhir"*).

---

## 🚀 5. Cara Menjalankan Pengujian BDD

### A. Menggunakan Runner Mandiri `run_bdd.py`
Dari root workspace direktori proyek:
```bash
python run_bdd.py
```
Atau dari dalam direktori `backend/`:
```bash
python run_bdd.py
```

### B. Menggunakan `pytest` Langsung
Menjalankan seluruh skenario BDD:
```bash
cd backend
pytest tests/bdd -v
```

### C. Menjalankan Berdasarkan Tag / Marker Spesifik
```bash
# Hanya jalankan skenario autentikasi
pytest tests/bdd -m "auth"

# Hanya jalankan skenario upload PDF
pytest tests/bdd -m "pdf"

# Hanya jalankan skenario scorecard INVEST
pytest tests/bdd -m "scorecard"

# Hanya jalankan skenario keamanan & isolasi SEC-4
pytest tests/bdd -m "sec4"
```

### D. Menjalankan Satu Berkas Uji Spesifik
```bash
pytest tests/bdd/test_04_audit_results_bdd.py -v
```

---

## 📊 6. Hasil Eksekusi Uji Terkini

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\portfolio\AI\reqlint\backend
configfile: pytest.ini
plugins: anyio-4.12.1, hypothesis-6.170.1, asyncio-1.4.0, bdd-9.0.1, cov-7.1.0
collected 32 items

tests\bdd\test_01_auth_bdd.py ......                                     [ 18%]
tests\bdd\test_02_input_story_bdd.py ....                                [ 31%]
tests\bdd\test_03_pdf_upload_bdd.py ......                               [ 50%]
tests\bdd\test_04_audit_results_bdd.py ..                                [ 56%]
tests\bdd\test_05_revision_bdd.py ...                                    [ 65%]
tests\bdd\test_06_history_bdd.py ....                                    [ 78%]
tests\bdd\test_07_export_bdd.py ....                                     [ 90%]
tests\bdd\test_08_security_bdd.py ...                                    [100%]

============================== 32 passed in 43.23s ==============================
```

