import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from httpx import AsyncClient
from app.services.audit_service import AuditService

scenarios("features/05_apply_and_manual_revision.feature")

@given(parsers.parse('audit yang telah selesai untuk draf "{draft}"'))
def prepare_completed_audit(bdd_context, client: AsyncClient, async_run, draft):
    headers = bdd_context.get("headers", {})
    payload = {"konten": draft, "judul_klausul": "Klausul Revisi"}
    resp = async_run(client.post("/api/v1/audits", json=payload, headers=headers))
    assert resp.status_code == 202
    id_audit = resp.json()["data"]["id_audit"]
    bdd_context["id_audit"] = id_audit
    # Complete pipeline
    async_run(AuditService.run_pipeline(id_audit))

@when("pengguna menekan 1-Click Apply untuk menerapkan saran perbaikan")
def apply_recommendation(bdd_context, client: AsyncClient, async_run):
    id_audit = bdd_context["id_audit"]
    headers = bdd_context.get("headers", {})
    payload = {"terapkan": ["rewrite", "acceptance_criteria"]}
    resp = async_run(client.post(f"/api/v1/audits/{id_audit}/apply", json=payload, headers=headers))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@then(parsers.parse('status revisi draf berubah menjadi "{status}"'))
def verify_revision_status(bdd_context, status):
    data = bdd_context["last_json"].get("data", {})
    assert data.get("status_revisi") == status

@then(parsers.parse('label skor diperbarui menjadi "{label}"'))
def verify_score_label(bdd_context, label):
    data = bdd_context["last_json"].get("data", {})
    assert data.get("label") == label

@when(parsers.parse('pengguna mengirimkan revisi manual "{revised_text}"'))
def send_manual_revision(bdd_context, client: AsyncClient, async_run, revised_text):
    id_audit = bdd_context["id_audit"]
    headers = bdd_context.get("headers", {})
    payload = {"konten_revisi": revised_text}
    resp = async_run(client.put(f"/api/v1/audits/{id_audit}/revision", json=payload, headers=headers))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@when("pengguna mengirimkan revisi manual berupa teks kosong")
def send_empty_manual_revision(bdd_context, client: AsyncClient, async_run):
    id_audit = bdd_context["id_audit"]
    headers = bdd_context.get("headers", {})
    payload = {"konten_revisi": "   "}
    resp = async_run(client.put(f"/api/v1/audits/{id_audit}/revision", json=payload, headers=headers))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@then("skor kualitas draf setelah revisi lebih besar dari 0")
def verify_revised_score(bdd_context):
    data = bdd_context["last_json"].get("data", {})
    assert data.get("skor_kualitas", 0) > 0

