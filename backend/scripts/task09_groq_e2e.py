"""Task 09 Phase 4 — REAL Groq end-to-end smoke run.

Standalone script (NOT part of the pytest suite): it uses the real
backend/.env configuration (SLM_PROVIDER=openai_compatible + GROQ_API_KEY)
and performs live provider calls. The mocked regression suite pins
SLM_PROVIDER=mock and must stay offline/deterministic.

What it does (per docs/task09 requirements):
  1. Confirm the backend recognizes the Groq config WITHOUT printing the key.
  2. Confirm provider connectivity (GET /models).
  3. Run a real six-dimension LLM classification.
  4. Validate the structured response against the evaluation contract.
  5. Run the shared response generation (verdict-preserving contract).
  6. Persist an audit through the FastAPI pipeline, retrieve the detail,
     verify evaluator identity + generation status.
  7. Reanalyze and verify the evaluator identity persists.

The audit is stored in an ISOLATED temporary SQLite database — the developer's
reqlint.db is never touched. Safe output only: provider/model/latency/verdicts.
"""
import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

TEST_STORY = (
    "As a registered customer, I want to view my order status so that I can "
    "track the delivery of my purchase."
)

# Isolated DB *before* importing app modules (DATABASE_URL is read at import).
_tmpdir = tempfile.mkdtemp(prefix="reqlint-task09-e2e-")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_tmpdir}/e2e.db"


