"""Tests for Multi-Model White-Box & K-Means Router V2 end-to-end integration."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch

from app.services.invest_ml_service import MLEvaluatorUnavailableError
from app.services.multimodel_router_service import MultiModelRouterService

CRIT = ["independent", "negotiable", "valuable", "estimable", "small", "testable"]


def test_router_v2_genuine_inference_en_and_id():
    en_res = MultiModelRouterService.evaluate_story_router(
        "As a user, I want to export my audit report to PDF within 2 seconds so that I can share it with my team."
    )
    assert en_res["model_version"] == "2.0-multimodel-router"
    assert set(en_res["dimensions"].keys()) == set(CRIT)
    for crit in CRIT:
        dim = en_res["dimensions"][crit]
        assert dim["label"] in ("PASS", "FAIL")
        assert 0.0 <= dim["confidence"] <= 1.0
        assert "routed to" in dim["rationale"]

    meta = en_res["routing_metadata"]
    assert meta["cluster_id"] in (0, 1, 2)
    assert meta["similarity_engine"] == "tfidf-bigram"
    assert set(meta["selected_models"].keys()) == set(CRIT)
    assert all(
        m in ("LogisticRegression", "DecisionTree", "ComplementNB")
        for m in meta["selected_models"].values()
    )

    id_res = MultiModelRouterService.evaluate_story_router(
        "Sebagai mahasiswa, saya ingin mengunggah dokumen tugas akhir dan melihat status verifikasi secara cepat, sehingga saya tidak terlambat mengumpulkan."
    )
    assert id_res["model_version"] == "2.0-multimodel-router"
    assert id_res["routing_metadata"]["language"] == "id"
    assert set(id_res["dimensions"].keys()) == set(CRIT)


def test_router_v2_multistory_tfidf_features():
    bundle = MultiModelRouterService._load_bundle()
    assert bundle is not None
    X, lang = MultiModelRouterService.extract_features_for_stories(
        [
            "As a user, I want to create an account so that I can log in.",
            "As a user, I want to create an account with email verification so that I can log in safely.",
        ],
        bundle["lexicon"],
    )
    assert X.shape == (2, 18)
    assert lang == "en"
    # Second story shares core terms with first story -> non-zero TF-IDF similarity
    assert X[1, 14] > 0.0  # max_sim_backlog
    assert X[1, 17] > 0.0  # max_sim_prev_backlog


def test_router_v2_missing_artifact_fails_closed():
    with patch.object(MultiModelRouterService, "_load_bundle", return_value=None):
        with pytest.raises(MLEvaluatorUnavailableError):
            MultiModelRouterService.evaluate_story_router("As a user, I want to log in.")


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    pwd = "SecretP@ss123"
    await client.post(
        "/api/v1/auth/register",
        json={"name": "RouterV2", "email": email, "password": pwd, "password_confirmation": pwd},
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    return {"Authorization": f"Bearer {login.json()['data']['access_token']}"}


@pytest.mark.asyncio
async def test_router_v2_end_to_end_api(client: AsyncClient):
    auth_headers = await _auth_headers(client, "routerv2@example.com")
    resp = await client.post(
        "/api/v1/audits",
        json={
            "konten": "As a developer, I want to filter audit history by score so that I can find low-quality stories quickly.",
            "judul_klausul": "Router V2 E2E",
            "tipe_masukan": "manual",
            "evaluator": "multimodel_router",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 202, resp.text
    id_audit = resp.json()["data"]["id_audit"]

    detail = await client.get(f"/api/v1/audits/{id_audit}", headers=auth_headers)
    assert detail.status_code == 200, detail.text
    data = detail.json()["data"]
    assert data["status_audit"] in ("COMPLETED", "PARTIAL")
    assert data["requested_evaluator"] == "multimodel_router"
    assert data["actual_evaluator"] == "multimodel_router"
    assert data["model_version"] == "2.0-multimodel-router"
    evaluation = data["evaluation"]
    assert evaluation["evaluator"] == "multimodel_router"
    assert set(evaluation["dimensions"].keys()) == set(CRIT)
    assert evaluation["metadata"]["cluster_id"] in (0, 1, 2)
    assert set(evaluation["metadata"]["selected_models"].keys()) == set(CRIT)


@pytest.mark.asyncio
async def test_granular_ml_model_selection_end_to_end(client: AsyncClient):
    auth_headers = await _auth_headers(client, "granularml@example.com")
    story = "As a product owner, I want to export audit results to PDF within 2 seconds so that I can share them."

    cases = [
        ("traditional_ml", "v1_logistic_regression", "2.1.0-srs-hybrid", None),
        ("multimodel_router", "v2_auto_router", "2.0-multimodel-router", "auto_router"),
        ("multimodel_router", "v2_logistic_regression", "2.0-v2-logistic-regression", "direct"),
        ("multimodel_router", "v2_decision_tree", "2.0-v2-decision-tree", "direct"),
        ("multimodel_router", "v2_complement_nb", "2.0-v2-complement-nb", "direct"),
    ]
    for ev, ml_model, expected_ver, expected_mode in cases:
        resp = await client.post(
            "/api/v1/audits",
            json={"konten": story, "judul_klausul": ml_model, "tipe_masukan": "manual", "evaluator": ev, "ml_model": ml_model},
            headers=auth_headers,
        )
        assert resp.status_code == 202, (ml_model, resp.text)
        aid = resp.json()["data"]["id_audit"]

        detail = (await client.get(f"/api/v1/audits/{aid}", headers=auth_headers)).json()["data"]
        assert detail["requested_evaluator"] == ev
        assert detail["actual_evaluator"] == ev
        assert detail["model_version"] == expected_ver
        if expected_mode:
            assert detail["evaluation"]["metadata"]["selection_mode"] == expected_mode

    # History list includes evaluator and model_version provenance
    hist = (await client.get("/api/v1/audits?limit=10", headers=auth_headers)).json()["data"]
    assert any(item["model_version"] == "2.0-v2-decision-tree" for item in hist["items"])

    # Invalid ml_model fails clearly with 422 INVALID_ML_MODEL
    bad = await client.post(
        "/api/v1/audits",
        json={"konten": story, "evaluator": "multimodel_router", "ml_model": "nonexistent_xgb"},
        headers=auth_headers,
    )
    assert bad.status_code == 422
    assert bad.json()["error_code"] == "INVALID_ML_MODEL"

    mismatch = await client.post(
        "/api/v1/audits",
        json={"konten": story, "evaluator": "rule_based", "ml_model": "v2_decision_tree"},
        headers=auth_headers,
    )
    assert mismatch.status_code == 422
    assert mismatch.json()["error_code"] == "INVALID_ML_MODEL"


@pytest.mark.asyncio
async def test_historical_audits_load_without_rerunning_evaluators(client: AsyncClient):
    from datetime import datetime, timezone
    from app.core.database import AsyncSessionLocal
    from app.db.models import AuditKebutuhan, DrafKebutuhan, User
    from sqlalchemy import select

    auth_headers = await _auth_headers(client, "historycompat@example.com")
    me = await client.get("/api/v1/auth/me", headers=auth_headers)
    user_id = me.json()["data"]["id_user"]
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        records = [
            ("rule_based", None, {"evaluation": {"evaluator": "rule_based", "verdict": "PASS", "score": 90.0, "dimensions": {}}}, 90.0),
            ("traditional_ml", "2.1.0-srs-hybrid", {"evaluation": {"evaluator": "traditional_ml", "verdict": "PASS", "score": 83.3, "dimensions": {}}}, 83.3),
            ("multimodel_router", "2.0-v2-decision-tree", {"evaluation": {"evaluator": "multimodel_router", "verdict": "FAIL", "score": 66.7, "dimensions": {}}}, 66.7),
            ("llm", "openai_compatible/openai/gpt-oss-120b", {"evaluation": {"evaluator": "llm", "verdict": "PASS", "score": 100.0, "dimensions": {}}}, 100.0),
            (None, None, None, 75.0),  # Pre-model-selection legacy record
        ]
        seeded_ids = []
        for ev, ver, bd, score in records:
            draf = DrafKebutuhan(
                id_user=user_id,
                judul_klausul=f"Hist {ev or 'legacy'}",
                tipe_masukan="manual",
                konten_asli="As a user, I want to view history so that I can audit past runs.",
                status_revisi="BELUM_DIREVISI",
                created_at=now,
            )
            db.add(draf)
            await db.flush()
            audit = AuditKebutuhan(
                id_draf=draf.id_draf,
                skor_kualitas=score,
                skor_awal=score,
                tanggal_audit=now,
                status_audit="COMPLETED",
                stage2_status="DONE",
                evaluator=ev,
                model_version=ver,
                breakdown=bd,
            )
            db.add(audit)
            await db.flush()
            seeded_ids.append((audit.id_audit, ev or "rule_based", ver, score))
        await db.commit()

    # Retrieval must NEVER re-run any evaluator
    with patch("app.services.invest_ml_service.InvestMLService.evaluate_story_ml", side_effect=AssertionError("should not run")), \
         patch("app.services.multimodel_router_service.MultiModelRouterService.evaluate_story_router", side_effect=AssertionError("should not run")), \
         patch("app.services.nlp_stage2.NLPStage2Service.classify_story_with_llm", side_effect=AssertionError("should not run")):
        for aid, expected_ev, expected_ver, expected_score in seeded_ids:
            res = await client.get(f"/api/v1/audits/{aid}", headers=auth_headers)
            assert res.status_code == 200, res.text
            data = res.json()["data"]
            assert data["requested_evaluator"] == expected_ev
            assert data["actual_evaluator"] == expected_ev
            assert data["model_version"] == expected_ver
            assert data["scorecard"]["skor_kualitas"] == expected_score
