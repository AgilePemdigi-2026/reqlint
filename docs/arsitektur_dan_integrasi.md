# 🏗️ Arsitektur Sistem & Panduan Integrasi ReqLint

Dokumen ini menggabungkan ringkasan arsitektur tingkat tinggi (*System Architecture Overview*) dan panduan integrasi teknis (*Integration Guide*) antara Backend, Frontend-QA, dan modul AI/NLP.

---

## 1. Arsitektur Sistem (High-Level Architecture)

ReqLint adalah platform penjaminan mutu dan audit otomatis *User Story* tangkas berbasis kriteria **INVEST** (*Independent, Negotiable, Valuable, Estimable, Small, Testable*) dan format standar **Connextra** (*Role - Action - Benefit*).

### 1.1 Diagram Arsitektur Sistem

```
+-------------------------------------------------------------------------------+
|                             FRONTEND + QA LAYER                               |
| Next.js 14 + Tailwind CSS + Agile Story Editor (Live Smells & INVEST Score)  |
+---------------------------------------+---------------------------------------+
                                        | HTTP / REST API (JSON)
                                        v
+-------------------------------------------------------------------------------+
|                             BACKEND API LAYER                                 |
| FastAPI (Python 3.11) + Pydantic v2 + PostgreSQL (Audit History) + Redis      |
+---------------------------------------+---------------------------------------+
                                        | Internal Python Module / Async Pipeline
                                        v
+-------------------------------------------------------------------------------+
|                            AI / NLP ENGINE LAYER                              |
| Bilingual Language Detector (ID / EN)                                         |
|  ├── Lapisan 1: Syntax & Rule Matcher (spaCy POS + Regex, < 200 ms)           |
|  └── Lapisan 2: ML Classifier & LLM Rewriter (INVEST Score, Diff, Gherkin AC) |
+-------------------------------------------------------------------------------+
```

### 1.2 Struktur Workspace Terisolasi (4 Anggota Tim)
1. **`pm-docs/`**: Ruang kerja Project Manager & Sistem Arsitek (rubrik kriteria INVEST, pedoman metodologi).
2. **`ai-engine/`**: Ruang kerja AI/NLP Engineer (pipeline NLP, generator korpus 1.000 story, rule matcher).
3. **`backend/`**: Ruang kerja Backend Engineer (REST API FastAPI, skema Pydantic, PostgreSQL SQLAlchemy, Celery/Redis).
4. **`frontend-qa/`**: Ruang kerja Frontend UI & QA Engineer (Next.js 14, kartu skor audit, visual diff, Cypress E2E).

---

## 2. Standar Antarmuka REST API & Integrasi

### 2.1 Konfigurasi & Autentikasi
* **Base URL:** `http://localhost:8000/api/v1`
* **Header Autentikasi:** `Authorization: Bearer <access_token>` untuk semua endpoint terproteksi.
* **Isolasi Data Pengguna (SEC-4):** Jika pengguna mengakses ID audit milik akun lain, backend mengembalikan kode status **`404 Not Found`** (`"Data audit tidak ditemukan"`), bukan `403`, untuk mencegah kebocoran informasi (*information leakage*).

### 2.2 Format Envelope Respons Baku

#### A. Format Sukses
```json
{
  "status": "success",
  "message": "Pesan deskriptif operasional",
  "data": { ... }
}
```

#### B. Format Error
```json
{
  "status": "error",
  "message": "Pesan error untuk antarmuka pengguna",
  "error_code": "KODE_ERROR_TERSTANDAR",
  "errors": [
    { "field": "nama_field", "message": "Detail kegagalan validasi" }
  ]
}
```

