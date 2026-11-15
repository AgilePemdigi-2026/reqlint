"""Task 10 Phase 0 — API trace against the REAL running stack.

Creates three audits (same story, one per evaluator) through the actual
FastAPI HTTP API, polls status, fetches details, and writes the full
request/response traces to docs/task10/api-traces/*.json.

Read-only wrt code; exercises the live backend on http://127.0.0.1:8000.
"""
import json
import sys
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000/api/v1"
OUT = Path(__file__).resolve().parents[2] / "docs" / "task10" / "api-traces"
OUT.mkdir(parents=True, exist_ok=True)

STORY = (
    "As a registered customer, I want to view my order status so that I can "
    "track the delivery of my purchase."
)
EVALUATORS = ["rule_based", "traditional_ml", "llm"]


def trace(name, step, payload):
    path = OUT / f"{name}-{step}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main() -> int:
    email = "t10-trace@example.com"
    pwd = "Trace#2026x"
    c = httpx.Client(timeout=60)

    r = c.post(f"{BASE}/auth/register", json={
        "name": "Task 10 Trace", "email": email, "password": pwd, "password_confirmation": pwd})
    if r.status_code not in (200, 201, 202, 409):
        print("register failed:", r.status_code, r.text[:200]); return 1
    r = c.post(f"{BASE}/auth/login", json={"email": email, "password": pwd})
    token = r.json()["data"]["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    summary = []
    for ev in EVALUATORS:
        name = f"audit-{ev}"
        create = c.post(f"{BASE}/audits", json={
            "konten": STORY, "judul_klausul": f"T10 {ev}", "tipe_masukan": "manual", "evaluator": ev},
            headers=h)
        trace(name, "01-create-request", {"url": "/audits", "method": "POST",
                                          "payload": {"konten": STORY, "judul_klausul": f"T10 {ev}",
                                                      "tipe_masukan": "manual", "evaluator": ev}})
        trace(name, "02-create-response", {"status": create.status_code, "body": create.json()})
        id_audit = create.json()["data"]["id_audit"]

        # Poll status until terminal (records every poll sample)
        polls = []
        t0 = time.monotonic()
        final_status = None
        while time.monotonic() - t0 < 90:
            s = c.get(f"{BASE}/audits/{id_audit}/status", headers=h)
            body = s.json()
            polls.append({"t": round(time.monotonic() - t0, 1), "status": s.status_code, "body": body})
            data = body.get("data") or {}
            final_status = data.get("status_audit")
            if final_status in ("COMPLETED", "PARTIAL", "FAILED"):
                break
            time.sleep(1.0)
        trace(name, "03-status-polls", polls)

        detail = c.get(f"{BASE}/audits/{id_audit}", headers=h)
        trace(name, "04-detail-response", {"status": detail.status_code, "body": detail.json()})

        d = detail.json().get("data") or {}
        evl = d.get("evaluation") or {}
        gen = d.get("generation") or {}
        dims = evl.get("dimensions") or {}
        summary.append({
            "id_audit": id_audit,
            "requested_evaluator": ev,
            "actual_evaluator": d.get("evaluator"),
            "status_audit": d.get("status_audit"),
            "stage2_status": d.get("stage2_status"),
            "evaluator_error_code": d.get("evaluator_error_code"),
            "score": d.get("scorecard", {}).get("skor_kualitas") if d.get("scorecard") else None,
            "model_version": d.get("model_version"),
            "findings": len(d.get("temuan") or []),
            "generation_status": gen.get("status"),
            "generation_provider": gen.get("provider"),
            "generation_error": (gen.get("error") or "")[:120],
            "dimensions": {k: v.get("label") for k, v in dims.items()},
            "scorecard_breakdown_keys": list((d.get("scorecard", {}) or {}).get("breakdown", {}).keys()),
        })

    (OUT / "00-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
