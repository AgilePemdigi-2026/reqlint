import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from httpx import AsyncClient
from app.services.audit_service import AuditService

scenarios("features/08_security_and_data_isolation.feature")

@given(parsers.parse('pengguna "{email}" telah membuat audit klausul rahasia'))
def user_create_secret_audit(bdd_context, client: AsyncClient, async_run, email):
    pwd = "SecretP@ss123"
    # Register & Login
    async_run(client.post("/api/v1/auth/register", json={
        "name": f"User {email}", "email": email, "password": pwd, "password_confirmation": pwd
    }))
    login_resp = async_run(client.post("/api/v1/auth/login", json={"email": email, "password": pwd}))
    token = login_resp.json()["data"]["access_token"]
    bdd_context["tokens"][email] = token

    # Create audit
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "konten": "Sebagai CEO, saya ingin laporan keuangan dirahasiakan agar aman.",
        "judul_klausul": "Audit Rahasia"
    }
    resp = async_run(client.post("/api/v1/audits", json=payload, headers=headers))
    id_audit = resp.json()["data"]["id_audit"]
    bdd_context["audits"][email] = id_audit
    async_run(AuditService.run_pipeline(id_audit))

@given(parsers.parse('pengguna "{email}" telah login ke dalam sistem'))
def user_login_into_system(bdd_context, client: AsyncClient, async_run, email):
    pwd = "SecretP@ss123"
    async_run(client.post("/api/v1/auth/register", json={
        "name": f"User {email}", "email": email, "password": pwd, "password_confirmation": pwd
    }))
    login_resp = async_run(client.post("/api/v1/auth/login", json={"email": email, "password": pwd}))
    token = login_resp.json()["data"]["access_token"]
    bdd_context["tokens"][email] = token

@when(parsers.parse('pengguna "{email_b}" mencoba mengakses audit milik "{email_a}"'))
def user_access_cross_audit(bdd_context, client: AsyncClient, async_run, email_b, email_a):
    token_b = bdd_context["tokens"][email_b]
    id_audit_a = bdd_context["audits"][email_a]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp = async_run(client.get(f"/api/v1/audits/{id_audit_a}", headers=headers_b))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@when(parsers.parse('pengguna "{email_b}" mencoba mengekspor laporan audit milik "{email_a}"'))
def user_export_cross_audit(bdd_context, client: AsyncClient, async_run, email_b, email_a):
    token_b = bdd_context["tokens"][email_b]
    id_audit_a = bdd_context["audits"][email_a]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    resp = async_run(client.get(f"/api/v1/audits/{id_audit_a}/export?format=json", headers=headers_b))
    bdd_context["last_response"] = resp
    try:
        bdd_context["last_json"] = resp.json()
    except Exception:
        bdd_context["last_json"] = None

@given("pengguna tidak menyertakan header Authorization")
def no_auth(bdd_context):
    bdd_context["headers"] = {}

@when("pengguna mencoba mengakses riwayat audit")
def access_history_unauthenticated(bdd_context, client: AsyncClient, async_run):
    headers = bdd_context.get("headers", {})
    resp = async_run(client.get("/api/v1/audits", headers=headers))
    bdd_context["last_response"] = resp
    try:
        bdd_context["last_json"] = resp.json()
    except Exception:
        bdd_context["last_json"] = None
    # For FastAPI HTTPBearer 401 response: {"detail": "Not authenticated"}
    # Let's map it so check_response_message can find it if needed
    if bdd_context["last_json"] and "message" not in bdd_context["last_json"] and "detail" in bdd_context["last_json"]:
        bdd_context["last_json"]["message"] = bdd_context["last_json"]["detail"]

