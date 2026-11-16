"""Task 09 tests: real-provider wiring, typed provider errors, secret safety,
evaluator error-code surfacing, and bilingual backend exports.

All provider interactions are mocked — this suite never touches the network.
The live-Groq verification is a separate recorded smoke run (docs/task09).
"""
import json
import httpx
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.services.nlp_stage2 import (
    NLPStage2Service,
    LLMProviderUnavailableError,
    LLMProviderRequestError,
)
from app.services.audit_service import AuditService

CRIT = ["independent", "negotiable", "valuable", "estimable", "small", "testable"]
FAKE_KEY = "gsk_FAKE_KEY_FOR_LEAK_TEST_000111"


def _status_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    response = httpx.Response(status, request=request, content=b'{"error": {"message": "boom"}}')
    return httpx.HTTPStatusError(f"HTTP {status}", request=request, response=response)


def _groq_env():
    """openai_compatible with a key present (the key value must never leak)."""
    return patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "openai_compatible"), patch(
        "app.services.nlp_stage2.settings.GROQ_API_KEY", FAKE_KEY
    )


# ── Configuration-level behavior ────────────────────────────────────────

@pytest.mark.asyncio
async def test_missing_groq_key_fails_fast_without_network_call():
    """openai_compatible without GROQ_API_KEY must fail fast with a clear code,
    not an opaque provider 401. The guard lives inside _call_provider, so the
    HTTP client is mocked to prove it is never constructed."""
    with patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "openai_compatible"), patch(
        "app.services.nlp_stage2.settings.GROQ_API_KEY", ""
    ), patch("app.services.nlp_stage2.httpx.AsyncClient") as mock_client:
        with pytest.raises(LLMProviderRequestError) as exc:
            await NLPStage2Service.classify_story_with_llm("As a user, I want X so that Y.")
    assert exc.value.code == "LLM_PROVIDER_KEY_MISSING"
    mock_client.assert_not_called()


def test_mock_provider_guard_unchanged():
    """The mock provider must still refuse to fake an LLM classification."""
    with patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "mock"):
        with pytest.raises(LLMProviderUnavailableError):
            import asyncio
            asyncio.run(NLPStage2Service.classify_story_with_llm("As a user, I want X."))


# ── Typed provider error mapping ────────────────────────────────────────

@pytest.mark.asyncio
async def test_timeout_maps_to_typed_code_and_retries():
    p1, p2 = _groq_env()
    with p1, p2, patch.object(
        NLPStage2Service, "_call_provider", side_effect=httpx.TimeoutException("timed out")
    ) as mock_call:
        with pytest.raises(LLMProviderRequestError) as exc:
            await NLPStage2Service.classify_story_with_llm("As a user, I want X so that Y.")
    assert exc.value.code == "LLM_PROVIDER_TIMEOUT"
    assert mock_call.await_count == 2  # transient: retried once


@pytest.mark.asyncio
async def test_auth_failure_fails_fast_without_retry():
    p1, p2 = _groq_env()
    with p1, p2, patch.object(
        NLPStage2Service, "_call_provider", side_effect=_status_error(401)
    ) as mock_call:
        with pytest.raises(LLMProviderRequestError) as exc:
            await NLPStage2Service.classify_story_with_llm("As a user, I want X so that Y.")
    assert exc.value.code == "LLM_PROVIDER_AUTH_FAILED"
    assert exc.value.http_status == 401
    assert mock_call.await_count == 1  # deterministic: no retry


@pytest.mark.asyncio
async def test_unknown_model_maps_to_model_not_found():
    p1, p2 = _groq_env()
    with p1, p2, patch.object(
        NLPStage2Service, "_call_provider", side_effect=_status_error(404)
    ):
        with pytest.raises(LLMProviderRequestError) as exc:
            await NLPStage2Service.classify_story_with_llm("As a user, I want X so that Y.")
    assert exc.value.code == "LLM_MODEL_NOT_FOUND"


