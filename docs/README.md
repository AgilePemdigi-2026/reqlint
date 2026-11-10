# 📚 Pusat Dokumentasi Terpadu ReqLint

Selamat datang di direktori dokumentasi terpadu proyek **ReqLint** (*Automated Agile User Story Quality Assurance via NLP*). Seluruh dokumentasi proyek, spesifikasi kebutuhan, hasil analisis proses bisnis, slide presentasi, pedoman anotasi, dan panduan teknis telah distandarkan dalam format Markdown.

---

## 🗂️ Indeks Dokumen Proyek

Berikut adalah daftar dokumen yang tersedia di dalam direktori `docs/`:

| No | Dokumen | Sumber / Asal | Ringkasan Isi |
|:---:|---|---|---|
| 1 | [**SRS Spesifikasi Kebutuhan**](file:///d:/portfolio/AI/reqlint/docs/srs_spesifikasi_kebutuhan.md) | `UTS_I4_REQLINT_SRS.pdf` | Spesifikasi Kebutuhan Sistem lengkap berbasis standar IEEE 29148 (Deskripsi umum, 7 fitur sistem FEAT-1 s.d. FEAT-7, antarmuka eksternal, skema PostgreSQL, dan NFR). |
| 2 | [**Analisis Proses Bisnis BPMN**](file:///d:/portfolio/AI/reqlint/docs/bpmn_analisis_proses.md) | `Kelompok3_I4_TugasBPMN.pdf` | Pemodelan proses bisnis audit kebutuhan konvensional (*As-Is*) versus otomatis dengan ReqLint (*To-Be*), diagram Mermaid, analisis bottleneck, dan metrik efisiensi waktu. |
| 3 | [**Pitch Deck ReqLint**](file:///d:/portfolio/AI/reqlint/docs/pitch_deck.md) | `Requirement Analyzer Pitch Deck.pdf` | Presentasi 13 slide mencakup urgensi *Shift-Left QA*, 3 pilar solusi, arsitektur teknis, pembagian peran 4 anggota tim, roadmap 16 minggu, dan kebaruan penelitian. |
| 4 | [**Data Uji Coba & Mockup**](file:///d:/portfolio/AI/reqlint/docs/mockup_data.md) | `UTS_I4_REQLINT_DATA.pdf` | Contoh data input/output, kartu skor audit (58/100 vs 95/100), temuan *smells*, visual diff rekomendasi AI, kriteria penerimaan Gherkin, dan payload JSON. |
| 5 | [**Arsitektur & Integrasi Teknis**](file:///d:/portfolio/AI/reqlint/docs/arsitektur_dan_integrasi.md) | Konsolidasi Sistem | Arsitektur 4-layer (Next.js, FastAPI, NLP Engine, PostgreSQL), struktur workspace tim, standar envelope REST API, kode status baku, dan pipeline audit 2-tahap. |
| 6 | [**Pedoman Anotasi & Data INVEST**](file:///d:/portfolio/AI/reqlint/docs/pedoman_anotasi_invest.md) | Konsolidasi Rubrik & Metodologi | Panduan operasional evaluasi 6 kriteria INVEST, vektor label biner bervalidasi konsensus, protokol Cohen's Kappa / PABAK, mesin perturbasi, dan pemisahan *test set* 100% alami. |
| 7 | [**Laporan Progres Proyek**](file:///d:/portfolio/AI/reqlint/docs/laporan_proyek.md) | `PROJECT_REPORT.md` | Laporan pencapaian implementasi, metrik kerja, kepemimpinan teknis PM, serta integrasi komponen lintas modul. |
| 8 | [**Pengujian BDD (Behavior-Driven Development)**](file:///d:/portfolio/AI/reqlint/docs/bdd_testing.md) | Quality Assurance & BDD Suite | Suite pengujian BDD berbasis Python (`pytest-bdd`) mencakup 8 modul fitur, 32 skenario Gherkin (ISO 29148, INVEST, SEC-4), dan panduan eksekusi pengujian. |

---

## 🔍 Panduan Navigasi Cepat Berdasarkan Kebutuhan

* **Ingin memahami alur bisnis & efisiensi proses?** 👉 Baca [bpmn_analisis_proses.md](file:///d:/portfolio/AI/reqlint/docs/bpmn_analisis_proses.md).
* **Ingin melihat gambaran umum & pitch deck proyek?** 👉 Baca [pitch_deck.md](file:///d:/portfolio/AI/reqlint/docs/pitch_deck.md).
* **Ingin mengintegrasikan Frontend dengan Backend API?** 👉 Baca [arsitektur_dan_integrasi.md](file:///d:/portfolio/AI/reqlint/docs/arsitektur_dan_integrasi.md).
* **Ingin mempelajari detail fitur sistem & skema database?** 👉 Baca [srs_spesifikasi_kebutuhan.md](file:///d:/portfolio/AI/reqlint/docs/srs_spesifikasi_kebutuhan.md).
* **Ingin melihat format data masukan/keluaran dan scorecard?** 👉 Baca [mockup_data.md](file:///d:/portfolio/AI/reqlint/docs/mockup_data.md).
* **Ingin berkontribusi pada pelabelan dataset dan aturan NLP?** 👉 Baca [pedoman_anotasi_invest.md](file:///d:/portfolio/AI/reqlint/docs/pedoman_anotasi_invest.md).
* **Ingin menjalankan dan mempelajari pengujian BDD Python?** 👉 Baca [bdd_testing.md](file:///d:/portfolio/AI/reqlint/docs/bdd_testing.md).
