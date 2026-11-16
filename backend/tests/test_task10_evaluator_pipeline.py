"""Task 10 tests: generator robustness (reproduced Groq failure), evaluator
provenance exposure, and fallback-prevention assertions.

All provider interactions are mocked and deterministic.
"""
import json
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.services.nlp_stage2 import NLPStage2Service
from app.services.audit_service import AuditService

CRIT = ["independent", "negotiable", "valuable", "estimable", "small", "testable"]


async def _register_and_login(client: AsyncClient, email: str):
    pwd = "SecretP@ss123"
    await client.post("/api/v1/auth/register", json={
        "name": "T10", "email": email, "password": pwd, "password_confirmation": pwd})
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    return {"Authorization": f"Bearer {login.json()['data']['access_token']}"}


@pytest.mark.asyncio
async def test_generation_tolerates_annotated_invest_observations():
    """Task 10 root cause (reproduced live against Groq): the model annotates
    the advisory invest_observations with extra keys (e.g. "notes") — the
    whole generation must NOT fail because of it."""
    evaluation = {"evaluator": "llm", "verdict": "PASS", "score": 100.0, "findings": []}
    provider_payload = {
        "explanation": "Story is clear.",
        "recommendation": "Add measurable targets.",
        "ai_rewrite": "As a user, I want to log in within 2 seconds so that I can work without delay.",
        "acceptance_criteria": [{"given": "g", "when": "w", "then": "t"}],
        "invest_observations": {
            "independent": True,
            "notes": "No external dependencies are identified; adding metrics would help.",
        },
    }
    with patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "openai_compatible"), patch.object(
        NLPStage2Service, "_call_provider", new_callable=AsyncMock,
        return_value=json.dumps(provider_payload),
    ):
        out = await NLPStage2Service.generate_response(
            "As a user, I want the login process to be fast.", evaluation)
    assert out["verdict_preserved"] == "PASS"
    assert out["score_preserved"] == 100.0
    assert out["ai_invest_observations"] == {"independent": True}  # annotation dropped
    assert out["provider"] == "openai_compatible"


@pytest.mark.asyncio
async def test_generation_tolerates_lenient_boolean_values():
    evaluation = {"evaluator": "llm", "verdict": "FAIL", "score": 50.0, "findings": []}
    provider_payload = {
        "explanation": "x", "recommendation": "y",
        "ai_rewrite": "r", "acceptance_criteria": [],
        "invest_observations": {"independent": "true", "negotiable": "false",
                                "valuable": 1, "estimable": 0},
    }
    with patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "openai_compatible"), patch.object(
        NLPStage2Service, "_call_provider", new_callable=AsyncMock,
        return_value=json.dumps(provider_payload),
    ):
        out = await NLPStage2Service.generate_response("As a user, I want X so that Y.", evaluation)
    assert out["ai_invest_observations"] == {"independent": True, "negotiable": False,
                                             "valuable": True, "estimable": False}


@pytest.mark.asyncio
async def test_generation_survives_fully_uncoercible_invest_object():
    evaluation = {"evaluator": "llm", "verdict": "FAIL", "score": 40.0, "findings": []}
    provider_payload = {
        "explanation": "x", "recommendation": "y", "ai_rewrite": "r",
        "acceptance_criteria": [{"given": "g", "when": "w", "then": "t"}],
        "invest_observations": {"independent": {"label": "FAIL", "reason": "nested"},
                                "summary": "text"},
    }
    with patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "openai_compatible"), patch.object(
        NLPStage2Service, "_call_provider", new_callable=AsyncMock,
        return_value=json.dumps(provider_payload),
    ):
        out = await NLPStage2Service.generate_response("As a user, I want X so that Y.", evaluation)
    # Advisory object dropped entirely — generation itself still succeeds.
    assert out["ai_invest_observations"] is None
    assert out["verdict_preserved"] == "FAIL"


