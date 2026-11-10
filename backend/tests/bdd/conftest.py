import os
import sys
import pytest
from pytest_bdd import given, when, then, parsers
from httpx import AsyncClient

@pytest.fixture
def bdd_context():
    """
    Scenario-scoped context dictionary to share data between Given, When, Then steps.
    """
    return {
        "headers": {},
        "tokens": {},
        "audits": {},
        "users": {},
        "last_response": None,
        "last_json": None,
        "payload": {},
        "id_audit": None,
        "poll_url": None,
        "pdf_bytes": None,
        "filename": None
    }

@pytest.fixture
def async_run(event_loop):
    """
    Synchronously execute an async coroutine on the session event loop.
    """
    def _runner(coro):
        return event_loop.run_until_complete(coro)
    return _runner

# ---------------- Common Step Definitions ----------------

@given(parsers.parse('pengguna terotentikasi sebagai "{email}"'))
def authenticate_user(bdd_context, client: AsyncClient, async_run, email: str):
    pwd = "SecretP@ss123"
    # Register if not yet registered
    reg_payload = {
        "name": f"User {email.split('@')[0]}",
        "email": email,
        "password": pwd,
        "password_confirmation": pwd
    }
    async_run(client.post("/api/v1/auth/register", json=reg_payload))

    # Login to get token
    login_resp = async_run(client.post("/api/v1/auth/login", json={"email": email, "password": pwd}))
    assert login_resp.status_code == 200, f"Gagal login untuk {email}: {login_resp.text}"
    token = login_resp.json()["data"]["access_token"]
    bdd_context["tokens"][email] = token
    bdd_context["headers"] = {"Authorization": f"Bearer {token}"}
    bdd_context["current_user_email"] = email

@then(parsers.parse("sistem mengembalikan kode status {status_code:d}"))
def check_status_code(bdd_context, status_code: int):
    resp = bdd_context.get("last_response")
    assert resp is not None, "Belum ada respons HTTP yang tersimpan di bdd_context"
    assert resp.status_code == status_code, f"Status code diharapkan {status_code}, didapat {resp.status_code}. Response: {resp.text}"

@then(parsers.parse('status respons bernilai "{status}"'))
def check_response_status(bdd_context, status: str):
    data = bdd_context.get("last_json")
    assert data is not None, "Respons JSON tidak ditemukan"
    assert data.get("status") == status, f"Status diharapkan '{status}', didapat '{data.get('status')}'"

@then(parsers.parse('pesan respons adalah "{message}"'))
def check_response_message(bdd_context, message: str):
    data = bdd_context.get("last_json")
    assert data is not None, "Respons JSON tidak ditemukan"
    assert data.get("message") == message, f"Pesan diharapkan '{message}', didapat '{data.get('message')}'"

@then(parsers.parse('kode error adalah "{error_code}"'))
def check_error_code(bdd_context, error_code: str):
    data = bdd_context.get("last_json")
    assert data is not None, "Respons JSON tidak ditemukan"
    assert data.get("error_code") == error_code, f"Kode error diharapkan '{error_code}', didapat '{data.get('error_code')}'"
