import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from httpx import AsyncClient

scenarios("features/01_auth.feature")

@given(parsers.parse('data pendaftaran pengguna dengan nama "{name}", email "{email}", dan sandi "{password}"'))
def prepare_reg_payload(bdd_context, name, email, password):
    bdd_context["payload"] = {
        "name": name,
        "email": email,
        "password": password,
        "password_confirmation": password
    }

@given(parsers.parse('data pendaftaran pengguna dengan nama "{name}", email "{email}", sandi "{password}", dan konfirmasi salah "{password_confirmation}"'))
def prepare_reg_mismatch_payload(bdd_context, name, email, password, password_confirmation):
    bdd_context["payload"] = {
        "name": name,
        "email": email,
        "password": password,
        "password_confirmation": password_confirmation
    }

@given(parsers.parse('data pendaftaran pengguna dengan nama "{name}", email "{email}", sandi "{password}", dan konfirmasi "{password_confirmation}"'))
def prepare_reg_short_payload(bdd_context, name, email, password, password_confirmation):
    bdd_context["payload"] = {
        "name": name,
        "email": email,
        "password": password,
        "password_confirmation": password_confirmation
    }

@when("pengguna mengirimkan permintaan registrasi")
def send_register(bdd_context, client: AsyncClient, async_run):
    resp = async_run(client.post("/api/v1/auth/register", json=bdd_context["payload"]))
    bdd_context["last_response"] = resp
    try:
        bdd_context["last_json"] = resp.json()
    except Exception:
        bdd_context["last_json"] = None

@then(parsers.parse('data pengguna memuat email "{email}"'))
def check_user_email(bdd_context, email):
    data = bdd_context["last_json"].get("data", {})
    assert data.get("email") == email

@then("data pengguna tidak memuat kata sandi mentah")
def check_no_raw_password(bdd_context):
    data = bdd_context["last_json"].get("data", {})
    assert "password" not in data
    assert "password_hash" not in data

@given(parsers.parse('akun pengguna sudah terdaftar dengan email "{email}" dan sandi "{password}"'))
@given(parsers.parse('akun terdaftar dengan email "{email}" dan sandi "{password}"'))
def register_user_given(bdd_context, client: AsyncClient, async_run, email, password):
    payload = {
        "name": "Registered User",
        "email": email,
        "password": password,
        "password_confirmation": password
    }
    resp = async_run(client.post("/api/v1/auth/register", json=payload))
    bdd_context["users"][email] = {"email": email, "password": password}

@when(parsers.parse('pengguna lain mencoba mendaftar dengan email "{email}" yang sama'))
def register_duplicate(bdd_context, client: AsyncClient, async_run, email):
    payload = {
        "name": "Another User",
        "email": email,
        "password": "PasswordBaru123",
        "password_confirmation": "PasswordBaru123"
    }
    resp = async_run(client.post("/api/v1/auth/register", json=payload))
    bdd_context["last_response"] = resp
    bdd_context["last_json"] = resp.json()

@when(parsers.parse('pengguna login dengan email "{email}" dan sandi "{password}"'))
def login_user(bdd_context, client: AsyncClient, async_run, email, password):
    payload = {
        "email": email,
        "password": password
    }
    resp = async_run(client.post("/api/v1/auth/login", json=payload))
    bdd_context["last_response"] = resp
    try:
        bdd_context["last_json"] = resp.json()
    except Exception:
        bdd_context["last_json"] = None

@then(parsers.parse('respons memuat token akses bertipe "{token_type}"'))
def check_access_token(bdd_context, token_type):
    data = bdd_context["last_json"].get("data", {})
    assert "access_token" in data
    assert data.get("token_type") == token_type