@pytest.mark.asyncio
async def test_generation_prompt_receives_dimension_evidence_for_ml():
    """ML audits have no span findings — the generator prompt must carry the
    per-dimension verdicts + rationales so recommendations cite real evidence."""
    evaluation = {
        "evaluator": "traditional_ml", "verdict": "FAIL", "score": 66.7, "findings": [],
        "dimensions": {
            "negotiable": {"label": "FAIL", "confidence": 0.81,
                           "rationale": "prescribes a specific UI layout"},
            "testable": {"label": "PASS", "confidence": 0.7, "rationale": "measurable"},
        },
    }
    captured = {}

    async def fake_call(system_prompt, user_prompt):
        captured["system"] = system_prompt
        captured["user"] = user_prompt
        return json.dumps({
            "explanation": "e", "recommendation": "r", "ai_rewrite": "w",
            "acceptance_criteria": [], "invest_observations": {"testable": True},
        })

    with patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "openai_compatible"), patch.object(
        NLPStage2Service, "_call_provider", side_effect=fake_call,
    ):
        await NLPStage2Service.generate_response("As a manager, I want reports fast.", evaluation)
    assert "negotiable: FAIL" in captured["user"]
    assert "prescribes a specific UI layout" in captured["user"]
    assert "confidence 81%" in captured["user"]
    # The strict advisory-schema instruction is present (belt & suspenders).
    assert "ONLY the six boolean keys" in captured["system"]


def test_extract_json_handles_fenced_json_with_surrounding_prose():
    fenced = 'Sure — here is the analysis:\n```json\n{"explanation": "ok", "n": 2}\n```\nHope that helps.'
    out = NLPStage2Service._extract_json(fenced)
    assert out == {"explanation": "ok", "n": 2}


def test_extract_json_handles_raw_json_with_prose():
    raw = 'The result is {"explanation": "ok", "n": 2} as requested.'
    out = NLPStage2Service._extract_json(raw)
    assert out == {"explanation": "ok", "n": 2}


def test_extract_json_handles_fenced_nested_json():
    fenced = '```json\n{"criteria": {"independent": {"label": "PASS"}}}\n```'
    out = NLPStage2Service._extract_json(fenced)
    assert out["criteria"]["independent"]["label"] == "PASS"


@pytest.mark.asyncio
async def test_detail_exposes_requested_and_actual_evaluator(client: AsyncClient):
    headers = await _register_and_login(client, "t10_prov@example.com")
    # ML audit: genuine inference, no provider needed.
    create = await client.post("/api/v1/audits", json={
        "konten": "As a user, I want to export the report in CSV so that I can archive it.",
        "evaluator": "traditional_ml"}, headers=headers)
    id_audit = create.json()["data"]["id_audit"]
    await AuditService.run_pipeline(id_audit)
    data = (await client.get(f"/api/v1/audits/{id_audit}", headers=headers)).json()["data"]
    assert data["requested_evaluator"] == "traditional_ml"
    assert data["actual_evaluator"] == "traditional_ml"
    assert data["evaluation"]["evaluator"] == "traditional_ml"
    assert data["model_version"] == "2.1.0-srs-hybrid"


@pytest.mark.asyncio
async def test_failed_llm_audit_has_no_actual_evaluator_and_no_scorecard_success(client: AsyncClient):
    headers = await _register_and_login(client, "t10_fail@example.com")
    create = await client.post("/api/v1/audits", json={
        "konten": "As a user, I want X so that Y.", "evaluator": "llm"}, headers=headers)
    id_audit = create.json()["data"]["id_audit"]
    # Suite conftest pins SLM_PROVIDER=mock -> LLM evaluator fails explicitly.
    await AuditService.run_pipeline(id_audit)
    data = (await client.get(f"/api/v1/audits/{id_audit}", headers=headers)).json()["data"]
    assert data["status_audit"] == "FAILED"
    assert data["requested_evaluator"] == "llm"
    assert data["actual_evaluator"] is None          # nothing produced the result
    assert data["evaluator_error_code"] == "LLM_EVALUATOR_UNAVAILABLE"
    assert data["scorecard"]["skor_kualitas"] == 0.0  # placeholder, never rendered as success


@pytest.mark.asyncio
async def test_generation_failure_keeps_requested_evaluator_provenance(client: AsyncClient):
    headers = await _register_and_login(client, "t10_partial@example.com")
    create = await client.post("/api/v1/audits", json={
        "konten": "As a user, I want X so that Y.", "evaluator": "traditional_ml"}, headers=headers)
    id_audit = create.json()["data"]["id_audit"]
    gen_error = type("E", (RuntimeError,), {})("GENERATION_FAILED: simulated")
    with patch("app.services.audit_service.NLPStage2Service.generate_response", side_effect=gen_error):
        await AuditService.run_pipeline(id_audit)
    data = (await client.get(f"/api/v1/audits/{id_audit}", headers=headers)).json()["data"]
    assert data["status_audit"] == "PARTIAL"
    assert data["requested_evaluator"] == "traditional_ml"
    assert data["actual_evaluator"] == "traditional_ml"  # ML result preserved, never RB-substituted
    assert data["generation"]["status"] == "FAILED"
