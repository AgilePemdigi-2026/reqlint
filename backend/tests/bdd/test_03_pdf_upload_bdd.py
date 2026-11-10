import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from httpx import AsyncClient
import pymupdf as fitz

scenarios("features/03_pdf_document_upload.feature")

@given("pengguna tidak menyertakan token autentikasi")
def no_auth_header(bdd_context):
    bdd_context["headers"] = {}

@given(parsers.parse('berkas PDF digital valid "{filename}" berisi teks "{content}"'))
def create_valid_pdf(bdd_context, filename, content):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), content)
    pdf_bytes = doc.write()
    doc.close()
    bdd_context["filename"] = filename
    bdd_context["file_bytes"] = pdf_bytes
    bdd_context["content_type"] = "application/pdf"

@given(parsers.parse('berkas tidak valid "{filename}" dengan konten teks biasa'))
def create_txt_file(bdd_context, filename):
    bdd_context["filename"] = filename
    bdd_context["file_bytes"] = b"Ini adalah file teks biasa bukan PDF."
    bdd_context["content_type"] = "text/plain"

@given(parsers.parse('berkas PDF rusak "{filename}" dengan byte acak tidak valid'))
def create_corrupt_pdf(bdd_context, filename):
    bdd_context["filename"] = filename
    bdd_context["file_bytes"] = b"%PDF-invalid-bytes-not-a-real-pdf-structure"
    bdd_context["content_type"] = "application/pdf"

@given(parsers.parse('berkas PDF hasil scan "{filename}" tanpa lapisan teks digital'))
def create_scanned_pdf(bdd_context, filename):
    doc = fitz.open()
    doc.new_page()  # empty page with no text
    pdf_bytes = doc.write()
    doc.close()
    bdd_context["filename"] = filename
    bdd_context["file_bytes"] = pdf_bytes
    bdd_context["content_type"] = "application/pdf"

@given(parsers.parse('berkas PDF "{filename}" dengan ukuran melebihi 10 megabyte'))
def create_huge_pdf(bdd_context, filename):
    huge_bytes = b"%PDF-1.4\n" + b"0" * (10 * 1024 * 1024 + 1024)
    bdd_context["filename"] = filename
    bdd_context["file_bytes"] = huge_bytes
    bdd_context["content_type"] = "application/pdf"

@when("pengguna mengunggah berkas PDF tersebut ke endpoint upload")
@when("pengguna mengunggah berkas tersebut ke endpoint upload")
def upload_document(bdd_context, client: AsyncClient, async_run):
    files = {
        "file": (
            bdd_context["filename"],
            bdd_context["file_bytes"],
            bdd_context["content_type"]
        )
    }
    headers = bdd_context.get("headers", {})
    resp = async_run(client.post("/api/v1/documents/upload", files=files, headers=headers))
    bdd_context["last_response"] = resp
    try:
        bdd_context["last_json"] = resp.json()
    except Exception:
        bdd_context["last_json"] = None

@then("data respons memuat id_dokumen")
def verify_id_dokumen(bdd_context):
    data = bdd_context["last_json"].get("data", {})
    assert "id_dokumen" in data
    assert data["id_dokumen"] is not None

@then(parsers.parse('teks hasil ekstraksi memuat "{text}"'))
def verify_extracted_text(bdd_context, text):
    data = bdd_context["last_json"].get("data", {})
    assert text in data.get("teks", "")

@then(parsers.parse('nama dokumen yang diekstrak adalah "{filename}"'))
def verify_doc_name(bdd_context, filename):
    data = bdd_context["last_json"].get("data", {})
    assert data.get("nama_dokumen") == filename

@then("id dokumen bernilai null")
def verify_guest_id_dokumen_null(bdd_context):
    data = bdd_context["last_json"].get("data", {})
    assert data.get("id_dokumen") is None

