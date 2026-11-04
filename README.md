# ReqLint: Agile User Story Quality Assurance & INVEST Linter

Automated Quality Assurance & Ambiguity Detection Tool exclusively for **Agile User Stories** based on the **INVEST Criteria** (*Independent, Negotiable, Valuable, Estimable, Small, Testable*) and the **Connextra Template** (*Role - Action - Benefit*).

> 📢 **Pusat Dokumentasi Terpadu**:  
> Seluruh dokumentasi proyek, spesifikasi sistem (SRS), analisis proses bisnis (BPMN), presentasi (Pitch Deck), arsitektur, dan pedoman anotasi telah dikonsolidasikan dalam format Markdown di:  
> 👉 **[docs/README.md](file:///d:/portfolio/AI/reqlint/docs/README.md)** | **[Laporan Proyek](file:///d:/portfolio/AI/reqlint/docs/laporan_proyek.md)**

---

## 🚀 Status Capaian Sistem

| Modul / Domain | Artefak & Capaian Kunci | Status |
|---|---|:---:|
| **Dokumentasi Terpadu** | [docs/](file:///d:/portfolio/AI/reqlint/docs/) (SRS, BPMN, Pitch Deck, Data Mockup, Arsitektur, Pedoman INVEST) | ✅ Lengkap |
| **Metodologi & Pedoman Anotasi** | [pedoman_anotasi_invest.md](file:///d:/portfolio/AI/reqlint/docs/pedoman_anotasi_invest.md) (v0.9) & [invest_criteria.json](file:///d:/portfolio/AI/reqlint/pm-docs/rubrics/invest_criteria.json) | ✅ Selesai |
| **Korpus Data 1.000 User Stories** | 500 ID + 500 EN ([invest_corpus_1000.csv](file:///d:/portfolio/AI/reqlint/ai-engine/data/invest_corpus_1000.csv)) dari Dalpiaz & PPL | 🚀 Selesai |
| **Engine Perturbasi Terkontrol** | Modul injeksi cacat ortogonal I, N, V, E, S, T ([perturbation_engine.py](file:///d:/portfolio/AI/reqlint/ai-engine/data_pipeline/perturbation_engine.py)) | ✅ Selesai |
| **Isolasi Evaluasi (Test Set)** | 100% Cerita Alami (0% Sintetis / 0% Perturbasi pada Test Set) | ✅ Terverifikasi |
| **Core NLP Engine Dwibahasa** | Deteksi Connextra, INVEST Smells, & Acceptance Criteria ([nlp_pipeline.py](file:///d:/portfolio/AI/reqlint/ai-engine/ai_module/nlp_pipeline.py)) | ✅ Selesai |
| **Backend & Frontend Full-Stack** | FastAPI User Story Schema ([requirements.py](file:///d:/portfolio/AI/reqlint/backend/app/api/v1/endpoints/requirements.py)) & Next.js Editor ([RequirementEditor.tsx](file:///d:/portfolio/AI/reqlint/frontend-qa/src/components/editor/RequirementEditor.tsx)) | ✅ Siap Pakai |

---

## 👥 Role-Based Project Workspaces (4 Team Members)

Each team member has a dedicated, isolated workspace directory:

| Member & Role | Workspace Directory | Documentation |
|---|---|---|
| **Member 1: PM & Architect** | `pm-docs/` | [docs/arsitektur_dan_integrasi.md](file:///d:/portfolio/AI/reqlint/docs/arsitektur_dan_integrasi.md) |
| **Member 2: AI / NLP Engineer** | `ai-engine/` | [docs/pedoman_anotasi_invest.md](file:///d:/portfolio/AI/reqlint/docs/pedoman_anotasi_invest.md) |
| **Member 3: Backend Engineer** | `backend/` | [docs/arsitektur_dan_integrasi.md](file:///d:/portfolio/AI/reqlint/docs/arsitektur_dan_integrasi.md) |
| **Member 4: Frontend + QA Engineer** | `frontend-qa/` | [docs/mockup_data.md](file:///d:/portfolio/AI/reqlint/docs/mockup_data.md) |


---

## 🌐 Bilingual Support (Indonesian & English)

ReqLint's AI engine automatically detects whether the input User Story is written in **Indonesian (`id`)** or **English (`en`)** and applies tailored NLP syntax checks, INVEST smell matchers, and Acceptance Criteria rewrites.

### Example Indonesian User Story Audit
- **Input**: *"Sebagai pembeli, saya sebaiknya dapat membayar transaksi dengan cepat."*
- **Flaws Flagged**:
  - `MISSING_BENEFIT_ID` (*INVEST: Valuable* - tidak ada klausa *sehingga/agar/supaya*)
  - `WEAK_DIRECTIVE_ID` (*INVEST: Testable* - kata lemah *sebaiknya/dapat*)
  - `SUBJECTIVE_ADJECTIVE_ID` (*INVEST: Estimable & Testable* - kata sifat tak terukur *cepat*)
- **Suggested INVEST Rewrite**:
  *"Sebagai pembeli, saya ingin membayar transaksi menggunakan e-wallet, sehingga pesanan segera diproses tanpa menunggu lama.<br><br>**Kriteria Penerimaan (Acceptance Criteria):**<br>- Given saldo e-wallet mencukupi<br>- When pembeli menekan tombol bayar<br>- Then sistem memproses pembayaran dalam waktu < 3 detik dan menampilkan notifikasi sukses."*

### Example English User Story Audit
- **Input**: *"As a buyer, I should be able to checkout easily."*
- **Flaws Flagged**:
  - `MISSING_BENEFIT_EN` (*INVEST: Valuable* - missing *so that* clause)
  - `WEAK_DIRECTIVE_EN` (*INVEST: Testable* - weak modal *should*)
  - `SUBJECTIVE_ADJECTIVE_EN` (*INVEST: Estimable & Testable* - subjective adverb *easily*)
- **Suggested INVEST Rewrite**:
  *"As a buyer, I want to checkout using saved payment details, so that I can complete my order in fewer than 3 clicks.<br><br>**Acceptance Criteria:**<br>- Given the buyer has a saved card<br>- When the buyer confirms the order<br>- Then checkout completes in < 2 seconds with an order ID."*

---

## 🚀 Running Full Stack with Docker Compose

```bash
docker-compose up --build
```

- **Frontend UI**: http://localhost:3000
- **FastAPI Docs**: http://localhost:8000/docs

