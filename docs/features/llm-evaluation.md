# LLM / SLM evaluation (Evaluator C) and Stage-2 generation

The backend integrates configurable LLM providers over plain HTTP (httpx) — no LangChain at
runtime. One integration serves two distinct capabilities, implemented in
`backend/app/services/nlp_stage2.py`:

1. **Evaluator C** — `classify_story_with_llm`: classifies the six INVEST criteria
   (PASS / FAIL / INSUFFICIENT_EVIDENCE) as an alternative audit evaluator.
2. **Stage-2 generator** — `generate_response`: produces an advisory rewrite + Gherkin acceptance
   criteria that **preserves the evaluation verdict** of Phase 1 (any evaluator).

## Providers

| `SLM_PROVIDER` | Transport | Auth | Notes |
|---|---|---|---|
| `mock` (default) | none | none | Deterministic built-in demo templates. **Not AI output** — labeled `ai_suggestion_source: "mock"` and "bukan analisis AI nyata" in API/UI. |
| `ollama` | `POST {SLM_BASE_URL}/api/generate` | none | Local/self-hosted models; `SLM_MODEL` selects the model tag. |
| `openai_compatible` | `POST {SLM_BASE_URL}/v1/chat/completions` | `Authorization: Bearer $GROQ_API_KEY` | Verified against Groq (`https://api.groq.com/openai`, model e.g. `llama-3.1-8b-instant`) in Task 09. Fails fast with `LLM_PROVIDER_KEY_MISSING` when no key is configured. |

Provider and model are configurable via environment variables only (see
[../getting-started/configuration.md](../getting-started/configuration.md)); there is no per-request
model selection.

## What the LLM actually does

**Evaluator C (classification).** Sends the sanitized story with an INVEST rubric prompt; expects a
JSON payload with a `criteria` object. Provider labels are validated: only PASS / FAIL /
INSUFFICIENT_EVIDENCE are accepted, anything else is coerced to `INSUFFICIENT_EVIDENCE` with a
`PROVIDER_LABEL_INVALID` rationale. The mock provider is **refused** for this evaluator (an
LLM-requested audit must never return mock output) — with `SLM_PROVIDER=mock` the audit fails with
`LLM_EVALUATOR_UNAVAILABLE`.

**Stage-2 generation.** Grounded in the Phase-1 evaluation: when the evaluator produced INVEST
dimension verdicts, the prompt carries per-dimension labels, confidences, and rationales; for
rule-based audits it carries the findings. The output schema (explanation, recommendation,
`ai_rewrite`, `acceptance_criteria`, optional `invest_observations`) is validated and coerced
(`_coerce_generation_payload`), and adversarial drift is hardened (`_sanitize_invest_observations`
— e.g. extra "notes" keys no longer break generation). Story text is escaped against delimiter
injection before entering prompts (`_sanitize_story_text`, mitigation ML-20).

## Deterministic vs model-dependent behavior

| Deterministic | Model-dependent |
|---|---|
| Evaluator selection, contracts, scoring, findings | Classification labels (Evaluator C) |
| Mock templates (fixed content) | Rewrite text, acceptance criteria wording |
| Error mapping, retries, label coercion | The factual quality of LLM assessments |

No output of the LLM is treated as ground truth: labels are coerced to the contract, generated
content is schema-validated, and the evaluation verdict comes from Phase 1, which generation
cannot change (a generation that contradicts the evaluation is rejected rather than applied).

## Failure handling

Failures map to stable coded errors (`LLMProviderRequestError` codes surfaced as
`evaluator_error_code`): `LLM_PROVIDER_TIMEOUT`, `LLM_PROVIDER_AUTH_FAILED`, `LLM_MODEL_NOT_FOUND`,
`LLM_RATE_LIMITED`, `LLM_PROVIDER_SERVER_ERROR`, `LLM_INVALID_RESPONSE`,
`LLM_PROVIDER_KEY_MISSING`, `LLM_EVALUATOR_UNAVAILABLE`. Retry behavior: the legacy
`run_stage2` path performs one retry on transient provider errors; evaluator/generation failures
mark the audit `FAILED`/`PARTIAL` respectively and never substitute another evaluator's result.

The health endpoint reports `slm: "mock"` when the mock provider is active, and `slm: "up"`
otherwise — it does not verify provider reachability (see [../architecture/backend.md](../architecture/backend.md)).

## What the LLM does **not** do

- It does not guarantee correctness of its assessments — outputs are advisory and validated only
  for structural conformance.
- It is not used for scoring (scores come from the evaluation contract and the Stage-1 penalty
  model).
- It is not autonomous: one classification call and/or one generation call per audit; no agent
  loop, no tool use.
- With the default mock provider, no external call happens at all.

## Runtime dependency notes

`langchain-groq` is listed in `ai-engine/requirements-ai.txt` but is **not** used by the backend
runtime (its LLM calls use httpx directly); it serves the ai-engine workbench's prototype rewriter
(`ai-engine/ai_module/llm/rewriter.py`). The backend Docker image installs it as part of that
requirements file.
