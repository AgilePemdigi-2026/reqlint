# THREE_EVALUATOR_ACCEPTANCE (Task 07)

**Metode:** acceptance testing live — **cerita yang sama** dianotasi ke ketiga evaluator pada backend lokal (`localhost:8000`, setelah migrasi DB), hasil diambil dari `GET /audits/{id}`.
**Input (sama untuk semua):** *"As a manager, I want to export the monthly report in CSV format by clicking the export button, so that I can archive it."*
**ID audit:** rule_based=12, traditional_ml=13, llm=14.

## 1. Hasil aktual (side-by-side)

| Aspek | Rule-Based (12) | Traditional ML (13) | LLM/SLM (14) |
|---|---|---|---|
| status | COMPLETED | COMPLETED | **FAILED (eksplisit)** |
| evaluator tercatat | rule_based | traditional_ml | llm |
| model_version | null (deterministik) | **2.1.0-srs-hybrid** | null (mock tidak dinilai) |
| skor kualitas (0–100) | 95.0 (penalty internal) | 66.7 (framework equal-weight 4/6) | — |
| verdict | FAIL | FAIL | — |
| dimensi I / N / V / E / S / T | IE / IE / **PASS** / IE / IE / **FAIL** | PASS / **FAIL** / **FAIL** / PASS / PASS / PASS | — |
| assessed dimensions | valuable, testable (2/6 — jujur) | semua 6 (genuine model) | — |
| findings span | 1 (AMBIGUITY — "cepat") | 0 (ML = verdict+confidence, tanpa span — honest) | — |
| generation | DONE | DONE | tidak berjalan (evaluator gagal dulu) |
| evaluator_error_code | — | — | `LLM_EVALUATOR_UNAVAILABLE` |

**Verdict preservation:** skor rule_based tetap 95.0 — identik sebelum & sesudah generation (LLM advisory tidak memotong skor). Terkonfirmasi juga di test `test_rule_based_audit_verdict_preserved_against_llm_penalty`.

## 2. Menjelaskan perbedaan (tanpa menciptakan kesetaraan)

1. **Rule-Based 95.0 vs ML 66.7** — mekanisme berbeda: Rule-Based menghukum kategori cacat yang dideteksinya (di sini hanya AMBIGUITY), sementara ML mengklasifikasi 6 dimensi langsung dari 23 fitur (untuk cerita ini model menilai negotiable & valuable gagal — konsisten dgn klausul manfaat yang tak eksplisit dan detail preskriptif "by clicking the export button").
2. **Coverage dimensi berbeda secara jujur**: Rule-Based hanya menilai V/T (detektor I/N/E/S belum ada) → 4 dimensi IE; ML/LLM menilai keenamnya. Ini **bukan inkonsistensi** — memang batas kemampuan detektor, ditandai eksplisit.
3. **LLM FAILED** pada lingkungan ini bukan defect: default `SLM_PROVIDER=mock` sengaja **tidak boleh** menyamar sebagai analisis LLM nyata (Task 06). Dengan provider nyata, jalurnya sudah teruji via mocked transport.
4. **Tidak ada perata-rataan** antar-evaluator; tiap audit menyimpan evaluator + model_version sendiri; reanalyze mempertahankan evaluator terpilih (teruji: `test_reanalyze_reuses_persisted_evaluator`).

## 3. Checklist acceptance per evaluator

### Rule-Based
- [x] Default evaluator (payload tanpa `evaluator` → rule_based).
- [x] Scoring penalty internal utuh (95.0; `skor_awal == skor_kualitas` — LLM advisory tidak memotong).
- [x] Dimensi tak didukung = IE eksplisit (`EVALUATOR_UNSUPPORTED_DIMENSION`), tidak menjadi PASS/FAIL.
- [x] Verdict tidak diubah generation.

### Traditional ML
- [x] Keenam pipeline dimensi ter-load & `predict_proba` dijalankan (inference nyata).
- [x] Interpretasi konsisten: `p ≥ 0.5 → PASS`, confidence = proba (0–1).
- [x] Model version terlihat user (`model_version` + badge UI).
- [x] Artifact missing/corrupt → error eksplisit (`test_ml_missing_artifact…`, `test_ml_corrupt_artifact…`).
- [x] Tidak ada fallback regex di jalur ML.
- [x] UI membedakan **confidence model** (per dimensi, di kontrak) dari **skor kualitas** (framework) — tidak digabung/ditukar.

### LLM/SLM
- [x] Mock provider = gagal eksplisit, tanpa penyamaran.
- [x] Transport mocked: parsing label valid + coercing off-contract → IE (teruji).
- [x] Provider failure tidak mengganti evaluator.
- [ ] **Live provider (Groq/Ollama): PENDING** — menunggu kredensial (lihat DEPLOYMENT_VALIDATION).

### Cross-evaluator
- [x] Identitas evaluator tercatat per audit & tampil di detail.
- [x] Findings/evidence attributable ke evaluator terpilih (rule_based: span; ML/LLM: dimensi).
- [x] Tidak ada averaging antar-evaluator; tidak ada klaim kesetaraan.
- [x] Reanalyze mempertahankan evaluator (`test_reanalyze_reuses_persisted_evaluator`).
