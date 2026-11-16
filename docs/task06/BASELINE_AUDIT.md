# BASELINE_AUDIT — Task 06 (Phase 0)

**Tanggal:** 2026-11-13 · **HEAD baseline:** `4d6f53c` (`fix/frontend-docker-npm-ci`) — sesuai brief; diverifikasi aktual.
**Working tree:** 0 modifikasi tracked; 25 entri untracked (dokumen riset/audit Task 01–04C + arsip) — **dipertahankan apa adanya**, tidak dibersihkan.

## 1. Baseline test (dijalankan SEBELUM perubahan Task 06)

| Suite | Perintah | Hasil aktual |
|---|---|---|
| Backend pytest | `python -m pytest backend/tests -q` | **71 passed** (25,7 s) |
| Frontend vitest | `npx vitest run` (frontend-qa) | **35 passed** (4 file) |
| BDD pytest-bdd (backend/tests/bdd) | ikut dalam suite pytest / `python run_bdd.py` | hijau (32 skenario; terverifikasi ulang pasca-implementasi §TEST_RESULTS) |

## 2. Lingkungan

- Python 3.14.2 dengan **fastapi, sklearn 1.8.0, pytest, spacy, joblib sudah terinstal** → backend & ML inference dapat diuji lokal.
- Catatan versi: bundle ML dilatih dengan sklearn **1.7.2**; lingkungan lokal 1.8.0 → `InconsistentVersionWarning` (fungsional; Docker di-pin 1.7.2 — lihat IMPLEMENTATION_REPORT).
- Node v24.13.0 + npm 11.6.2; `frontend-qa/node_modules` tersedia.
- Docker: **tidak tersedia** di mesin ini → build image diverifikasi secara statis (bukan build aktual).

## 3. Discovery implementasi (verifikasi ulang Task 05 — tetap akurat)

- **Evaluator A Rule-Based**: `nlp_stage1.py` + `scoring.py`; terintegrasi `/lint` + pipeline audit; evidence span (`highlight_start/end`) tersimpan di TemuanCacat; ditampilkan FindingsTable.
- **Evaluator B Traditional ML**: `invest_ml_service.py` + bundle `pm-docs/rubrics/reqlint_invest_models.pkl` (v2.1.0-srs-hybrid, 23 fitur, 6 pipeline StandardScaler→LogReg, `predict_proba` ✓, metrics embedded). Hanya endpoint legacy; UI tidak terjangkau; bundle tidak ikut image; sklearn tidak di requirements.
- **Evaluator C LLM**: `nlp_stage2.py` (mock/Groq/Ollama); terintegrasi pipeline (rewrite + AC + invest flags).
- **Shared generator**: `nlp_stage2.py` sudah menjadi generator tunggal, tetapi (a) invest flags LLM mengubah skor (−4/kriteria), (b) `stage1_findings` tidak masuk prompt, (c) mock menghasilkan invest None (honest).
- **Scoring aktual (audit dgn keputusan INVEST-scoring Task 06):**
  - Rule-based: penalty-based 0–100 (`100 − Σ(penalty × severity)`; AMBIGUITY 8, PASSIVE 6, WEAK 5, TIDAK_LENGKAP 15; multi-story = rata-rata) — **mekanisme internal dipertahankan sebagai skor utama**.
  - Traditional ML: **tidak punya skor 0–100** — keluaran asli = 6 dimensi verdict + `predict_proba` (confidence). Overall 0–100 dihitung via framework equal-weighted (bukan diarang).
  - LLM: label 6 kriteria dari LLM → overall via framework yang sama.
  - Titik pelanggaran verdict yang ditemukan: `audit_service` Stage-2 lama memanggil `calculate_score(..., invest_results=invest_flags)` → −4/criteria mengubah skor Rule-Based.
- **Frontend**: dual-mode editor (backend→fallback lokal), adapter memetakan `temuan` → findings dengan highlight; `BackendAuditCard` tetap tak ter-mount.
- **Reset password**: token dibuat (hash 1 jam) tetapi **tidak dikirim** (tanpa SMTP).
- **ISO labeling**: SummaryCard meter "ISO 29148" + breakdown heuristik (`modifiable = 80` konstanta, dst.); landing "Dibangun di atas ISO 29148".

## 4. Keputusan desain tambahan (owner) — integrasi ke Task 06

**Scoring framework = INVEST, skala 0–100, initial equal weighting.** Integrasi (tanpa membatalkan pekerjaan):

1. Mekanisme internal tiap evaluator dipertahankan; **adapter** menyajikan hasil dalam kontrak bersama (`evaluation_contract.py`).
2. Rule-based: skor utama = mekanisme penalty internal (dipertahankan); dimensi INVEST diturunkan **hanya** dari kategori yang benar-benar dideteksi (V ← TIDAK_LENGKAP; T ← AMBIGUITY/WEAK_DIRECTIVE/PASSIVE_VOICE); I/N/E/S = INSUFFICIENT_EVIDENCE (`EVALUATOR_UNSUPPORTED_DIMENSION`) — tidak diarang.
3. Traditional ML: 6 dimensi genuin dari `predict_proba` (verdict p≥0.5, confidence = proba); overall 0–100 = equal-weighted over 6 dimensi. **Limitasi jujur**: 10 fitur konteks (similarity/posisi kategori) memakai default netural pada mode single-story.
4. LLM: 6 dimensi dari klasifikasi LLM; overall = framework yang sama.
5. Kualitas (score) ≠ confidence ≠ findings ≠ evidence ≠ rekomendasi AI — field terpisah dalam kontrak.
6. Generator tidak mengubah skor/verdict (verdict preservation, teruji).
7. Re-evaluation (reanalyze) memakai evaluator + model_version yang tersimpan di baris audit → perbandingan before/after valid.
8. Ketiga evaluator tidak pernah dirata-rata.
