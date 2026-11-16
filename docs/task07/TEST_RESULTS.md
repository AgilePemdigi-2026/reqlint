# TEST_RESULTS (Task 07)

**Semua dijalankan nyata pada 2026-11-15 setelah seluruh perubahan Task 07.** Baseline Task 06: pytest 91, vitest 38, tsc clean, build sukses, BDD 32.

## Eksekusi final

| Suite | Perintah | Hasil | Δ vs Task 06 |
|---|---|---|---|
| Backend pytest (termasuk 20 test Task 06) | `python -m pytest backend/tests -q` | **91 passed** (70,2 s) | sama — tanpa regresi |
| Frontend vitest (38 + 7 export integrity) | `npx vitest run` | **45 passed** (45) | +7 baru |
| TypeScript | `npx tsc --noEmit` | **clean** (setelah perbaikan `seq` fixture) | sama |
| Production build | `npx next build` | **sukses** | sama |
| BDD runner (01–08) | `python run_bdd.py` | **32 passed** | sama |
| Live API smoke 3 evaluator | curl ke `localhost:8000` | rule_based ✅ / traditional_ml ✅ (genuine inference) / llm ✅ FAILED eksplisit | sesuai desain |
| DB migration pada DB eksisting | startup uvicorn | ✅ kolom baru ditambah idempotent; health `db: up` | — |

## Test baru Task 07 (7)

`frontend-qa/src/lib/export.test.ts` — export integrity:
1. md memuat identitas evaluator + model version.
2. md memakai label heuristik jujur (tanpa klaim "Kepatuhan: ISO 29148").
3. md memisahkan AI advisory dari findings evaluator.
4. json membawa `evaluator`/`model_version`/`ai_advisory_notes` sebagai key terpisah.
5. Tanpa meta → tidak ada klaim evaluator (null).
6. `buildExport` meneruskan meta utk md & json.
7. Advisory tidak pernah menyatu ke bagian findings.

## Defect yang ditemukan & diperbaiki di Task 07 (regression ditambah)

| Defect | Akar | Fix | Test |
|---|---|---|---|
| Advisory `ai_invest_notes` ter-render **terbalik** (flag `false` = gagal oleh LLM, UI/export menulis "lolos") | logika ternary di `audit/[id]/page.tsx` + `export.ts` | logika dibenarkan + semantik didokumentasikan (`true`=lolos, `false`=ditandai) | export.test #3 + render halaman |
| Export md/json tidak membawa identitas evaluator/model/advisory | `lib/export.ts` tidak menerima meta | `ExportMeta` + threading di `toMarkdown/toJson/buildExport` + call site halaman detail | export.test #1/#2/#4/#6 |
| `Adapter return type` tidak memuat field Task 06 (anotasi eksplisit) | return-type annotation lama | tipe diperluas + import `EvaluatorId` | adapter.test Task 06 (3 test) |
| Fixture test tanpa `seq` (Audit type) | fixture baru | `seq: 1` | — |

## Yang TIDAK dapat dieksekusi di lingkungan ini (bukan "passed")

- Docker build & compose smoke (Docker tidak terinstal).
- SMTP real-email delivery (kredensial tidak ada).
- LLM provider nyata Groq/Ollama (kredensial/tidak ada).
- UI proxy E2E via frontend lokal (target build-time `http://backend:8000`).