@pytest.mark.asyncio
async def test_rate_limit_maps_to_rate_limited():
    p1, p2 = _groq_env()
    with p1, p2, patch.object(
        NLPStage2Service, "_call_provider", side_effect=_status_error(429)
    ):
        with pytest.raises(LLMProviderRequestError) as exc:
            await NLPStage2Service.classify_story_with_llm("As a user, I want X so that Y.")
    assert exc.value.code == "LLM_RATE_LIMITED"


@pytest.mark.asyncio
async def test_server_error_maps_to_provider_server_error():
    p1, p2 = _groq_env()
    with p1, p2, patch.object(
        NLPStage2Service, "_call_provider", side_effect=_status_error(503)
    ):
        with pytest.raises(LLMProviderRequestError) as exc:
            await NLPStage2Service.classify_story_with_llm("As a user, I want X so that Y.")
    assert exc.value.code == "LLM_PROVIDER_SERVER_ERROR"


@pytest.mark.asyncio
async def test_invalid_json_output_maps_to_invalid_response():
    p1, p2 = _groq_env()
    with p1, p2, patch.object(
        NLPStage2Service, "_call_provider", return_value="The model chatted prose with no JSON."
    ):
        with pytest.raises(LLMProviderRequestError) as exc:
            await NLPStage2Service.classify_story_with_llm("As a user, I want X so that Y.")
    assert exc.value.code == "LLM_INVALID_RESPONSE"


@pytest.mark.asyncio
async def test_generation_failure_uses_same_typed_errors():
    p1, p2 = _groq_env()
    evaluation = {"evaluator": "rule_based", "verdict": "FAIL", "score": 60.0, "findings": []}
    with p1, p2, patch.object(
        NLPStage2Service, "_call_provider", side_effect=_status_error(401)
    ):
        with pytest.raises(LLMProviderRequestError) as exc:
            await NLPStage2Service.generate_response("As a user, I want X.", evaluation)
    assert exc.value.code == "LLM_PROVIDER_AUTH_FAILED"


# ── Secret safety ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_provider_errors_never_leak_the_api_key():
    p1, p2 = _groq_env()
    with p1, p2, patch.object(
        NLPStage2Service, "_call_provider", side_effect=_status_error(401)
    ):
        with pytest.raises(LLMProviderRequestError) as exc:
            await NLPStage2Service.classify_story_with_llm("As a user, I want X so that Y.")
    assert FAKE_KEY not in str(exc.value)
    assert "Authorization" not in str(exc.value)


# ── Pipeline surfacing of the typed code ────────────────────────────────

async def _register_and_login(client: AsyncClient, email: str):
    pwd = "SecretP@ss123"
    await client.post("/api/v1/auth/register", json={
        "name": "T09", "email": email, "password": pwd, "password_confirmation": pwd})
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    return {"Authorization": f"Bearer {login.json()['data']['access_token']}"}


@pytest.mark.asyncio
async def test_pipeline_surfaces_typed_llm_error_code(client: AsyncClient):
    headers = await _register_and_login(client, "t09_code@example.com")
    create = await client.post(
        "/api/v1/audits", json={"konten": "As a user, I want X so that Y.", "evaluator": "llm"},
        headers=headers)
    id_audit = create.json()["data"]["id_audit"]

    with patch(
        "app.services.audit_service.NLPStage2Service.classify_story_with_llm",
        side_effect=LLMProviderRequestError("LLM_RATE_LIMITED", "provider rate limit exceeded; retry later", 429),
    ):
        await AuditService.run_pipeline(id_audit)

    detail = await client.get(f"/api/v1/audits/{id_audit}", headers=headers)
    data = detail.json()["data"]
    assert data["status_audit"] == "FAILED"
    assert data["evaluator_error_code"] == "LLM_RATE_LIMITED"
    assert data["evaluator_error"]["code"] == "LLM_RATE_LIMITED"
    # The evaluation result is NOT fabricated on failure.
    assert data["evaluation"] is None


