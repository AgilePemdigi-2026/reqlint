# TEST_RESULTS (Task 06)

**Semua angka di bawah hasil eksekusi nyata di lingkungan ini** (Python 3.14.2, sklearn 1.8.0 lokal, Node 24.13). Baseline diambil SEBELUM perubahan.

## Backend pytest

| Fase | Perintah | Hasil |
|---|---|---:|
| Baseline (sebelum Task 06) | `python -m pytest backend/tests -q` | **71 passed** (25,7 s) |
| Checkpoint pasc-implementasi backend | idem | 71 passed (setelah perbaikan circular-reference serialization) |
| Final (71 lama + 20 baru) | idem | **91 passed** (26,5 s) |
| Task 06 tests saja | `pytest backend/tests/test_task06_evaluators.py` | **20 passed** (7,2 s) |

## Frontend

| Fase | Perintah | Hasil |
|---|---|---:|
| Baseline vitest | `npx vitest run` | 35 passed |
| Final vitest (35 + 3 baru) | idem | **38 passed** (4 file) |
| Type-check | `npx tsc --noEmit` | clean (setelah perbaikan return-type adapter) |
| Production build | `npx next build` | **sukses** (exit 0) |

## BDD (pytest-bdd, backend/tests/bdd — 01 s.d. 08)

| Suite | Hasil |
|---|---:|
| `python run_bdd.py` (semua skenario 01–08, termasuk siklus audit penuh, ownership SEC-4, export 3 format) | **32 passed** (14,3 s) |

## Live smoke test (uvicorn localhost:8000, real DB migration ran)

| Skenario | Hasil |
|---|---|
| `GET /health` | ✅ `{"db":"up",...}` — migrasi kolom `evaluator/model_version` berhasil pada DB eksisting |
| Register + Login | ✅ 201/200 |
| Audit evaluator `rule_based` | ✅ COMPLETED; evaluator=rule_based; skor 95.0 (penalty mechanism); verdict FAIL; dims V=PASS, T=FAIL, I/N/E/S=IE; `skor_awal == skor_kualitas` (**verdict preserved — tanpa penalty LLM**); generation DONE |
| Audit evaluator `traditional_ml` | ✅ COMPLETED; **genuine inference** — model_version `2.1.0-srs-hybrid`, 6 dimensi berlabel dari `predict_proba` (confidences 0–1), skor framework 66.7 (4/6 = equal-weight); generation DONE |
| Audit evaluator `llm` (provider=mock) | ✅ FAILED eksplisit: `evaluator_error_code = LLM_EVALUATOR_UNAVAILABLE` — **tanpa fallback ke mock/rule-based** |
| Invalid evaluator (`encoder`) | ✅ 422 `INVALID_EVALUATOR` |
| Reanalyze ML | ✅ evaluator + model_version bertahan (before/after sebanding) |

## Keterbatasan yang diakui

1. **Docker build & compose validation**: Docker tidak tersedia di mesin ini → diverifikasi statis (bundle COPY path = path kandidat loader; sklearn pin 1.7.2 = versi bundle). Build image aktual menunggu lingkungan Docker.
2. **sklearn versi lokal 1.8.0 vs bundle 1.7.2** → `InconsistentVersionWarning` saat inference lokal (fungsional). Docker pin `scikit-learn==1.7.2` menghilangkan mismatch di deployment.
3. **SMTP real-email delivery**: diuji dengan **mocked SMTP** (20 test); pengiriman email nyata menunggu kredensial SMTP deployment (variabel terdokumentasi).
4. **Live UI walkthrough via proxy frontend**: proxy `/api` frontend di-build dengan target `http://backend:8000` (hostname compose) → tidak dapat diuji lokal tanpa rebuild; smoke dilakukan langsung ke API backend. Halaman frontend sendiri terverifikasi build + serving 200.
5. Provider LLM nyata (Groq/Ollama) tidak tersedia di lingkungan ini → klasifikasi LLM diuji dengan transport mock yang mengembalikan JSON valid + kasus label off-contract (coerce → IE); panggilan jaringan nyata menunggu kredensial.
