# 📋 Dokumen Mockup Data Input & Output ReqLint
> **Nomor Berkas**: `UTS_I4_REQLINT_DATA`  
> **Kelompok**: 3 (Kelas I4)  
> **Anggota Tim**:
> 1. Daniel Purnomo (187241001)
> 2. Mochammad Farhan Akbar (187241002)
> 3. Bima Akbar Rizqullah (187241077)
> 4. Andreas Pratama Syahputra (187241101)

---

## 📌 1. Sampel Evaluasi Teks User Story Bermasalah (Interactive Editor)

### A. Data Input (Teks Diketik / Ditempel Pengguna)
* `"Sebagai user, saya ingin proses login sistem berjalan dengan sangat cepat dan user-friendly agar tidak membuang waktu."`
* `"Sebagai pengembang, draf kebutuhan harus disimpan secara otomatis oleh sistem."`

### B. Data Output (Hasil Pemrosesan ReqLint Engine)
* **Quality Scorecard**: **58 / 100** *(Status: Needs Improvement)*

#### Tabel Temuan Cacat (*Ambiguity & Smell Detector*):
| Lokasi Teks | Kategori Cacat | Istilah Terdeteksi | Rekomendasi Perbaikan |
|---|---|---|---|
| Kalimat 1 | **Ambiguity** | *"sangat cepat"* | Kata tidak terukur. Tentukan parameter batas latensi spesifik (misal: `< 2 detik`). |
| Kalimat 1 | **Non-Testable** | *"user-friendly"* | Kata bersifat subjektif. Ganti dengan kriteria navigasi atau standar UI/UX spesifik. |
| Kalimat 2 | **Passive Voice** | *"harus disimpan"* | Penulisan kalimat pasif tanpa aktor eksplisit. Ubah ke bentuk aktif (*User POV*). |

#### Hasil AI Rewrite (*Diff Viewer Comparison*):
* **Draf Asli**:
  > *"Sebagai user, saya ingin proses login sistem berjalan dengan sangat cepat dan user-friendly agar tidak membuang waktu."*
* **Usulan Perbaikan (AI Rewrite)**:
  > *"Sebagai pengguna, saya ingin memverifikasi kredensial login dalam waktu kurang dari 2 detik agar dapat langsung mengakses halaman dashboard utama."*

#### Kriteria Penerimaan Otomatis (*Format Given-When-Then*):
* **Given**: Pengguna berada di halaman login.
* **When**: Pengguna memasukkan email dan kata sandi yang valid lalu menekan tombol "Login".
* **Then**: Sistem memvalidasi kredensial dan mengalihkan ke dashboard dalam waktu `< 2 detik`.

---

## ✅ 2. Sampel Evaluasi User Story Ideal / Lulus (Skor Tinggi)

### A. Data Input (Teks Diketik Pengguna)
> *"Sebagai System Analyst, saya ingin melihat riwayat audit pada tabel log agar dapat melacak perkembangan revisi draf kebutuhan."*

### B. Data Output (Hasil Pemrosesan ReqLint Engine)
* **Quality Scorecard**: **95 / 100** *(Status: Passed / Excellent)*
* **Tabel Temuan Cacat**: **0 Cacat Terdeteksi**
* **Analisis Kepatuhan INVEST**:
  * **Independent**: Mandiri dan dapat berdiri sendiri tanpa dependensi tersembunyi.
  * **Testable**: Kriteria penerimaan jelas, objektif, dan dapat diuji secara otomatis.
  * **Unambiguous**: Mematuhi struktur *Role*, *Means*, *End* secara presisi tanpa kata subjektif atau konstruksi pasif.

---

## 📄 3. Sampel Unggah Dokumen PDF Spesifikasi

### A. Data Input (Pengunggahan Berkas)
* **Nama Berkas**: `Draf_Spesifikasi_Kebutuhan_v1.pdf`
* **Ukuran Berkas**: 1.4 MB
* **Konten Teks dalam PDF**:
  > *"US-01: Sebagai System Analyst, saya ingin mengunggah berkas PDF berukuran sangat besar agar dapat diekstraksi secara otomatis."*

### B. Data Output (Ekstraksi & Evaluasi Sistem)
* **Status Ekstraksi**: Sukses *(1 Klausul Terdeteksi & Diekstraksi via PyMuPDF)*
* **Quality Scorecard Agregat**: **65 / 100**
* **Temuan Cacat**: Istilah *"sangat besar"* terdeteksi ambigu. Disarankan menentukan batasan ukuran berkas eksplisit (misal: *maksimal 10 MB*).

---

## 📜 4. Penelusuran Riwayat Evaluasi (History Audit Log)

### A. Data Input
Pengguna mengakses menu navigasi **"History Audit"**.

### B. Data Output (Tabel Riwayat dari Database)
| ID Audit | Tanggal | Judul / Klausul | Quality Score | Status Revisi |
|---|---|---|:---:|:---:|
| `AUD-101` | 08/10/2026 | Klausul Fitur Login | 58% | Needs Improvement |
| `AUD-102` | 08/10/2026 | Klausul Upload Spesifikasi PDF | 65% | Needs Improvement |
| `AUD-103` | 08/10/2026 | Klausul Riwayat Audit Log | 95% | Passed |

---

## 💾 5. Sampel Ekspor Laporan Hasil Evaluasi (JSON)

### A. Data Input
Pengguna menekan tombol **"Export/Download Hasil"** dan memilih format berkas **JSON**.

### B. Data Output (Payload Berkas JSON)
```json
{
  "audit_id": "AUD-2026-001",
  "timestamp": "2026-10-08T18:00:00Z",
  "quality_score": 58,
  "total_defects": 3,
  "findings": [
    {
      "category": "Ambiguity",
      "text_segment": "sangat cepat",
      "suggestion": "Tentukan parameter batas waktu spesifik (misal: < 2 detik)."
    },
    {
      "category": "Non-Testable",
      "text_segment": "user-friendly",
      "suggestion": "Ganti dengan kriteria navigasi atau standar UI/UX spesifik."
    },
    {
      "category": "Passive Voice",
      "text_segment": "harus disimpan",
      "suggestion": "Ubah menjadi kalimat aktif dengan aktor yang jelas (User POV)."
    }
  ],
  "suggested_rewrite": "Sebagai pengguna, saya ingin memverifikasi kredensial login dalam waktu kurang dari 2 detik agar dapat langsung mengakses halaman dashboard utama.",
  "acceptance_criteria": {
    "given": "Pengguna berada di halaman login",
    "when": "Pengguna memasukkan email dan kata sandi yang valid lalu menekan tombol Login",
    "then": "Sistem memvalidasi kredensial dan mengalihkan ke dashboard dalam waktu < 2 detik"
  }
}
```
