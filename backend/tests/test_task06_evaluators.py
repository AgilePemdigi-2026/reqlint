"""Task 06 tests: three-evaluator architecture, shared generator contract,
verdict preservation, ML strict inference, and password-reset email delivery."""
import json
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

from app.services.evaluation_contract import (
    build_dimensions,
    build_evaluation_result,
    framework_score,
    overall_verdict,
    InvalidEvaluationContract,
)
from app.services.invest_ml_service import InvestMLService, MLEvaluatorUnavailableError
from app.services.nlp_stage2 import NLPStage2Service, LLMProviderUnavailableError

CRIT = ["independent", "negotiable", "valuable", "estimable", "small", "testable"]


# ── Shared evaluation contract ──────────────────────────────────────────

def test_framework_score_equal_weighting():
    dims = build_dimensions({c: "PASS" for c in CRIT})
    assert framework_score(dims) == 100.0


def test_framework_score_ie_excluded_and_renormalized():
    labels = {
        "independent": "FAIL", "negotiable": "PASS", "valuable": "PASS",
        "estimable": "INSUFFICIENT_EVIDENCE", "small": "PASS", "testable": "PASS",
    }
    dims = build_dimensions(labels)
    # 4 PASS of 5 assessed (IE excluded) with equal weights → 80.0
    assert framework_score(dims) == 80.0


def test_framework_score_none_when_nothing_assessed():
    dims = build_dimensions({})
    assert framework_score(dims) is None
    assert overall_verdict(dims) == "INSUFFICIENT_EVIDENCE"


def test_build_dimensions_rejects_invalid_label():
    with pytest.raises(InvalidEvaluationContract):
        build_dimensions({"independent": "MAYBE"})


def test_build_evaluation_result_rejects_unknown_evaluator_and_score():
    dims = build_dimensions({c: "PASS" for c in CRIT})
    with pytest.raises(InvalidEvaluationContract):
        build_evaluation_result("encoder", "PASS", 100.0, dims)
    with pytest.raises(InvalidEvaluationContract):
        build_evaluation_result("rule_based", "PASS", 150.0, dims)


def test_overall_verdict_any_fail_is_fail():
    labels = {c: "PASS" for c in CRIT}
    labels["small"] = "FAIL"
    assert overall_verdict(build_dimensions(labels)) == "FAIL"


# ── Evaluator B: Traditional ML (genuine inference, no regex fallback) ──

def test_ml_bundle_metadata_and_real_inference():
    meta = InvestMLService.get_model_metadata()
    assert meta is not None and meta["model_version"] == "2.1.0-srs-hybrid"
    assert meta["feature_count"] == 23

    result = InvestMLService.evaluate_story_ml(
        "As a user, I want to log in quickly and easily so that I can access my data."
    )
    assert result["model_version"] == "2.1.0-srs-hybrid"
    assert set(result["dimensions"].keys()) == set(CRIT)
    for crit, dim in result["dimensions"].items():
        assert dim["label"] in ("PASS", "FAIL")
        assert 0.0 <= dim["confidence"] <= 1.0


def test_ml_missing_artifact_raises_instead_of_regex_fallback():
    with patch.object(InvestMLService, "_load_model_bundle", return_value=None):
        with pytest.raises(MLEvaluatorUnavailableError):
            InvestMLService.evaluate_story_ml("As a user, I want something.")


def test_ml_corrupt_artifact_raises_instead_of_regex_fallback():
    class Boom:
        def load(self, *_a, **_k):
            raise RuntimeError("corrupt pickle")
    with patch.object(InvestMLService, "_load_model_bundle", return_value=Boom()):
        with pytest.raises(MLEvaluatorUnavailableError):
            InvestMLService.evaluate_story_ml("As a user, I want something.")


# ── Evaluator C: LLM classification ─────────────────────────────────────

def test_llm_classification_requires_real_provider():
    # Default SLM_PROVIDER=mock → the mock cannot produce genuine classification.
    with pytest.raises(LLMProviderUnavailableError):
        import asyncio
        asyncio.run(NLPStage2Service.classify_story_with_llm("As a user, I want X."))


def test_llm_classification_parses_provider_labels():
    payload = {
        "criteria": {
            "independent": {"label": "PASS", "reason": "self-contained"},
            "negotiable": {"label": "FAIL", "reason": "prescribes blue button"},
            "valuable": {"label": "PASS", "reason": "benefit stated"},
            "estimable": {"label": "INSUFFICIENT_EVIDENCE", "reason": "no size signals"},
            "small": {"label": "PASS", "reason": "single capability"},
            "testable": {"label": "FAIL", "reason": "subjective wording"},
        }
    }
    import asyncio
    with patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "openai_compatible"),          patch.object(NLPStage2Service, "_call_provider", return_value=json.dumps(payload)):
        out = asyncio.run(NLPStage2Service.classify_story_with_llm("As a user, I want X so that Y."))
    assert out["dimensions"]["negotiable"]["label"] == "FAIL"
    assert out["dimensions"]["estimable"]["label"] == "INSUFFICIENT_EVIDENCE"
    assert out["provider"] != "mock"


