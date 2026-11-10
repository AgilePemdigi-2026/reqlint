import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from httpx import AsyncClient
from app.services.audit_service import AuditService

scenarios("features/06_history_and_search.feature")

@given(parsers.parse('akun pengguna baru terdaftar sebagai "{email}"'))
def register_fresh_user(bdd_context, client: AsyncClient, async_run, email):
    pwd = "SecretP@ss123"
    reg_payload = {
        "name": "Fresh User",
        "email": email,
        "password": pwd,
        "password_confirmation": pwd
    }
    async_run(client.post("/api/v1/auth/register", json=reg_payload))
    login_resp = async_run(client.post("/api/v1/auth/login", json={"email": email, "password": pwd}))
    token = login_resp.json()["data"]["access_token"]
    bdd_context["headers"] = {"Authorization": f"Bearer {token}"}

@when("pengguna membuka daftar riwayat audit")
def open_history(bdd_context, client: AsyncClient, async_run):
    headers = bdd_context.get("headers", {})
    resp = async_run(client.get("/api/v1/audits", headers=headers))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@then("status riwayat memiliki has_any_history bernilai false")
def verify_has_any_history_false(bdd_context):
    data = bdd_context["last_json"].get("data", {})
    assert data.get("has_any_history") is False

@then("status riwayat memiliki has_any_history bernilai true")
def verify_has_any_history_true(bdd_context):
    data = bdd_context["last_json"].get("data", {})
    assert data.get("has_any_history") is True

@given(parsers.parse('pengguna telah menyelesaikan audit untuk klausul "{klausul}"'))
def create_completed_audit_clause(bdd_context, client: AsyncClient, async_run, klausul):
    headers = bdd_context.get("headers", {})
    payload = {
        "konten": f"Sebagai pengguna, saya ingin {klausul} agar operasional lancar.",
        "judul_klausul": klausul
    }
    resp = async_run(client.post("/api/v1/audits", json=payload, headers=headers))
    assert resp.status_code == 202
    id_audit = resp.json()["data"]["id_audit"]
    async_run(AuditService.run_pipeline(id_audit))

@then(parsers.parse("daftar item riwayat memiliki panjang minimal {min_len:d}"))
def verify_history_length(bdd_context, min_len: int):
    items = bdd_context["last_json"].get("data", {}).get("items", [])
    assert len(items) >= min_len

@when(parsers.parse('pengguna mencari riwayat dengan kata kunci "{query}"'))
def search_history(bdd_context, client: AsyncClient, async_run, query):
    headers = bdd_context.get("headers", {})
    resp = async_run(client.get(f"/api/v1/audits?q={query}", headers=headers))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@then(parsers.parse('item hasil pencarian memuat klausul terkait "{keyword}"'))
def verify_search_match(bdd_context, keyword):
    items = bdd_context["last_json"].get("data", {}).get("items", [])
    assert len(items) > 0
    matched = any(keyword.lower() in item.get("judul_klausul", "").lower() for item in items)
    assert matched

@then("daftar item pencarian adalah kosong")
def verify_search_empty(bdd_context):
    items = bdd_context["last_json"].get("data", {}).get("items", [])
    assert len(items) == 0

