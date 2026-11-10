import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from httpx import AsyncClient
from app.services.audit_service import AuditService

scenarios("features/07_export_report.feature")

@given("audit yang telah selesai dengan ID siap diekspor")
def prepare_exportable_audit(bdd_context, client: AsyncClient, async_run):
    headers = bdd_context.get("headers", {})
    payload = {
        "konten": "Sebagai analis sistem, saya ingin laporan diekspor rapi agar dokumentasi lengkap.",
        "judul_klausul": "Ekspor Laporan Audit"
    }
    resp = async_run(client.post("/api/v1/audits", json=payload, headers=headers))
    assert resp.status_code == 202
    id_audit = resp.json()["data"]["id_audit"]
    bdd_context["id_audit"] = id_audit
    async_run(AuditService.run_pipeline(id_audit))

@when(parsers.parse('pengguna meminta ekspor hasil audit dengan format "{fmt}"'))
def request_export(bdd_context, client: AsyncClient, async_run, fmt):
    id_audit = bdd_context["id_audit"]
    headers = bdd_context.get("headers", {})
    resp = async_run(client.get(f"/api/v1/audits/{id_audit}/export?format={fmt}", headers=headers))
    bdd_context["last_response"] = resp
    try:
        bdd_context["last_json"] = resp.json()
    except Exception:
        bdd_context["last_json"] = None

@then(parsers.parse('tipe konten header adalah "{content_type}"'))
def verify_exact_content_type(bdd_context, content_type):
    resp = bdd_context["last_response"]
    assert resp.headers.get("content-type") == content_type

@then(parsers.parse('tipe konten header memuat "{content_type}"'))
def verify_partial_content_type(bdd_context, content_type):
    resp = bdd_context["last_response"]
    assert content_type in resp.headers.get("content-type", "")

@then(parsers.parse('header content-disposition memuat nama file "{filename}"'))
def verify_content_disposition(bdd_context, filename):
    resp = bdd_context["last_response"]
    disposition = resp.headers.get("content-disposition", "")
    assert filename in disposition