def test_llm_classification_coerces_off_contract_labels_to_ie():
    payload = {"criteria": {
        "independent": {"label": "MAYBE", "reason": "off-contract"},
        "negotiable": {"label": "PASS", "reason": "ok"},
        "valuable": {"label": "PASS", "reason": "ok"},
        "estimable": {"label": "PASS", "reason": "ok"},
        "small": {"label": "PASS", "reason": "ok"},
        "testable": {"label": "PASS", "reason": "ok"},
    }}
    import asyncio
    with patch("app.services.nlp_stage2.settings.SLM_PROVIDER", "openai_compatible"),          patch.object(NLPStage2Service, "_call_provider", return_value=json.dumps(payload)):
        out = asyncio.run(NLPStage2Service.classify_story_with_llm("As a user, I want X so that Y."))
    assert out["dimensions"]["independent"]["label"] == "INSUFFICIENT_EVIDENCE"
    assert out["dimensions"]["independent"]["rationale"].startswith("PROVIDER_LABEL_INVALID")


# ── Shared generator: verdict preservation ──────────────────────────────

def test_mock_generator_is_grounded_and_verdict_preserving():
    evaluation = {
        "evaluator": "rule_based", "verdict": "FAIL", "score": 65.0,
        "findings": [
            {"kategori_cacat": "AMBIGUITY", "potongan_teks_asli": "cepat",
             "highlight_start": 30, "highlight_end": 35, "saran_perbaikan": "use a metric"}
        ],
    }
    import asyncio
    out = asyncio.run(NLPStage2Service.generate_response(
        "Sebagai user, saya ingin X cepat.", evaluation,
        stage1_findings=evaluation["findings"],
    ))
    assert "Mock analysis template" in out["explanation"]  # honest, labeled as mock
    assert "AMBIGUITY" in out["explanation"]               # grounded in actual findings
    assert "cepat" in out["explanation"]
    assert out["verdict_preserved"] == "FAIL"
    assert out["score_preserved"] == 65.0
    assert out["provider"] == "mock"
    # Mock never fabricates INVEST observations (P0 constraint 5).
    assert out["ai_invest_observations"] is None


# ── Pipeline integration: evaluator dispatch over the API ──────────────

async def _create_and_run(client, headers, konten, evaluator):
    create = await client.post(
        "/api/v1/audits",
        json={"konten": konten, "judul_klausul": "t06", "evaluator": evaluator},
        headers=headers,
    )
    assert create.status_code == 202
    id_audit = create.json()["data"]["id_audit"]
    from app.services.audit_service import AuditService
    await AuditService.run_pipeline(id_audit)
    detail = await client.get(f"/api/v1/audits/{id_audit}", headers=headers)
    assert detail.status_code == 200
    return detail.json()["data"]


@pytest.mark.asyncio
async def test_rule_based_audit_verdict_preserved_against_llm_penalty(client: AsyncClient):
    """Task 06 core regression: with a rule_based audit, LLM invest flags must
    NOT change the evaluation score (no hidden -4/criterion penalty)."""
    pwd = "SecretP@ss123"
    email = "t06_rule@example.com"
    await client.post("/api/v1/auth/register", json={
        "name": "T06 Rule", "email": email, "password": pwd, "password_confirmation": pwd})
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    # A story with a rule-detected defect so the score is < 100.
    data = await _create_and_run(
        client, headers,
        "Sebagai user, saya ingin laporan yang cepat dan mudah.", "rule_based",
    )
    assert data["evaluator"] == "rule_based"
    assert data["status_audit"] == "COMPLETED"
    evaluation = data["evaluation"]
    assert evaluation["evaluator"] == "rule_based"
    # Rule-based assesses only V/T genuinely; the rest is IE — never fabricated.
    assert evaluation["dimensions"]["valuable"]["label"] in ("PASS", "FAIL")
    assert evaluation["dimensions"]["independent"]["label"] == "INSUFFICIENT_EVIDENCE"
    assert evaluation["dimensions"]["independent"]["rationale"] == "EVALUATOR_UNSUPPORTED_DIMENSION"
    # Stage-1 score preserved: identical to the value BEFORE generation ran
    # (skor_awal == skor_kualitas proves the LLM advisory did not cut it).
    assert data["scorecard"]["skor_awal"] == data["scorecard"]["skor_kualitas"]
    # LLM invest observations are advisory notes, separate from the verdict.
    assert "ai_invest_notes" in data
    assert data["generation"]["status"] == "DONE"


@pytest.mark.asyncio
async def test_traditional_ml_audit_runs_genuine_inference(client: AsyncClient):
    pwd = "SecretP@ss123"
    email = "t06_ml@example.com"
    await client.post("/api/v1/auth/register", json={
        "name": "T06 ML", "email": email, "password": pwd, "password_confirmation": pwd})
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    data = await _create_and_run(
        client, headers,
        "As a user, I want to export the report in CSV so that I can archive it.", "traditional_ml",
    )
    assert data["evaluator"] == "traditional_ml"
    assert data["model_version"] == "2.1.0-srs-hybrid"
    evaluation = data["evaluation"]
    assert evaluation["evaluator"] == "traditional_ml"
    assert evaluation["model_version"] == "2.1.0-srs-hybrid"
    # Genuine model inference: all six dimensions carry a real probability.
    for crit in CRIT:
        dim = evaluation["dimensions"][crit]
        assert dim["label"] in ("PASS", "FAIL")
        assert 0.0 <= dim["confidence"] <= 1.0
    assert data["generation"]["status"] == "DONE"


