import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from httpx import AsyncClient
from app.services.audit_service import AuditService

scenarios("features/02_input_story_audit.feature")

@when("pengguna mengirimkan draf kebutuhan yang kosong")
def send_empty_draft(bdd_context, client: AsyncClient, async_run):
    headers = bdd_context.get("headers", {})
    resp = async_run(client.post("/api/v1/audits", json={"konten": "   "}, headers=headers))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@when(parsers.parse('pengguna mengirimkan draf kebutuhan "{konten}" dengan judul "{judul}"'))
def send_valid_draft(bdd_context, client: AsyncClient, async_run, konten, judul):
    headers = bdd_context.get("headers", {})
    payload = {"konten": konten, "judul_klausul": judul}
    resp = async_run(client.post("/api/v1/audits", json=payload, headers=headers))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()
    if resp.status_code == 202:
        bdd_context["id_audit"] = bdd_context["last_json"]["data"]["id_audit"]

@then("respons memuat id_audit dan url polling status")
def check_id_and_poll_url(bdd_context):
    data = bdd_context["last_json"].get("data", {})
    assert "id_audit" in data
    assert "poll_url" in data
    assert data["id_audit"] is not None

@given(parsers.parse('draf kebutuhan "{konten}" telah diterima sistem'))
def given_draft_accepted(bdd_context, client: AsyncClient, async_run, konten):
    headers = bdd_context.get("headers", {})
    payload = {"konten": konten, "judul_klausul": "Klausul Uji BDD"}
    resp = async_run(client.post("/api/v1/audits", json=payload, headers=headers))
    assert resp.status_code == 202
    bdd_context["id_audit"] = resp.json()["data"]["id_audit"]

@when("pipeline audit selesai diproses")
def run_pipeline_sync(bdd_context, async_run):
    id_audit = bdd_context["id_audit"]
    async_run(AuditService.run_pipeline(id_audit))

@when("pengguna memeriksa status audit")
def check_status_endpoint(bdd_context, client: AsyncClient, async_run):
    id_audit = bdd_context["id_audit"]
    headers = bdd_context.get("headers", {})
    resp = async_run(client.get(f"/api/v1/audits/{id_audit}/status", headers=headers))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@then(parsers.parse('status audit adalah "{status}"'))
def verify_audit_status(bdd_context, status):
    data = bdd_context["last_json"].get("data", {})
    assert data.get("status_audit") == status

@then(parsers.parse('status stage2 adalah "{status}"'))
def verify_stage2_status(bdd_context, status):
    data = bdd_context["last_json"].get("data", {})
    assert data.get("stage2_status") == status

@given(parsers.parse('teks kebutuhan Bahasa Indonesia: "{text}"'))
def given_heuristic_text(bdd_context, text):
    bdd_context["heuristic_text"] = text

@when(parsers.parse('pengguna meminta audit heuristik langsung dengan bahasa "{lang}"'))
def send_heuristic_audit(bdd_context, client: AsyncClient, async_run, lang):
    # P0/SEC-02: endpoint legacy /requirements/audit kini mewajibkan autentikasi.
    pwd = "SecretP@ss123"
    email = "heuristic_bdd@example.com"
    async_run(client.post("/api/v1/auth/register", json={
        "name": "Heuristic BDD", "email": email, "password": pwd, "password_confirmation": pwd
    }))
    login = async_run(client.post("/api/v1/auth/login", json={"email": email, "password": pwd}))
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
    payload = {
        "requirement_text": bdd_context["heuristic_text"],
        "override_language": lang
    }
    resp = async_run(client.post("/api/v1/requirements/audit", json=payload, headers=headers))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@then(parsers.parse('bahasa terdeteksi adalah "{lang}"'))
def verify_detected_language(bdd_context, lang):
    assert bdd_context["last_json"].get("detected_language") == lang

@then("skor kualitas tersedia dalam respons")
def verify_quality_score_present(bdd_context):
    assert "quality_score" in bdd_context["last_json"]

@then("daftar temuan smells tidak kosong")
def verify_smells_not_empty(bdd_context):
    smells = bdd_context["last_json"].get("smells", [])
    assert isinstance(smells, list)
    assert len(smells) > 0

@then("rekomendasi revisi INVEST tersedia dalam respons")
def verify_revisions_present(bdd_context):
    revisions = bdd_context["last_json"].get("revisions", [])
    assert isinstance(revisions, list)
    assert len(revisions) > 0