@pytest.mark.asyncio
async def test_generation_failure_preserves_evaluation_and_marks_partial(client: AsyncClient):
    headers = await _register_and_login(client, "t09_gen@example.com")
    create = await client.post(
        "/api/v1/audits", json={"konten": "As a user, I want X so that Y.", "evaluator": "llm"},
        headers=headers)
    id_audit = create.json()["data"]["id_audit"]

    payload = {"criteria": {c: {"label": "PASS", "reason": "ok"} for c in CRIT}}
    gen_error = LLMProviderRequestError("LLM_PROVIDER_TIMEOUT", "provider did not respond within 20s")

    async def classify_ok(story_text):
        return {"dimensions": {c: {"label": "PASS", "confidence": None, "rationale": "ok"} for c in CRIT},
                "provider": "openai_compatible", "model": "openai/gpt-oss-120b"}

    with patch("app.services.audit_service.NLPStage2Service.classify_story_with_llm",
               side_effect=classify_ok), patch(
        "app.services.audit_service.NLPStage2Service.generate_response", side_effect=gen_error):
        await AuditService.run_pipeline(id_audit)

    detail = await client.get(f"/api/v1/audits/{id_audit}", headers=headers)
    data = detail.json()["data"]
    assert data["status_audit"] == "PARTIAL"
    assert data["stage2_status"] == "FAILED"
    assert data["generation"]["status"] == "FAILED"
    assert data["generation"]["error"].startswith("LLM_PROVIDER_TIMEOUT")
    # Evaluation preserved: verdict + six dimensions still present.
    assert data["evaluation"]["verdict"] == "PASS"
    assert len(data["evaluation"]["dimensions"]) == 6
    # And the score/verdict survive in the scorecard.
    assert data["scorecard"]["skor_kualitas"] == data["evaluation"]["score"]


@pytest.mark.asyncio
async def test_real_provider_shape_acceptance_criteria_are_serializable_dicts(client: AsyncClient):
    """Task 09 E2E regression: with a REAL provider the shared generator emits
    pydantic models internally; the pipeline stores acceptance_criteria into a
    JSON column, which requires plain dicts (mock path always returned dicts,
    so only a real-shaped mocked call catches this)."""
    headers = await _register_and_login(client, "t09_shape@example.com")
    create = await client.post(
        "/api/v1/audits", json={"konten": "As a user, I want X so that Y.", "evaluator": "llm"},
        headers=headers)
    id_audit = create.json()["data"]["id_audit"]

    classify_json = json.dumps({"criteria": {c: {"label": "PASS", "reason": "ok"} for c in CRIT}})
    generation_json = json.dumps({
        "explanation": "All six criteria hold.",
        "recommendation": "No changes required.",
        "ai_rewrite": "As a user, I want X within 2 seconds so that Y.",
        "acceptance_criteria": [{"given": "g", "when": "w", "then": "t"}],
        "invest_observations": {"independent": True, "negotiable": True, "valuable": True,
                                "estimable": True, "small": True, "testable": True},
    })

    async def provider_responses(system_prompt, user_prompt):
        # classify -> "criteria" payload; generation -> "ai_rewrite" payload
        if '"criteria"' in system_prompt:
            return classify_json
        return generation_json

    with patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "openai_compatible"), patch.object(
        NLPStage2Service, "_call_provider", side_effect=provider_responses
    ):
        await AuditService.run_pipeline(id_audit)

    detail = await client.get(f"/api/v1/audits/{id_audit}", headers=headers)
    data = detail.json()["data"]
    assert data["status_audit"] == "COMPLETED"
    assert data["stage2_status"] == "DONE"
    assert data["generation"]["status"] == "DONE"
    assert isinstance(data["rekomendasi_ai"]["acceptance_criteria"][0], dict)
    # Advisory notes stay separate from the evaluator verdict (Task 06 rule).
    assert data["ai_invest_notes"] == {"independent": True, "negotiable": True, "valuable": True,
                                       "estimable": True, "small": True, "testable": True}
    assert data["evaluation"]["verdict"] == "PASS"