@pytest.mark.asyncio
async def test_llm_evaluator_with_mock_provider_fails_explicitly(client: AsyncClient):
    """No silent mock analysis: LLM evaluator + mock provider = explicit FAILED."""
    pwd = "SecretP@ss123"
    email = "t06_llm@example.com"
    await client.post("/api/v1/auth/register", json={
        "name": "T06 LLM", "email": email, "password": pwd, "password_confirmation": pwd})
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    create = await client.post(
        "/api/v1/audits",
        json={"konten": "As a user, I want X so that Y.", "evaluator": "llm"},
        headers=headers,
    )
    assert create.status_code == 202
    id_audit = create.json()["data"]["id_audit"]
    from app.services.audit_service import AuditService
    await AuditService.run_pipeline(id_audit)

    detail = await client.get(f"/api/v1/audits/{id_audit}", headers=headers)
    data = detail.json()["data"]
    assert data["evaluator"] == "llm"
    assert data["status_audit"] == "FAILED"
    assert data["evaluator_error_code"] == "LLM_EVALUATOR_UNAVAILABLE"
    assert data["evaluator_error"]["evaluator"] == "llm"


@pytest.mark.asyncio
async def test_invalid_evaluator_rejected_with_422(client: AsyncClient):
    pwd = "SecretP@ss123"
    email = "t06_invalid@example.com"
    await client.post("/api/v1/auth/register", json={
        "name": "T06 Inv", "email": email, "password": pwd, "password_confirmation": pwd})
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
    r = await client.post(
        "/api/v1/audits",
        json={"konten": "As a user, I want X so that Y.", "evaluator": "encoder"},
        headers=headers,
    )
    assert r.status_code == 422
    assert r.json()["error_code"] == "INVALID_EVALUATOR"


@pytest.mark.asyncio
async def test_reanalyze_reuses_persisted_evaluator(client: AsyncClient):
    pwd = "SecretP@ss123"
    email = "t06_rea@example.com"
    await client.post("/api/v1/auth/register", json={
        "name": "T06 Re", "email": email, "password": pwd, "password_confirmation": pwd})
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    data = await _create_and_run(client, headers, "As a user, I want X so that Y.", "traditional_ml")
    assert data["evaluator"] == "traditional_ml"

    reanalyze = await client.post(f"/api/v1/audits/{data['id_audit']}/reanalyze", headers=headers)
    assert reanalyze.status_code == 202
    from app.services.audit_service import AuditService
    await AuditService.run_pipeline(data["id_audit"])

    detail = await client.get(f"/api/v1/audits/{data['id_audit']}", headers=headers)
    assert detail.json()["data"]["evaluator"] == "traditional_ml"  # same evaluator, same model version
    assert detail.json()["data"]["model_version"] == "2.1.0-srs-hybrid"


# ── P0: password-reset email delivery (mocked SMTP) ─────────────────────

@pytest.mark.asyncio
async def test_forgot_password_sends_reset_email_when_smtp_configured(client: AsyncClient):
    pwd = "SecretP@ss123"
    email = "smtp_user@example.com"
    await client.post("/api/v1/auth/register", json={
        "name": "SMTP User", "email": email, "password": pwd, "password_confirmation": pwd})

    sent = {}
    def fake_smtp(host, port, timeout=None):
        class FakeSMTP:
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
            def starttls(self):
                sent["tls"] = True
            def login(self, u, p):
                sent["login"] = u
            def send_message(self, msg):
                sent["body"] = msg.get_content()
                sent["to"] = msg["To"]
        return FakeSMTP()

    with patch("app.services.auth_service.settings.SMTP_HOST", "smtp.test"), \
         patch("smtplib.SMTP", side_effect=fake_smtp):
        r = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert r.status_code == 200
    assert sent["to"] == email
    assert "reset-password?token=" in sent["body"]

    # Complete the flow using the delivered token, then log in with the new password.
    token = sent["body"].split("token=")[1].split()[0].strip()
    new_pwd = "NewSecretP@ss456"
    reset = await client.post("/api/v1/auth/reset-password", json={
        "email": email, "token": token, "password": new_pwd,
        "password_confirmation": new_pwd,
    })
    assert reset.status_code == 200
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": new_pwd})
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_forgot_password_without_smtp_never_leaks_token(client: AsyncClient):
    pwd = "SecretP@ss123"
    email = "nosmtp_user@example.com"
    await client.post("/api/v1/auth/register", json={
        "name": "No SMTP", "email": email, "password": pwd, "password_confirmation": pwd})
    r = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert r.status_code == 200
    body = r.text
    assert "token" not in body.lower()   # no token in the API response
    assert "SMTP" not in body            # internal state is not disclosed