def report(step: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {step}" + (f" — {detail}" if detail else ""))


async def main() -> int:
    results: dict = {"steps": []}

    # ── 1. Configuration recognized (no key material printed) ──
    from app.core.config import settings

    key_state = "configured" if settings.GROQ_API_KEY else "missing"
    is_groq = settings.SLM_PROVIDER == "openai_compatible" and "groq.com" in settings.SLM_BASE_URL
    report(
        "backend recognizes Groq configuration",
        is_groq and key_state == "configured",
        f"provider={settings.SLM_PROVIDER} base={settings.SLM_BASE_URL} "
        f"model={settings.SLM_MODEL} timeout={settings.SLM_TIMEOUT_SECONDS}s "
        f"GROQ_API_KEY={key_state}",
    )
    results["config"] = {
        "provider": settings.SLM_PROVIDER,
        "base_url": settings.SLM_BASE_URL,
        "model": settings.SLM_MODEL,
        "timeout_seconds": settings.SLM_TIMEOUT_SECONDS,
        "groq_api_key": key_state,
    }

    # ── 2. Provider connectivity ──
    import httpx

    t0 = time.monotonic()
    models = httpx.get(
        f"{settings.SLM_BASE_URL.rstrip('/')}/v1/models",
        headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
        timeout=15,
    )
    dt = time.monotonic() - t0
    model_ids = [m["id"] for m in models.json().get("data", [])] if models.status_code == 200 else []
    report(
        "provider connectivity (GET /models)",
        models.status_code == 200,
        f"HTTP {models.status_code} in {dt:.1f}s, {len(model_ids)} models, "
        f"configured model listed: {settings.SLM_MODEL in model_ids}",
    )
    results["connectivity"] = {"http_status": models.status_code, "latency_s": round(dt, 1)}

    # ── 3+4. Real six-dimension classification, validated via the contract ──
    from app.services.nlp_stage2 import NLPStage2Service
    from app.services.evaluation_contract import build_evaluation_result, overall_verdict, framework_score

    t0 = time.monotonic()
    classification = await NLPStage2Service.classify_story_with_llm(TEST_STORY)
    classify_latency = time.monotonic() - t0
    dims = classification["dimensions"]
    labels_ok = all(dims[c]["label"] in {"PASS", "FAIL", "INSUFFICIENT_EVIDENCE"} for c in dims)
    report(
        "real 6-dimension LLM classification",
        len(dims) == 6 and labels_ok,
        "labels=" + json.dumps({c: dims[c]["label"] for c in dims}) + f" in {classify_latency:.1f}s",
    )
    results["classification"] = {
        "labels": {c: dims[c]["label"] for c in dims},
        "provider": classification["provider"],
        "model": classification["model"],
        "latency_s": round(classify_latency, 1),
    }

    evaluation = build_evaluation_result(
        evaluator="llm",
        verdict=overall_verdict(dims),
        score=framework_score(dims),
        dimensions=dims,
        model_version=f"{classification['provider']}/{classification['model']}",
        findings=[],
        breakdown=None,
        metadata={"source": "task09-e2e"},
    )
    report(
        "structured response satisfies the evaluation contract",
        evaluation["evaluator"] == "llm" and evaluation["verdict"] is not None,
        f"verdict={evaluation['verdict']} score={evaluation['score']} "
        f"model_version={evaluation['model_version']}",
    )

    # ── 5. Shared response generation (real provider) ──
    t0 = time.monotonic()
    generation = await NLPStage2Service.generate_response(TEST_STORY, evaluation, stage1_findings=[])
    gen_latency = time.monotonic() - t0
    gen_ok = (
        generation["verdict_preserved"] == evaluation["verdict"]
        and generation["score_preserved"] == evaluation["score"]
        and bool(generation.get("ai_rewrite"))
        and generation.get("acceptance_criteria") is not None
        and generation.get("provider") == settings.SLM_PROVIDER
    )
    report(
        "shared response generation (real provider)",
        gen_ok,
        f"verdict_preserved={generation['verdict_preserved']} "
        f"score_preserved={generation['score_preserved']} "
        f"criteria={len(generation.get('acceptance_criteria') or [])} in {gen_latency:.1f}s",
    )
    results["generation"] = {
        "status": "DONE" if gen_ok else "INVALID",
        "verdict_preserved": generation["verdict_preserved"],
        "score_preserved": generation["score_preserved"],
        "latency_s": round(gen_latency, 1),
    }

    # ── 6+7. Full pipeline through the API on an isolated DB ──
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy.pool import StaticPool
    from app.core.database import Base, get_db
    import app.core.database as core_db
    import app.services.audit_service as audit_svc
    from app.main import app as fastapi_app

    engine = create_async_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False}, poolclass=StaticPool)
    from sqlalchemy.ext.asyncio import AsyncSession
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    core_db.AsyncSessionLocal = SessionLocal
    audit_svc.AsyncSessionLocal = SessionLocal

    async def override_get_db():
        async with SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db

    from httpx import AsyncClient, ASGITransport

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://e2e") as client:
        email = "task09-e2e@example.com"
        pwd = "E2eSmoke#2026"
        await client.post("/api/v1/auth/register", json={
            "name": "Task 09 E2E", "email": email, "password": pwd, "password_confirmation": pwd})
        login = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
        headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

        t0 = time.monotonic()
        create = await client.post("/api/v1/audits", json={
            "konten": TEST_STORY, "judul_klausul": "Task 09 E2E story", "evaluator": "llm"},
            headers=headers)
        create_ok = create.status_code == 202
        id_audit = create.json()["data"]["id_audit"]
        await AuditService_run_pipeline(audit_svc, id_audit)
        pipeline_latency = time.monotonic() - t0

        detail = (await client.get(f"/api/v1/audits/{id_audit}", headers=headers)).json()["data"]
        pipeline_ok = (
            detail["evaluator"] == "llm"
            and detail["status_audit"] == "COMPLETED"
            and detail["generation"]["status"] == "DONE"
            and detail["generation"]["provider"] == settings.SLM_PROVIDER
            and detail["evaluation"]["evaluator"] == "llm"
        )
        report(
            "audit persisted + retrieved via API (LLM evaluator)",
            create_ok and pipeline_ok,
            f"status={detail['status_audit']} stage2={detail['stage2_status']} "
            f"evaluator={detail['evaluator']} model={detail['model_version']} "
            f"generation={detail['generation']['status']}/"
            f"{detail['generation']['provider']} in {pipeline_latency:.1f}s",
        )
        results["pipeline"] = {
            "create_http": create.status_code,
            "status_audit": detail["status_audit"],
            "stage2_status": detail["stage2_status"],
            "evaluator": detail["evaluator"],
            "model_version": detail["model_version"],
            "generation_status": detail["generation"]["status"],
            "generation_provider": detail["generation"]["provider"],
            "latency_s": round(pipeline_latency, 1),
        }

        # Frontend-facing fields the UI reads for the LLM experience.
        adv = detail.get("ai_invest_notes")
        report("frontend-facing LLM fields present", detail.get("ai_suggestion_source") == "provider",
               f"ai_suggestion_source={detail.get('ai_suggestion_source')} ai_invest_notes={'present' if adv else 'none'}")
        results["frontend_fields"] = {"ai_suggestion_source": detail.get("ai_suggestion_source")}

        # ── 7. Reanalysis keeps evaluator identity ──
        rean = await client.post(f"/api/v1/audits/{id_audit}/reanalyze", headers=headers)
        rean_ok = rean.status_code == 202
        await AuditService_run_pipeline(audit_svc, id_audit)
        detail2 = (await client.get(f"/api/v1/audits/{id_audit}", headers=headers)).json()["data"]
        report(
            "reanalysis keeps evaluator identity (llm) end-to-end",
            rean_ok and detail2["evaluator"] == "llm" and detail2["status_audit"] == "COMPLETED",
            f"status={detail2['status_audit']} evaluator={detail2['evaluator']} "
            f"model={detail2['model_version']}",
        )
        results["reanalysis"] = {"status_audit": detail2["status_audit"], "evaluator": detail2["evaluator"]}

    ok = all(r.get("ok", True) for r in results["steps"]) if "steps" in results else True
    print(json.dumps(results, indent=2))
    return 0


async def AuditService_run_pipeline(audit_svc, id_audit: int) -> None:
    await audit_svc.AuditService.run_pipeline(id_audit)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