@pytest.mark.asyncio
async def test_reanalysis_keeps_evaluator_identity_after_provider_error(client: AsyncClient):
    headers = await _register_and_login(client, "t09_rea@example.com")
    create = await client.post(
        "/api/v1/audits", json={"konten": "As a user, I want X so that Y.", "evaluator": "llm"},
        headers=headers)
    id_audit = create.json()["data"]["id_audit"]

    with patch("app.services.audit_service.NLPStage2Service.classify_story_with_llm",
               side_effect=LLMProviderRequestError("LLM_PROVIDER_AUTH_FAILED", "provider rejected the credentials", 401)):
        await AuditService.run_pipeline(id_audit)
    detail = await client.get(f"/api/v1/audits/{id_audit}", headers=headers)
    assert detail.json()["data"]["evaluator"] == "llm"

    # Reanalysis keeps the SAME evaluator (never silently switches).
    reanalyze = await client.post(f"/api/v1/audits/{id_audit}/reanalyze", headers=headers)
    assert reanalyze.status_code == 202
    payload = {"criteria": {c: {"label": "PASS", "reason": "ok"} for c in CRIT}}
    with patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "openai_compatible"), patch.object(
        NLPStage2Service, "_call_provider", return_value=json.dumps(payload)
    ):
        await AuditService.run_pipeline(id_audit)
    detail = await client.get(f"/api/v1/audits/{id_audit}", headers=headers)
    data = detail.json()["data"]
    assert data["evaluator"] == "llm"
    assert data["status_audit"] == "COMPLETED"


# ── Bilingual backend exports ────────────────────────────────────────────

def _audit_detail():
    return {
        "id_audit": 1,
        "judul_klausul": "Contoh Judul",
        "tanggal_audit": "2026-11-15T00:00:00Z",
        "status_audit": "COMPLETED",
        "status_revisi": "BELUM_DIREVISI",
        "scorecard": {"skor_awal": 90, "skor_kualitas": 85},
        "ringkasan": {"ambiguity": 1, "tidak_lengkap": 0, "weak_directive": 0, "passive_voice": 0, "total": 1},
        "temuan": [{"kategori_cacat": "AMBIGUITY", "severity": "HIGH", "potongan_teks_asli": "cepat",
                    "saran_perbaikan": "gunakan metrik"}],
        "rekomendasi_ai": None,
    }


def test_markdown_export_id_labels_default():
    from app.services.export_service import ExportService
    body = ExportService.render_markdown(_audit_detail(), "teks asli", "").decode("utf-8")
    assert "Laporan Audit Kebutuhan" in body
    assert "Ringkasan Temuan" in body


def test_markdown_export_en_labels():
    from app.services.export_service import ExportService
    body = ExportService.render_markdown(_audit_detail(), "teks asli", "", lang="en").decode("utf-8")
    assert "Requirements Audit Report" in body
    assert "Findings Summary" in body
    assert "Defect Findings" in body
    assert "Suggested Fix" in body
    assert "No revision yet" in body
    # user-authored text is never translated
    assert "teks asli" in body


def test_pdf_export_en_labels_runs():
    from app.services.export_service import ExportService
    data = ExportService.render_pdf(_audit_detail(), "teks asli", "", lang="en")
    assert data[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_export_endpoint_rejects_unknown_lang(client: AsyncClient):
    headers = await _register_and_login(client, "t09_exp@example.com")
    r = await client.get("/api/v1/audits/9999/export?format=md&lang=fr", headers=headers)
    assert r.status_code == 422
    assert r.json()["error_code"] == "UNSUPPORTED_LANG"
