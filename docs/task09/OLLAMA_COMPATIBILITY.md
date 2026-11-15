# OLLAMA / SLM COMPATIBILITY — Task 09 (Phase 6)

## Status: reviewed, code-compatible, **not live-verified** (no Ollama runtime in this environment)

Ollama support already exists in the architecture (`SLM_PROVIDER=ollama` branch in `nlp_stage2._call_provider`)
and was **preserved untouched** by Task 09. Per the task constraints: Ollama is not required for the Groq
integration to pass, no local models were installed, and a cloud LLM (Groq) is never described as a local SLM.

## What was verified by code inspection

| Aspect | Implementation | Assessment |
|---|---|---|
| Base URL config | `SLM_BASE_URL` (default `http://localhost:11434`) | ✅ standard |
| Endpoint | `POST {base}/api/generate`, `stream: false`, `format: "json"` | ✅ Ollama native JSON mode |
| Model config | `SLM_MODEL` (default `phi3:mini`) | ✅ |
| Response parsing | `resp.json()["response"]` → shared `_extract_json` | ✅ fenced/brace tolerant |
| Label mapping | off-contract labels → `INSUFFICIENT_EVIDENCE` + `PROVIDER_LABEL_INVALID` | ✅ same as Groq path |
| Timeout | `SLM_TIMEOUT_SECONDS` (now default 20) | ✅ appropriate for local hardware |
| Error handling | now benefits from Task 09 typed mapping: connection refused → `LLM_PROVIDER_UNREACHABLE`; timeout → `LLM_PROVIDER_TIMEOUT`; invalid JSON → `LLM_INVALID_RESPONSE` (one retry) | ✅ improved by Task 09 |
| Evaluator identity | `provider/model` recorded in `model_version` (e.g. `ollama/phi3:mini`) | ✅ provenance distinct from cloud |
| Terminology | UI/docs distinguish cloud LLM provider (Groq) vs locally hosted SLM (Ollama) | ✅ |

## Setup & validation steps (for an environment with Ollama)

1. Install Ollama and pull a small instruct model:
   `ollama pull phi3:mini` (or another JSON-capable small model).
2. Configure `backend/.env` — **exactly one** SLM block (duplicate keys = last one wins):
   ```
   SLM_PROVIDER=ollama
   SLM_BASE_URL=http://localhost:11434
   SLM_MODEL=phi3:mini
   SLM_TIMEOUT_SECONDS=60
   ```
3. Confirm the model is served: `curl http://localhost:11434/api/tags`.
4. Run the mocked-free smoke: create an audit with `evaluator=llm` through the UI (or reuse
   `backend/scripts/task09_groq_e2e.py` with the ollama block — it exercises the same pipeline; the
   `GET /models` connectivity step is Groq-specific and will report the ollama endpoint instead).
5. Verify in the audit detail: `model_version=ollama/phi3:mini`, six INVEST dimensions labeled,
   generation status `DONE`, `ai_suggestion_source=provider`.

## Known limitations (honest, pre-existing)

- `format: "json"` constrains output to valid JSON but does not guarantee the exact schema — the existing
  retry + `LLM_INVALID_RESPONSE` mapping handles stray outputs; small models may produce more
  `INSUFFICIENT_EVIDENCE` degradations than Groq-hosted models.
- Latency depends entirely on local hardware; raise `SLM_TIMEOUT_SECONDS` accordingly.
- Not verified in this environment (no Ollama daemon); blocked item, not a defect claim.