### 2.3 Pesan Validasi Standar (SRS Compliance)
Gunakan string baku berikut untuk pencocokan toast/notifikasi di antarmuka frontend:
* **Pendaftaran Berhasil (201):** `"Pendaftaran berhasil, silakan masuk"`
* **Email Duplikat (409):** `"Email sudah terdaftar"`
* **Format Sandi Tidak Cocok (422):** `"Format sandi tidak valid atau konfirmasi sandi tidak cocok"`
* **Login Gagal (401):** `"Kredensial tidak valid"`
* **Draf Kosong (422):** `"Draf kebutuhan tidak boleh kosong"`
* **Bukan File PDF (422):** `"Format file tidak valid, harap unggah dokumen .pdf"`
* **PDF Hasil Pindai / Gambar (422):** `"PDF tidak memuat lapisan teks (hasil pemindaian), harap unggah dokumen digital"`
* **File Melebihi Batas (413):** `"Ukuran file melebihi batas 10 MB"`
* **Ekstraksi Sukses (200):** `"Dokumen berhasil diekstraksi"`
* **Revisi Sukses (200):** `"Draf berhasil diperbarui"`
* **Label Skor Terkini:** `"Skor Kualitas Terkini"`

---

## 3. Alur Kerja Audit Kebutuhan 2-Tahap

```
[Register / Login] ──► Token JWT
                            │
        ┌───────────────────┴───────────────────┐
  Input Teks Manual                       Upload PDF (POST /documents/upload)
        │                                       │
        └───────────────────┬───────────────────┘
                            ▼
              Mulai Audit: POST /audits
              (Respons 202 Accepted, id_audit, poll_url)
                            │
                            ▼
             Polling: GET /audits/{id_audit}/status
             (Interval ~1s hingga status == "COMPLETED")
                            │
                            ▼
                Detail: GET /audits/{id_audit}
              (Scorecard, Temuan, Diff, Gherkin AC)
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
  1-Click Apply        Edit Manual         Export Laporan
(POST /apply)        (PUT /revision)     (GET /export?format=pdf|json|md)
```

### 3.1 Peta Endpoint Utama

| Metode | Endpoint | Deskripsi | Status Code |
|---|---|---|:---:|
| `POST` | `/api/v1/auth/register` | Pendaftaran akun pengguna baru | 201 / 409 / 422 |
| `POST` | `/api/v1/auth/login` | Autentikasi akun & penerbitan token JWT | 200 / 401 |
| `POST` | `/api/v1/documents/upload` | Ekstraksi teks dari dokumen PDF | 200 / 413 / 422 |
| `POST` | `/api/v1/audits` | Memulai pipeline audit teks kebutuhan | 202 |
| `GET` | `/api/v1/audits/{id}/status` | Polling status eksekusi audit | 200 |
| `GET` | `/api/v1/audits/{id}` | Mengambil detail lengkap hasil audit | 200 / 404 |
| `POST` | `/api/v1/audits/{id}/apply` | Menerapkan rekomendasi perbaikan (1-Click) | 200 / 404 |
| `PUT` | `/api/v1/audits/{id}/revision` | Menyimpan revisi teks manual pengguna | 200 / 404 / 422 |
| `GET` | `/api/v1/audits/{id}/export` | Mengunduh berkas laporan audit (`pdf`, `json`, `md`) | 200 / 404 |
| `GET` | `/api/v1/audits/history` | Mengambil daftar riwayat audit pengguna | 200 |

---

## 4. Pipeline Analisis AI 2-Tahap

1. **Tahap 1: Deteksi Cepat Sintaks & *Smell* (Deterministic Rule Engine)**
   * Menjalankan deteksi bahasa (*ID* vs *EN*).
   * Memeriksa keberadaan klausa Connextra (*Role*, *Action*, *Benefit*).
   * Menandai *smells* kuantitatif dan kualitatif (*subjective adjectives*, *weak directives*, *vague quantifiers*, *compound conjunctions*).
   * Waktu eksekusi rata-rata: < 200 ms.

2. **Tahap 2: Evaluasi Mendalam & Rekomendasi (ML Evaluator & LLM Rewriter)**
   * Menilai 6 dimensi INVEST dengan pembobotan nilai (skala 0–100).
   * Menghasilkan teks rekomendasi yang diperbaiki (*AI-powered Rewrite*).
   * Menghasilkan kriteria penerimaan terstruktur (*Gherkin Acceptance Criteria* format *Given-When-Then*).
   * Menghitung diff kata dan karakter antara teks asli dan rekomendasi.
