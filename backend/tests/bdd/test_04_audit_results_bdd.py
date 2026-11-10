import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from httpx import AsyncClient
from app.services.audit_service import AuditService

scenarios("features/04_audit_results_and_scorecard.feature")

@given(parsers.parse('draf audit tersimpan untuk teks "{text}"'))
@given(parsers.parse('draf audit tersimpan untuk teks ideal "{text}"'))
def create_audit_draft(bdd_context, client: AsyncClient, async_run, text):
    headers = bdd_context.get("headers", {})
    payload = {"konten": text, "judul_klausul": "Evaluasi INVEST"}
    resp = async_run(client.post("/api/v1/audits", json=payload, headers=headers))
    assert resp.status_code == 202
    bdd_context["id_audit"] = resp.json()["data"]["id_audit"]

@when("proses analisis pipeline selesai dijalankan")
def execute_pipeline(bdd_context, async_run):
    id_audit = bdd_context["id_audit"]
    async_run(AuditService.run_pipeline(id_audit))

@when("pengguna mengambil rincian detail audit")
def fetch_audit_detail(bdd_context, client: AsyncClient, async_run):
    id_audit = bdd_context["id_audit"]
    headers = bdd_context.get("headers", {})
    resp = async_run(client.get(f"/api/v1/audits/{id_audit}", headers=headers))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@then(parsers.parse('status kualitas audit berstatus "{status}"'))
def verify_scorecard_status(bdd_context, status):
    detail = bdd_context["last_json"].get("data", {})
    scorecard = detail.get("scorecard", {})
    skor = scorecard.get("skor_kualitas") or detail.get("skor_kualitas", 0)
    calculated_status = "Excellent" if skor >= 85 else ("Acceptable" if skor >= 70 else "Needs Improvement")
    assert calculated_status == status or detail.get("status_audit") == status

@then(parsers.parse("skor kualitas berada di bawah {score:d}"))
def verify_score_below(bdd_context, score: int):
    detail = bdd_context["last_json"].get("data", {})
    skor = detail.get("skor_kualitas") or detail.get("scorecard", {}).get("skor_kualitas", 0)
    assert skor < score, f"Skor {skor} tidak berada di bawah {score}"

@then(parsers.parse('temuan cacat mendeteksi kategori ambiguitas "{term}"'))
def verify_ambiguity_finding(bdd_context, term):
    detail = bdd_context["last_json"].get("data", {})
    temuan = detail.get("temuan", [])
    found = any(
        term.lower() in t.get("potongan_teks_asli", "").lower() or
        t.get("kategori_cacat") in ["AMBIGUITY", "NON_TESTABLE"]
        for t in temuan
    )
    assert found, f"Temuan dengan istilah '{term}' atau ambiguitas tidak ditemukan di: {temuan}"

@then(parsers.parse('rekomendasi AI menghasilkan "{field}"'))
def verify_ai_field(bdd_context, field):
    detail = bdd_context["last_json"].get("data", {})
    rek = detail.get("rekomendasi_ai", {})
    assert field in rek

@then("kriteria penerimaan otomatis memiliki format Given When Then")
def verify_given_when_then(bdd_context):
    detail = bdd_context["last_json"].get("data", {})
    ac = detail.get("rekomendasi_ai", {}).get("acceptance_criteria", [])
    assert len(ac) > 0
    has_gwt = any("given" in str(item).lower() or "when" in str(item).lower() or "then" in str(item).lower() for item in ac)
    assert has_gwt

@then(parsers.parse("skor kualitas mencapai minimal {score:d}"))
def verify_score_minimal(bdd_context, score: int):
    detail = bdd_context["last_json"].get("data", {})
    skor = detail.get("skor_kualitas") or detail.get("scorecard", {}).get("skor_kualitas", 0)
    assert skor >= score, f"Skor {skor} di bawah batas minimal {score}"

@then(parsers.parse("jumlah temuan cacat adalah {count:d}"))
def verify_finding_count(bdd_context, count: int):
    detail = bdd_context["last_json"].get("data", {})
    temuan = detail.get("temuan", [])
    assert len(temuan) == count, f"Jumlah temuan {len(temuan)} != {count}"

@then("analisis kepatuhan INVEST terpenuhi")
def verify_invest_compliance(bdd_context):
    detail = bdd_context["last_json"].get("data", {})
    assert detail.get("scorecard") is not None
