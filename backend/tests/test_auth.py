import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    payload = {
        "name": "Farhan Akbar",
        "email": "farhan@example.com",
        "password": "SecretP@ss123",
        "password_confirmation": "SecretP@ss123"
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "success"
    assert data["message"] == "Pendaftaran berhasil, silakan masuk"
    assert data["data"]["email"] == "farhan@example.com"
    assert "password" not in data["data"]

@pytest.mark.asyncio
async def test_register_password_mismatch(client: AsyncClient):
    payload = {
        "name": "Farhan Akbar",
        "email": "mismatch@example.com",
        "password": "SecretP@ss123",
        "password_confirmation": "DifferentP@ss123"
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422
    data = resp.json()
    assert data["status"] == "error"
    assert data["message"] == "Format sandi tidak valid atau konfirmasi sandi tidak cocok"
    assert data["error_code"] == "INVALID_PASSWORD"

@pytest.mark.asyncio
async def test_register_password_too_short(client: AsyncClient):
    payload = {
        "name": "Farhan Akbar",
        "email": "short@example.com",
        "password": "pass1",
        "password_confirmation": "pass1"
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422
    data = resp.json()
    assert data["status"] == "error"

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    # Catatan isolasi (ditemukan saat P0): suite BDD di backend/tests/bdd/ terkoleksi
    # SEBELUM file test_*.py dan juga mendaftarkan "duplicate@example.com" pada DB
    # in-memory bersama (session-scoped) — sehingga email ini harus unik lintas suite.
    payload = {
        "name": "Farhan Akbar",
        "email": "duplicate-auth-test@example.com",
        "password": "SecretP@ss123",
        "password_confirmation": "SecretP@ss123"
    }
    resp1 = await client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 409
    data = resp2.json()
    assert data["status"] == "error"
    assert data["message"] == "Email sudah terdaftar"
    assert data["error_code"] == "EMAIL_TAKEN"

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    reg_payload = {
        "name": "Login User",
        "email": "loginuser@example.com",
        "password": "SecretP@ss123",
        "password_confirmation": "SecretP@ss123"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {
        "email": "loginuser@example.com",
        "password": "SecretP@ss123"
    }
    resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["message"] == "Login berhasil"
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["user"]["email"] == "loginuser@example.com"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    login_payload = {
        "email": "loginuser@example.com",
        "password": "WrongPassword999"
    }
    resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert resp.status_code == 401
    data = resp.json()
    assert data["status"] == "error"
    assert data["message"] == "Kredensial tidak valid"
    assert data["error_code"] == "INVALID_CREDENTIALS"

@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient):
    login_payload = {
        "email": "notfound@example.com",
        "password": "SecretP@ss123"
    }
    resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert resp.status_code == 401
    data = resp.json()
    assert data["status"] == "error"
    assert data["message"] == "Kredensial tidak valid"
    assert data["error_code"] == "INVALID_CREDENTIALS"

@pytest.mark.asyncio
async def test_me_endpoint_authenticated(client: AsyncClient):
    email = "me_user@example.com"
    pwd = "SecretP@ss123"
    await client.post("/api/v1/auth/register", json={
        "name": "Me User", "email": email, "password": pwd, "password_confirmation": pwd
    })
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    token = login_res.json()["data"]["access_token"]

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == email

@pytest.mark.asyncio
async def test_me_endpoint_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    data = resp.json()
    assert data["status"] == "error"
    assert data["message"] == "Sesi tidak valid atau telah berakhir"
    assert data["error_code"] == "UNAUTHORIZED"
