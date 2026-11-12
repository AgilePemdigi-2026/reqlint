import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str) -> dict:
    """Helper: register + login, return Authorization headers (pattern from test_audits.py)."""
    pwd = "SecretP@ss123"
    await client.post("/api/v1/auth/register", json={
        "name": "Legacy User", "email": email, "password": pwd, "password_confirmation": pwd
    })
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_requirements_audit_requires_auth(client: AsyncClient):
    """P0/SEC-02 regression: the legacy audit endpoint must reject anonymous calls."""
    payload = {
        "requirement_text": "Sebagai pembeli, saya sebaiknya dapat membayar transaksi dengan cepat.",
        "override_language": "id",
    }
    response = await client.post("/api/v1/requirements/audit", json=payload)
    assert response.status_code == 401
    body = response.json()
    assert body["status"] == "error"
    assert body.get("error_code") == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_requirements_audit_indonesian(client: AsyncClient):
    payload = {
        "requirement_text": "Sebagai pembeli, saya sebaiknya dapat membayar transaksi dengan cepat, sehingga pesanan segera diproses.",
        "override_language": "id"
    }
    headers = await _register_and_login(client, "legacy_user@example.com")
    response = await client.post("/api/v1/requirements/audit", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] == "id"
    assert "quality_score" in data
    assert "ambiguity_index" in data
    assert "completeness_score" in data
    assert "verifiability_score" in data
    assert isinstance(data["smells"], list)
    assert len(data["smells"]) > 0
    assert isinstance(data["revisions"], list)


@pytest.mark.asyncio
async def test_requirements_audit_rejects_oversized_text(client: AsyncClient):
    """P0/SEC-02 companion: legacy endpoint input is bounded by MAX_TEXT_CHARS."""
    headers = await _register_and_login(client, "legacy_user2@example.com")
    payload = {
        "requirement_text": "Sebagai pengguna, saya ingin data aman. " * 2000,  # > 50.000 chars
        "override_language": "id",
    }
    response = await client.post("/api/v1/requirements/audit", json=payload, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_requirements_audit_guest_upload_pdf(client: AsyncClient):
    import pymupdf as fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Sebagai analis, saya ingin mengunggah dokumen PDF agar cerita pengguna dapat diekstraksi.")
    pdf_bytes = doc.write()
    doc.close()

    # Guest upload (without Authorization header)
    response = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("guest_sample.pdf", pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "success"
    assert res_json["data"]["nama_dokumen"] == "guest_sample.pdf"
    assert res_json["data"]["id_dokumen"] is None  # Guest mode
