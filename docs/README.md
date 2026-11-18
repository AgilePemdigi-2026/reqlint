# 📚 Pusat Dokumentasi Terpadu ReqLint

Selamat datang di direktori dokumentasi terpadu proyek **ReqLint** (*Automated Agile User Story Quality Assurance via NLP*). Seluruh dokumentasi proyek, spesifikasi kebutuhan, hasil analisis proses bisnis, slide presentasi, pedoman anotasi, dan panduan teknis telah distandarkan dalam format Markdown.

Dokumentasi teknis operasional (instalasi, arsitektur, API, pengujian, deployment) berada di
**[indeks dokumentasi teknis](getting-started/installation.md)** — mulai dari
[README.md](../README.md) di root repositori.

---

## 🛠️ Dokumentasi Teknis (current, English)

| Area | Dokumen |
|---|---|
| Instalasi, development lokal, konfigurasi | [installation](getting-started/installation.md) · [local-development](getting-started/local-development.md) · [configuration](getting-started/configuration.md) |
| Arsitektur | [system-overview](architecture/system-overview.md) · [backend](architecture/backend.md) · [frontend](architecture/frontend.md) · [database](architecture/database.md) · [data-flow](architecture/data-flow.md) |
| Fitur & mesin analisis | [product-overview](features/product-overview.md) · [requirements-analysis](features/requirements-analysis.md) · [traditional-ml](features/traditional-ml.md) · [llm-evaluation](features/llm-evaluation.md) |
| API | [api-reference](api/api-reference.md) |
| Pengembangan | [testing](development/testing.md) · [troubleshooting](development/troubleshooting.md) |
| Deployment | [docker](deployment/docker.md) · [DEPLOY_COOLIFY.md](../DEPLOY_COOLIFY.md) · [DEPLOY_COOLIFY_COMPOSE.md](../DEPLOY_COOLIFY_COMPOSE.md) |

---

## 🗂️ Indeks Dokumen Proyek (deliverables & laporan)

Berikut adalah daftar dokumen deliverable yang tersedia di dalam direktori `docs/`:

| No | Dokumen | Sumber / Asal | Ringkasan Isi |
|:---:|---|---|---|
| 1 | [**SRS Spesifikasi Kebutuhan**](srs_spesifikasi_kebutuhan.md) | `UTS_I4_REQLINT_SRS.pdf` | Spesifikasi Kebutuhan Sistem lengkap berbasis standar IEEE 29148 (Deskripsi umum, 7 fitur sistem FEAT-1 s.d. FEAT-7, antarmuka eksternal, skema PostgreSQL, dan NFR). |
| 2 | [**Analisis Proses Bisnis BPMN**](bpmn_analisis_proses.md) | `Kelompok3_I4_TugasBPMN.pdf` | Pemodelan proses bisnis audit kebutuhan konvensional (*As-Is*) versus otomatis dengan ReqLint (*To-Be*), diagram Mermaid, analisis bottleneck, dan metrik efisiensi waktu. |
| 3 | [**Pitch Deck ReqLint**](pitch_deck.md) | `Requirement Analyzer Pitch Deck.pdf` | Presentasi 13 slide mencakup urgensi *Shift-Left QA*, 3 pilar solusi, arsitektur teknis, pembagian peran 4 anggota tim, roadmap 16 minggu, dan kebaruan penelitian. |
| 4 | [**Data Uji Coba & Mockup**](mockup_data.md) | `UTS_I4_REQLINT_DATA.pdf` | Contoh data input/output, kartu skor audit (58/100 vs 95/100), temuan *smells*, visual diff rekomendasi AI, kriteria penerimaan Gherkin, dan payload JSON. |
| 5 | [**Arsitektur & Integrasi Teknis**](arsitektur_dan_integrasi.md) | Konsolidasi Sistem | Arsitektur 4-layer (Next.js, FastAPI, NLP Engine, PostgreSQL), struktur workspace tim, standar envelope REST API, kode status baku, dan pipeline audit 2-tahap. *(Untuk arsitektur terkini sesuai implementasi, lihat [architecture/system-overview.md](architecture/system-overview.md).)* |
| 6 | [**Pedoman Anotasi & Data INVEST**](pedoman_anotasi_invest.md) | Konsolidasi Rubrik & Metodologi | Panduan operasional evaluasi 6 kriteria INVEST, vektor label biner bervalidasi konsensus, protokol Cohen's Kappa / PABAK, mesin perturbasi, dan pemisahan *test set* 100% alami. (Versi lengkap: [pm-docs/rubrics/pedoman_anotasi_invest.md](../pm-docs/rubrics/pedoman_anotasi_invest.md).) |
| 7 | [**Laporan Progres Proyek**](laporan_proyek.md) | `PROJECT_REPORT.md` | Laporan pencapaian implementasi, metrik kerja, kepemimpinan teknis PM, serta integrasi komponen lintas modul. |
| 8 | [**Pengujian BDD (Behavior-Driven Development)**](bdd_testing.md) | Quality Assurance & BDD Suite | Suite pengujian BDD berbasis Python (`pytest-bdd`) mencakup 8 modul fitur, 32 skenario Gherkin (ISO 29148, INVEST, SEC-4), dan panduan eksekusi pengujian. *(Suite kini berisi 10 file / 34 skenario; ringkasan lengkap: [development/testing.md](development/testing.md).)* |

Selain deliverable di atas, `docs/` juga memuat paket proses dan laporan kerja per task:
`annotation_preparation/` (paket anotasi Task 04), `task04c_research_consolidation/`,
serta `task06/`–`task10/` (laporan baseline, implementasi, hasil tes, dan release readiness).

---

## 🔍 Panduan Navigasi Cepat Berdasarkan Kebutuhan

* **Ingin menjalankan proyek secara lokal?** 👉 [getting-started/installation.md](getting-started/installation.md)
* **Ingin memahami arsitektur sesuai implementasi?** 👉 [architecture/system-overview.md](architecture/system-overview.md)
* **Ingin memahami alur bisnis & efisiensi proses?** 👉 [bpmn_analisis_proses.md](bpmn_analisis_proses.md)
* **Ingin melihat gambaran umum & pitch deck proyek?** 👉 [pitch_deck.md](pitch_deck.md)
* **Ingin mengintegrasikan Frontend dengan Backend API?** 👉 [api/api-reference.md](api/api-reference.md)
* **Ingin mempelajari detail fitur sistem & skema database?** 👉 [srs_spesifikasi_kebutuhan.md](srs_spesifikasi_kebutuhan.md) · [architecture/database.md](architecture/database.md)
* **Ingin memahami evaluator Traditional ML / LLM?** 👉 [features/traditional-ml.md](features/traditional-ml.md) · [features/llm-evaluation.md](features/llm-evaluation.md)
* **Ingin berkontribusi pada pelabelan dataset dan aturan NLP?** 👉 [pedoman_anotasi_invest.md](pedoman_anotasi_invest.md)
* **Ingin menjalankan pengujian?** 👉 [development/testing.md](development/testing.md) · [bdd_testing.md](bdd_testing.md)
* **Ingin men-deploy ke Docker/Coolify?** 👉 [deployment/docker.md](deployment/docker.md) · [DEPLOY_COOLIFY.md](../DEPLOY_COOLIFY.md)
