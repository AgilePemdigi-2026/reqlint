# REPRODUCTION AND TRACES — Task 10 Phase 0

**Environment under test:** backend `uvicorn app.main:app` on :8000 (started 23:47, i.e. WITH Task 09 code +
fixed `.env`), frontend `next start` on :3100. All findings below are reproduced facts, not assumptions.

## 1. Database evidence (backend/reqlint.db, audits 20–28 — the reproduction batch)

Every audit 20–25: `requested evaluator` dispatched correctly and produced a real evaluation contract, but
ALL were `PARTIAL` with `generation.status=FAILED`:

```
audit=20 evaluator=llm                    status=PARTIAL gen=FAILED  skor=100.0 model=openai_compatible/openai/gpt-oss-120b
audit=21 evaluator=rule_based             status=PARTIAL gen=FAILED  skor=36.5
audit=22-25 evaluator=traditional_ml      status=PARTIAL gen=FAILED  skor=50/66.7 model=2.1.0-srs-hybrid
   generation.error = "LLM_INVALID_RESPONSE: provider output could not be parsed into the expected JSON schema"
```

Conclusions: backend dispatch integrity was intact (requested == actual; ML genuinely inferred; LLM genuinely
called Groq) — the reported "falls back to Rule-Based" was a **frontend rendering problem**, and the
"Generator: failed" was a **real backend generator bug**.

## 2. Raw provider capture (the generator root cause)

Replaying `generate_response()` with audit 20's exact inputs, capturing the raw Groq content (gpt-oss-120b):

```json
"invest_observations": {
  "independent": true,
  "notes": "No external dependencies are identified; the story can be implemented in isolation. ..."
}
```

Two independent live calls both added the free-text `notes` key. `Stage2OutputModel.invest: Dict[str, bool]`
→ pydantic ValidationError → `LLM_INVALID_RESPONSE` on both retry attempts. The earlier Task 09 E2E passed
only because that story happened to receive a clean six-key dict — the failure was content/probabilistic,
which matches "consistently displays Generator: failed" in real usage.

## 3. API traces (backend/scripts/task10_trace.py → docs/task10/api-traces/)

**Pre-fix run (audits 26–28):** dispatch correct for all three evaluators; generation FAILED for 26 (rule_based)
and 27 (ML), DONE for 28 (llm) — demonstrating the intermittent generator failure. ML dimensions present in
API response (`"negotiable": "FAIL", "valuable": "FAIL", …`) while the UI displayed none of them.

**Post-fix run (audits 35–37, all three evaluators, same story):**

```
35 rule_based     COMPLETED gen=DONE skor=95.0  requested==actual
36 traditional_ml COMPLETED gen=DONE skor=66.7  requested==actual  model=2.1.0-srs-hybrid
37 llm            COMPLETED gen=DONE skor=100.0 requested==actual  model=openai_compatible/openai/gpt-oss-120b
```

## 4. UI observations (browser against :3100)

Pre-fix:
- Login page alert: "Tidak dapat terhubung ke server backend" → **CORS disallowed origin** (curl preflight:
  `HTTP 400 Disallowed CORS origin`); BackendHealthBadge showed offline although the backend was running.
- Editor submit → `/audit/29` (ML): **no loading screen; local Rule-Based scorecard rendered instantly**
  (`loadingShown=false, localRuleBasedRendered=true` measured at t≈400 ms).
- `/audit/27` (ML, terminal): banner "Traditional ML / 2.1.0-srs-hybrid", "Generator: gagal — hasil evaluasi
  tetap tersedia", "Tahap AI gagal dijalankan…", findings table empty, ISO meter showing **67 (the ML score
  masquerading as a document-practice percentage)**, "Praktik Dokumen (heuristik) 67 · INVEST –", and **no
  dimension results anywhere** (DOM snapshot: no PASS/FAIL/rationale text).
- `/audit/[id]` returned SSR 500 (clobbered `.next`; environmental, fixed by rebuild).

Post-fix (audits 31–34, real UI clicks, screenshots in TEST_RESULTS.md):
- Processing card visible immediately after submit for all evaluators, naming the requested evaluator;
  no local scorecard flash.
- Terminal results: provenance banner "Evaluator diminta / Evaluator aktual / Model / Generator",
  score provenance line, Hasil Dimensi INVEST panel (PASS/FAIL/IE badges + confidence + rationale,
  attributed to the actual evaluator), honest "–" meters for ML/LLM.
- LLM audit 33: `Model: openai_compatible/openai/gpt-oss-120b`, `Generator: selesai (openai_compatible)`,
  contextual revision + acceptance criteria generated.
- Deliberate failure (audit 34): bogus `SLM_MODEL` → explicit failure panel "Evaluasi Gagal" with the
  localized `LLM_MODEL_NOT_FOUND` message and "— tidak ada fallback ke evaluator lain." — **no score card**.
  After restoring the model, "Analisis Ulang" from the failure panel reprocessed the SAME audit to COMPLETED
  with `evaluator=llm` preserved (retry recovery).

## 5. Database verification (post-fix, audits 31–34)

```
31 rule_based     requested/actual=rule_based/rule_based       COMPLETED gen=DONE skor=95.0
32 traditional_ml requested/actual=traditional_ml/traditional_ml COMPLETED gen=DONE skor=66.7 model=2.1.0-srs-hybrid
33 llm            requested/actual=llm/llm                     COMPLETED gen=DONE skor=100.0 model=openai_compatible/openai/gpt-oss-120b
34 llm            FAILED during bogus-model test → COMPLETED after retry, evaluator identity llm preserved
```

Each evaluator produced a DISTINCT dimension profile for the same story (RB: V=PASS/T=FAIL with I/N/E/S
honestly IE; ML: 4 PASS/2 FAIL with confidence; LLM: its own profile) — proof that the displayed evaluator is
the one that actually ran.
