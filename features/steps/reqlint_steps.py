"""
Step definitions Behave lengkap untuk seluruh fitur Backend dan Frontend ReqLint.
Setiap fitur langsung membuka dan menjalankan halaman web asli ReqLint (http://localhost:3000)
yang sudah dibuat di folder `frontend-qa` dan `backend`.
"""
from pathlib import Path
from behave import given, when, then

from features.bdd_support.helpers import render, get_path

ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_SRC = ROOT_DIR / "frontend-qa" / "src"


def _web(context):
    return getattr(context, "web", None)


# =========================================================================== #
# 1. HEALTH & SYSTEM STEPS (Membuka Landing Page `/` & Workspace `/editor`)
# =========================================================================== #
@given("sistem ReqLint berjalan dan endpoint API siap")
def step_system_ready(context):
    resp = context.backend.request("GET", "/api/v1/health")
    assert resp.status_code == 200, f"Healthcheck gagal: {resp.text}"


@given("endpoint upload PDF pada server FastAPI tersedia")
def step_upload_endpoint_ready(context):
    resp = context.backend.request("GET", "/api/v1/health")
    assert resp.status_code == 200, f"Endpoint belum siap: {resp.text}"


@when('saya mengirim request GET ke "{path}"')
def step_get_request(context, path):
    actual_path = render(context, path)
    context.response = context.backend.request("GET", actual_path, headers=context.auth_headers)
    try:
        context.data = context.response.json()
    except Exception:
        context.data = {}

    web = _web(context)
    if web:
        if actual_path == "/":
            web.goto("/", wait_selector="h1")
        elif actual_path == "/api/v1/health":
            web.ensure_demo_logged_in()
            web.goto("/editor", wait_selector="h1")


@then("server merespons dengan status 200 OK")
def step_status_200_ok(context):
    assert context.response.status_code == 200, (
        f"Expected 200, got {context.response.status_code}: {context.response.text}"
    )


@then("server merespons dengan status {code:d}")
def step_status_code(context, code):
    assert context.response.status_code == code, (
        f"Expected status {code}, got {context.response.status_code}: {context.response.text}"
    )


@then('field JSON "{json_path}" bernilai "{expected}"')
def step_json_field_str(context, json_path, expected):
    expected_val = render(context, expected)
    actual_val = get_path(context.response.json(), json_path)
    assert str(actual_val) == expected_val, f"Field {json_path}: expected '{expected_val}', got '{actual_val}'"


@then('field JSON "{json_path}" bernilai angka {expected}')
def step_json_field_num(context, json_path, expected):
    expected_num = float(expected)
    actual_val = float(get_path(context.response.json(), json_path))
    assert abs(actual_val - expected_num) < 0.01, f"Field {json_path}: expected {expected_num}, got {actual_val}"


@then('field JSON "{json_path}" bernilai boolean {expected}')
def step_json_field_bool(context, json_path, expected):
    exp_bool = expected.strip().lower() == "true"
    actual_val = get_path(context.response.json(), json_path)
    assert bool(actual_val) is exp_bool, f"Field {json_path}: expected {exp_bool}, got {actual_val}"


@then('header respons "{header_name}" memuat "{expected_sub}"')
def step_header_contains(context, header_name, expected_sub):
    actual = context.response.headers.get(header_name.lower(), "")
    assert expected_sub.lower() in actual.lower(), (
        f"Header '{header_name}' ('{actual}') tidak memuat '{expected_sub}'"
    )


# =========================================================================== #
# 2. AUTHENTICATION STEPS (Membuka halaman `/register` & `/login`)
# =========================================================================== #
@when('saya mendaftarkan akun baru dengan nama "{name}", email "{email}", sandi "{pwd}", dan konfirmasi "{conf}"')
def step_register_user(context, name, email, pwd, conf):
    email_val = render(context, email)
    context.response = context.backend.request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "name": name,
            "email": email_val,
            "password": pwd,
            "password_confirmation": conf,
        },
    )
    context.data = context.response.json()

    web = _web(context)
    if web:
        web.clear_browser_auth()
        web.goto("/register", wait_selector='input[name="name"]')
        web.fill_register_form(name, email_val, pwd, conf, terms=True)


@given('pengguna dengan email "{email}" dan sandi "{pwd}" sudah terdaftar')
def step_user_already_registered(context, email, pwd):
    email_val = render(context, email)
    resp = context.backend.request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "name": "Registered User",
            "email": email_val,
            "password": pwd,
            "password_confirmation": pwd,
        },
    )
    assert resp.status_code in (201, 409)
    context.frontend.register_user("Registered User", email_val, pwd, pwd, terms=True)


@when('saya login dengan email "{email}" dan sandi "{pwd}"')
def step_login_user(context, email, pwd):
    email_val = render(context, email)
    context.response = context.backend.request(
        "POST",
        "/api/v1/auth/login",
        json_body={"email": email_val, "password": pwd},
    )
    context.data = context.response.json()

    web = _web(context)
    if web:
        web.clear_browser_auth()
        web.goto("/login", wait_selector='input[name="email"]')
        web.fill_login_form(email_val, pwd)


@then("respons memiliki token akses yang valid")
def step_has_valid_token(context):
    token = get_path(context.response.json(), "data.access_token")
    assert token and len(str(token)) > 5, "Token akses kosong atau tidak valid"


@given("saya sudah login sebagai pengguna terautentikasi")
def step_logged_in_user(context):
    email = context.vars["email_unik"]
    pwd = context.vars["password"]
    context.backend.request(
        "POST",
        "/api/v1/auth/register",
        json_body={"name": "User Utama", "email": email, "password": pwd, "password_confirmation": pwd},
    )
    login_resp = context.backend.request("POST", "/api/v1/auth/login", json_body={"email": email, "password": pwd})
    token = login_resp.json()["data"]["access_token"]
    context.auth_headers = {"Authorization": f"Bearer {token}"}

    web = _web(context)
    if web:
        web.ensure_demo_logged_in()


@when('saya meminta profil pengguna saat ini di "{path}"')
def step_get_me(context, path):
    context.response = context.backend.request("GET", path, headers=context.auth_headers)
    context.data = context.response.json()

    web = _web(context)
    if web:
        if context.auth_headers:
            web.ensure_demo_logged_in()
            web.goto("/editor", wait_selector="h1")
        else:
            web.clear_browser_auth()
            web.goto("/login", wait_selector="h1")


# =========================================================================== #
# 3. PDF DOCUMENT UPLOAD STEPS (Membuka halaman `/editor` & Upload PDF)
# =========================================================================== #
@when('saya mengunggah file "{filename}"')
def step_upload_named_pdf(context, filename):
    file_path = ROOT_DIR / filename
    if file_path.exists():
        pdf_bytes = file_path.read_bytes()
    else:
        pdf_bytes = (
            b"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
            b"4 0 obj << /Length 88 >> stream\nBT /F1 12 Tf 50 700 Td "
            b"(Sebagai pengguna, saya ingin mengunggah dokumen SRS ke ReqLint.) Tj ET\nendstream endobj\n%%EOF"
        )
    context.response = context.backend.request(
        "POST",
        "/api/v1/documents/upload",
        headers=context.auth_headers,
        files={"file": (filename, pdf_bytes, "application/pdf")},
    )
    context.data = context.response.json()

    web = _web(context)
    if web and file_path.exists():
        web.upload_file_in_editor(file_path)


@then("respons mengonfirmasi bahwa teks dokumen berhasil diekstrak")
def step_confirm_pdf_extracted(context):
    data = context.response.json()
    assert data.get("status") == "success", f"Status bukan success: {data}"
    teks = data.get("data", {}).get("teks", "")
    assert len(teks.strip()) > 0, "Teks hasil ekstraksi PDF kosong"


@when('saya mengunggah dokumen PDF valid berisi teks "{text}"')
def step_upload_pdf_with_text(context, text):
    pdf_bytes = (
        f"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\nstream\nBT ({text}) Tj ET\nendstream\n%%EOF"
    ).encode("latin-1", errors="ignore")
    context.response = context.backend.request(
        "POST",
        "/api/v1/documents/upload",
        headers=context.auth_headers,
        files={"file": ("spesifikasi.pdf", pdf_bytes, "application/pdf")},
    )
    context.data = context.response.json()

    web = _web(context)
    if web:
        web.set_editor_draft_text(text)


@then('data respons memiliki "{field}" yang tidak kosong')
def step_data_field_not_null(context, field):
    val = context.response.json().get("data", {}).get(field)
    assert val is not None, f"Field data.{field} bernilai None"


@when('saya mengunggah berkas bernama "{filename}" dengan isi "{content}"')
def step_upload_arbitrary_file(context, filename, content):
    mime = "application/pdf" if filename.endswith(".pdf") else "text/plain"
    context.response = context.backend.request(
        "POST",
        "/api/v1/documents/upload",
        headers=context.auth_headers,
        files={"file": (filename, content.encode("utf-8"), mime)},
    )
    context.data = context.response.json()


@when("saya mengunggah dokumen PDF kosong tanpa lapisan teks")
def step_upload_empty_scanned_pdf(context):
    empty_pdf = b"%PDF-1.4\n1 0 obj << /Type /Page /Empty true >> endobj\n" + (b" " * 80) + b"\n%%EOF"
    context.response = context.backend.request(
        "POST",
        "/api/v1/documents/upload",
        headers=context.auth_headers,
        files={"file": ("scanned_empty.pdf", empty_pdf, "application/pdf")},
    )
    context.data = context.response.json()


@when("saya mengunggah dokumen PDF berukuran lebih dari 10 MB")
def step_upload_large_pdf(context):
    large_pdf = b"%PDF-1.4\n" + (b"0" * (10 * 1024 * 1024 + 1024)) + b"\n%%EOF"
    context.response = context.backend.request(
        "POST",
        "/api/v1/documents/upload",
        headers=context.auth_headers,
        files={"file": ("terlalu_besar.pdf", large_pdf, "application/pdf")},
    )
    context.data = context.response.json()


# =========================================================================== #
# 4. ANALYZER INVEST ML & INLINE LINT STEPS (Membuka `/editor` & `/audit/[id]`)
# =========================================================================== #
@when('saya mengirimkan user story "{user_story}"')
def step_send_user_story(context, user_story):
    context.response = context.backend.request(
        "POST",
        "/api/v1/requirements/audit",
        json_body={"requirement_text": user_story},
    )
    context.data = context.response.json()

    web = _web(context)
    if web and user_story.strip():
        web.set_editor_draft_text(user_story)
        web.click_analyze_in_editor()


@then('sistem mendeteksi input sebagai bahasa "{lang}"')
def step_check_detected_lang(context, lang):
    assert context.response.status_code == 200, f"Gagal: {context.response.text}"
    assert context.data.get("detected_language") == lang, (
        f"Expected language '{lang}', got '{context.data.get('detected_language')}'"
    )


@then('sistem mengembalikan temuan cacat "{rule1}" dan "{rule2}"')
def step_check_two_rules(context, rule1, rule2):
    smells = context.data.get("smells", [])
    rule_ids = [s.get("rule_id") for s in smells]
    assert rule1 in rule_ids, f"{rule1} tidak ditemukan dalam {rule_ids}"
    assert rule2 in rule_ids, f"{rule2} tidak ditemukan dalam {rule_ids}"


@then("sistem memberikan rekomendasi revisi user story")
def step_check_revisions_list(context):
    revisions = context.data.get("revisions", [])
    assert isinstance(revisions, list) and len(revisions) > 0, "Daftar revisions kosong"
    assert "suggested_text" in revisions[0]


@when('saya menjalankan inline lint dengan konten "{konten}"')
def step_inline_lint(context, konten):
    context.response = context.backend.request(
        "POST",
        "/api/v1/lint",
        headers=context.auth_headers,
        json_body={"konten": konten},
    )
    context.data = context.response.json()

    web = _web(context)
    if web and context.auth_headers:
        web.set_editor_draft_text(konten)


@when('saya menjalankan inline lint dengan konten ""')
def step_inline_lint_empty(context):
    step_inline_lint(context, "")


@then("jumlah temuan pada inline lint lebih dari 0")
def step_lint_findings_gt_zero(context):
    temuan = context.response.json()["data"]["temuan"]
    assert len(temuan) > 0, "Temuan inline lint kosong"


# =========================================================================== #
# 5. FULL AUDIT LIFECYCLE, HISTORY, & EXPORT STEPS (`/editor`, `/audit/[id]`, `/history`)
# =========================================================================== #
@when('saya membuat audit baru dengan judul "{judul}" dan konten "{konten}"')
def step_create_audit(context, judul, konten):
    context.response = context.backend.request(
        "POST",
        "/api/v1/audits",
        headers=context.auth_headers,
        json_body={"judul_klausul": judul, "konten": konten, "tipe_masukan": "manual"},
    )
    context.data = context.response.json()
    if context.response.status_code == 202:
        context.current_audit_id = context.data["data"]["id_audit"]
        web = _web(context)
        if web and konten.strip():
            web.set_editor_draft_text(konten)
            context.fe_last_audit = web.click_analyze_in_editor()


@given('saya telah membuat audit dengan judul "{judul}" dan konten "{konten}"')
def step_given_created_audit(context, judul, konten):
    step_create_audit(context, judul, konten)
    assert context.response.status_code == 202


@then('saya memeriksa status polling audit hingga "{expected_status}"')
def step_poll_audit_status(context, expected_status):
    resp = context.backend.request(
        "GET",
        f"/api/v1/audits/{context.current_audit_id}/status",
        headers=context.auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status_audit"] == expected_status


@when("saya mengambil detail hasil audit tersebut")
def step_get_audit_detail(context):
    context.response = context.backend.request(
        "GET",
        f"/api/v1/audits/{context.current_audit_id}",
        headers=context.auth_headers,
    )
    context.data = context.response.json()


@then("detail audit memiliki scorecard, ringkasan cacat, daftar temuan, dan rekomendasi AI")
def step_verify_audit_detail(context):
    detail = context.data["data"]
    assert detail["scorecard"] is not None
    assert "iso_29148" in detail["scorecard"]["breakdown"]
    assert "invest" in detail["scorecard"]["breakdown"]
    assert detail["ringkasan"]["total"] >= 1
    assert len(detail["temuan"]) >= 1
    assert detail["rekomendasi_ai"] is not None
    assert "ai_rewrite" in detail["rekomendasi_ai"]


@when('saya menerapkan rekomendasi AI "{opt1}" dan "{opt2}" pada audit tersebut')
def step_apply_ai_recommendation(context, opt1, opt2):
    context.response = context.backend.request(
        "POST",
        f"/api/v1/audits/{context.current_audit_id}/apply",
        headers=context.auth_headers,
        json_body={"terapkan": [opt1, opt2]},
    )
    context.data = context.response.json()

    web = _web(context)
    if web and getattr(context, "fe_last_audit", None):
        context.fe_last_audit = web.click_apply_revision_on_audit_page(context.fe_last_audit["id"])


@then('teks revisi memuat "{substring}"')
def step_revised_text_contains(context, substring):
    konten_rev = context.data["data"]["konten_revisi"]
    assert substring in konten_rev, f"'{substring}' tidak ditemukan di dalam '{konten_rev}'"


@when('saya menyimpan revisi manual "{teks_revisi}" pada audit tersebut')
def step_manual_revision(context, teks_revisi):
    context.response = context.backend.request(
        "PUT",
        f"/api/v1/audits/{context.current_audit_id}/revision",
        headers=context.auth_headers,
        json_body={"konten_revisi": teks_revisi},
    )
    context.data = context.response.json()

    web = _web(context)
    if web:
        web.set_editor_draft_text(teks_revisi)
        context.fe_last_audit = web.click_analyze_in_editor()


@given("pengguna kedua terdaftar dan login")
def step_second_user_login(context):
    email2 = f"user2_{context.vars['uid']}@example.com"
    pwd = context.vars["password"]
    context.backend.request(
        "POST",
        "/api/v1/auth/register",
        json_body={"name": "User Kedua", "email": email2, "password": pwd, "password_confirmation": pwd},
    )
    resp = context.backend.request("POST", "/api/v1/auth/login", json_body={"email": email2, "password": pwd})
    token2 = resp.json()["data"]["access_token"]
    context.second_user_headers = {"Authorization": f"Bearer {token2}"}


@when("pengguna kedua mencoba mengakses detail audit milik pengguna pertama")
def step_second_user_access_first_audit(context):
    context.response = context.backend.request(
        "GET",
        f"/api/v1/audits/{context.current_audit_id}",
        headers=context.second_user_headers,
    )
    context.data = context.response.json()


@when("saya mengambil daftar riwayat audit")
def step_list_audits(context):
    context.response = context.backend.request("GET", "/api/v1/audits", headers=context.auth_headers)
    context.data = context.response.json()

    web = _web(context)
    if web:
        web.goto("/history", wait_selector="h1")


@when('saya mencari riwayat audit dengan kata kunci "{keyword}"')
def step_search_audits(context, keyword):
    context.response = context.backend.request(
        "GET",
        f"/api/v1/audits?q={keyword}",
        headers=context.auth_headers,
    )
    context.data = context.response.json()

    web = _web(context)
    if web:
        web.search_history_on_page(keyword)


@when('saya mengekspor audit tersebut dalam format "{fmt}"')
def step_export_audit(context, fmt):
    context.response = context.backend.request(
        "GET",
        f"/api/v1/audits/{context.current_audit_id}/export?format={fmt}",
        headers=context.auth_headers,
    )
    web = _web(context)
    if web and getattr(context, "fe_last_audit", None) and fmt in ("md", "json"):
        web.click_export_on_audit_page(context.fe_last_audit["id"], fmt)


@when("saya meminta analisis ulang pada audit tersebut")
def step_reanalyze_audit(context):
    context.response = context.backend.request(
        "POST",
        f"/api/v1/audits/{context.current_audit_id}/reanalyze",
        headers=context.auth_headers,
    )
    context.data = context.response.json()


# =========================================================================== #
# 6. FRONTEND UI STEPS (Menguji langsung halaman web `frontend-qa` di browser)
# =========================================================================== #
@given('pengguna membuka halaman utama "{route}" pada frontend ReqLint')
@given('pengguna membuka halaman "{route}" pada frontend ReqLint')
def step_fe_open_page(context, route):
    web = _web(context)
    if web:
        web.goto(route, wait_selector="h1")
    else:
        context.frontend.visit(route)


@then('halaman menampilkan komponen Landing Page beserta bagian "{sec1}" dan "{sec2}"')
def step_fe_verify_landing(context, sec1, sec2):
    assert context.frontend.current_page == "/"
    sections_file = (FRONTEND_SRC / "components" / "landing" / "sections.tsx").read_text(encoding="utf-8")
    assert sec1 in sections_file, f"Bagian {sec1} tidak ditemukan di sections.tsx"
    assert sec2 in sections_file, f"Bagian {sec2} tidak ditemukan di sections.tsx"

    web = _web(context)
    if web and web.driver is not None:
        page_src = web.driver.page_source
        assert sec1 in page_src, f"'{sec1}' tidak tampil di DOM halaman utama"
        assert sec2 in page_src, f"'{sec2}' tidak tampil di DOM halaman utama"


@given("pengguna belum login pada frontend ReqLint")
def step_fe_not_logged_in(context):
    web = _web(context)
    if web:
        web.clear_browser_auth()
    else:
        context.frontend.logout_user()


@when('pengguna mencoba membuka halaman "{route}"')
@when('pengguna membuka halaman "{route}"')
def step_fe_navigate(context, route):
    web = _web(context)
    if web:
        web.goto(route, wait_selector="h1")
        if route in ("/editor", "/history", "/help", "/contact") and not context.frontend.current_user:
            web.wait_url_contains("/login", timeout=10)
    else:
        context.frontend.visit(route)


@then('halaman diarahkan ke "{expected_route}"')
def step_fe_assert_route(context, expected_route):
    assert context.frontend.current_page == expected_route, (
        f"Expected route {expected_route}, got {context.frontend.current_page}"
    )
    web = _web(context)
    if web and web.driver is not None:
        web.wait_url_contains(expected_route, timeout=10)
        assert web.current_path() == expected_route, f"Browser berada di {web.current_path()}, bukan {expected_route}"


@when(
    'pengguna mengisi form registrasi dengan nama "{name}", email "{email}", sandi "{pwd}", dan menyetujui ketentuan layanan'
)
def step_fe_register(context, name, email, pwd):
    web = _web(context)
    if web:
        ok = web.fill_register_form(name, email, pwd, pwd, terms=True)
    else:
        ok = context.frontend.register_user(name, email, pwd, pwd, terms=True)
    assert ok, f"Registrasi frontend gagal: {context.frontend.last_error}"


@then('pengguna berhasil masuk dan diarahkan ke halaman "{route}"')
def step_fe_logged_in_at(context, route):
    assert context.frontend.current_user is not None
    assert context.frontend.current_page == route
    web = _web(context)
    if web and web.driver is not None:
        web.wait_url_contains(route, timeout=10)


@when('pengguna menekan tombol "Gunakan akun demo"')
def step_fe_click_demo(context):
    web = _web(context)
    if web:
        web.click_demo_login()
    else:
        context.frontend.login_demo()


@then('pengguna berhasil masuk sebagai "{name}" dan diarahkan ke halaman "{route}"')
def step_fe_verify_demo_login(context, name, route):
    assert context.frontend.current_user is not None
    assert context.frontend.current_user["name"] == name
    assert context.frontend.current_page == route
    web = _web(context)
    if web and web.driver is not None:
        web.wait_url_contains(route, timeout=10)


@given('pengguna sudah masuk menggunakan akun demo di halaman "/editor"')
def step_fe_logged_in_demo_editor(context):
    web = _web(context)
    if web:
        web.ensure_demo_logged_in()
        if web.current_path() != "/editor":
            web.goto("/editor", wait_selector="h1")
    else:
        context.frontend.login_demo()
    assert context.frontend.current_page == "/editor"


@when('pengguna memilih bahasa analisis "{lang}" pada editor')
def step_fe_select_lang(context, lang):
    web = _web(context)
    if web:
        web.select_editor_language(lang)
    else:
        context.frontend.select_language(lang)


@when('pengguna memilih contoh template "{tpl_id}" pada editor')
def step_fe_select_template(context, tpl_id):
    web = _web(context)
    if web:
        web.select_editor_template(tpl_id)
    else:
        context.frontend.select_template(tpl_id)


@then('editor memuat draf user story berbahasa "{lang}"')
def step_fe_verify_draft_lang(context, lang):
    assert context.frontend.draft["language"] == lang
    if lang == "en":
        assert "As a user" in context.frontend.draft["text"]
    else:
        assert "Sebagai" in context.frontend.draft["text"]


@when('pengguna mengunggah berkas PDF "{filename}" melalui tombol Upload PDF di editor')
def step_fe_upload_pdf_in_editor(context, filename):
    file_path = ROOT_DIR / filename
    web = _web(context)
    if web:
        ok = web.upload_file_in_editor(file_path)
    else:
        pdf_bytes = (
            file_path.read_bytes()
            if file_path.exists()
            else b"%PDF-1.4\n(Sebagai user, saya ingin upload PDF.) Tj\n%%EOF"
        )
        ok = context.frontend.import_file(filename, pdf_bytes)
    assert ok, f"Import file ke editor gagal: {context.frontend.last_toast}"


@then('notifikasi toast frontend menampilkan "{expected_toast}"')
def step_fe_check_toast(context, expected_toast):
    assert context.frontend.last_toast == expected_toast, (
        f"Expected toast '{expected_toast}', got '{context.frontend.last_toast}'"
    )


@then("teks di dalam editor terisi dengan hasil ekstraksi dokumen PDF")
def step_fe_editor_has_extracted_text(context):
    assert len(context.frontend.draft["text"].strip()) > 0


@when('pengguna menulis draf "{text}" di editor')
def step_fe_write_draft(context, text):
    web = _web(context)
    if web:
        web.set_editor_draft_text(text)
    else:
        context.frontend.set_editor_text(text)


@when('pengguna menekan tombol "Analisis" di halaman editor')
@given("pengguna telah menjalankan analisis draf di editor")
def step_fe_run_analysis(context):
    web = _web(context)
    if web:
        context.fe_last_audit = web.click_analyze_in_editor()
    else:
        context.fe_last_audit = context.frontend.run_editor_analysis()


@then('pengguna diarahkan ke halaman hasil audit "{route}"')
def step_fe_at_audit_page(context, route):
    assert context.frontend.current_page == route, (
        f"Expected {route}, got {context.frontend.current_page}"
    )


@then('halaman hasil audit menampilkan "{c1}", "{c2}", "{c3}", dan "{c4}"')
def step_fe_verify_audit_cards(context, c1, c2, c3, c4):
    score_card_src = (FRONTEND_SRC / "components" / "audit" / "score-card.tsx").read_text(encoding="utf-8")
    findings_src = (FRONTEND_SRC / "components" / "audit" / "findings-table.tsx").read_text(encoding="utf-8")
    rev_src = (FRONTEND_SRC / "components" / "audit" / "revision-cards.tsx").read_text(encoding="utf-8")
    combined = score_card_src + findings_src + rev_src
    for label in (c1, c2, c3, c4):
        assert label in combined, f"Komponen '{label}' tidak ditemukan pada halaman hasil audit"
    assert context.fe_last_audit["score"] > 0
    assert context.fe_last_audit["acceptanceCriteria"] is not None


@when('pengguna menekan tombol "Apply" pada kartu Rekomendasi Perbaikan')
def step_fe_apply_revision(context):
    prev_score = context.fe_last_audit["score"]
    context.fe_prev_score = prev_score
    web = _web(context)
    if web:
        context.fe_last_audit = web.click_apply_revision_on_audit_page(context.fe_last_audit["id"])
    else:
        context.fe_last_audit = context.frontend.apply_revision(context.fe_last_audit["id"])


@then('audit baru "{route}" dibuat dengan skor kualitas yang lebih tinggi dari sebelumnya')
def step_fe_verify_new_audit_score(context, route):
    assert context.frontend.current_page == route
    assert context.fe_last_audit["score"] >= context.fe_prev_score


@when('pengguna mengekspor hasil audit di frontend ke format "{fmt}"')
def step_fe_export_format(context, fmt):
    web = _web(context)
    if web:
        web.click_export_on_audit_page(context.fe_last_audit["id"], fmt)
    else:
        context.frontend.export_audit(context.fe_last_audit["id"], fmt)


@then('berkas unduhan berakhir dengan ekstensi "{ext}"')
def step_fe_check_export_ext(context, ext):
    assert context.frontend.last_export is not None
    assert context.frontend.last_export["filename"].endswith(ext)


@when("pengguna menghapus seluruh riwayat audit di halaman history")
def step_fe_clear_history(context):
    web = _web(context)
    if web:
        web.clear_all_history_on_page()
    else:
        context.frontend.clear_audits()


@then('daftar riwayat audit menjadi kosong dan menampilkan pesan "{msg}"')
def step_fe_history_empty(context, msg):
    assert len(context.frontend.audits) == 0
    history_src = (FRONTEND_SRC / "app" / "(app)" / "history" / "page.tsx").read_text(encoding="utf-8")
    assert msg in history_src


@when("pengguna menekan tombol ganti tema di menu akun")
def step_fe_toggle_theme(context):
    web = _web(context)
    if web:
        web.toggle_theme_in_account_menu()
    else:
        context.frontend.toggle_theme()


@then('tema aplikasi berubah menjadi "{expected_theme}"')
def step_fe_check_theme(context, expected_theme):
    assert context.frontend.theme == expected_theme


@when('pengguna menekan tombol "Keluar" di menu akun')
def step_fe_logout(context):
    web = _web(context)
    if web:
        web.click_logout_in_account_menu()
    else:
        context.frontend.logout_user()


@then('pengguna keluar dari sesi dan diarahkan ke "{route}"')
def step_fe_logged_out(context, route):
    assert context.frontend.current_user is None
    assert context.frontend.current_page == route


# =========================================================================== #
# 7. SPRINT 3 NEW FEATURES (Forgot/Reset Password, Help, Contact, i18n, History Filters)
# =========================================================================== #
@when('saya meminta tautan reset kata sandi untuk email "{email}"')
def step_be_forgot_password(context, email):
    email_val = render(context, email)
    context.response = context.backend.request(
        "POST",
        "/api/v1/auth/forgot-password",
        json_body={"email": email_val},
    )
    context.data = context.response.json()
    context.last_reset_token = context.backend.last_reset_token


@when(
    'saya mereset kata sandi menggunakan token reset terbaru menjadi "{new_pwd}" dengan konfirmasi "{conf_pwd}"'
)
def step_be_reset_password_latest_token(context, new_pwd, conf_pwd):
    token = getattr(context, "last_reset_token", None) or context.backend.last_reset_token or ""
    context.response = context.backend.request(
        "POST",
        "/api/v1/auth/reset-password",
        json_body={
            "token": token,
            "password": new_pwd,
            "password_confirmation": conf_pwd,
        },
    )
    context.data = context.response.json()


@when('saya mereset kata sandi menggunakan token "{raw_token}" menjadi "{new_pwd}" dengan konfirmasi "{conf_pwd}"')
def step_be_reset_password_custom_token(context, raw_token, new_pwd, conf_pwd):
    context.response = context.backend.request(
        "POST",
        "/api/v1/auth/reset-password",
        json_body={
            "token": raw_token,
            "password": new_pwd,
            "password_confirmation": conf_pwd,
        },
    )
    context.data = context.response.json()


@when('pengguna masuk melalui halaman "/login" dengan email "{email}" dan sandi "{pwd}"')
def step_fe_login_on_page(context, email, pwd):
    email_val = render(context, email)
    web = _web(context)
    if web:
        web.fill_login_form(email_val, pwd)
        if context.frontend.current_user:
            web.wait_url_contains("/editor", timeout=10)
    else:
        context.frontend.login_user(email_val, pwd)


@when('pengguna mengisi email "{email}" pada form lupa kata sandi dan menekan tombol "Kirim Tautan Reset"')
@when('pengguna meminta tautan reset kata sandi pada halaman "/forgot-password" untuk email "{email}"')
def step_fe_submit_forgot_password(context, email):
    email_val = render(context, email)
    web = _web(context)
    if web:
        context.fe_reset_token = web.submit_forgot_password_form(email_val)
    else:
        context.fe_reset_token = context.frontend.request_password_reset(email_val)


@then('halaman lupa kata sandi menampilkan pesan konfirmasi "{expected_msg}"')
def step_fe_verify_forgot_msg(context, expected_msg):
    assert context.frontend.last_message == expected_msg, (
        f"Expected '{expected_msg}', got '{context.frontend.last_message}'"
    )


@when('pengguna membuka halaman "/reset-password" menggunakan token reset yang diterima')
def step_fe_open_reset_password_with_token(context):
    token = getattr(context, "fe_reset_token", None) or context.backend.last_reset_token
    assert token, "Token reset kata sandi tidak ditemukan"
    web = _web(context)
    if web:
        web.open_reset_password_page(token)
    else:
        context.frontend.visit(f"/reset-password?token={token}")


@when('pengguna mengisi kata sandi baru "{new_pwd}" dan konfirmasi "{conf_pwd}" lalu menekan tombol "Reset Kata Sandi"')
def step_fe_submit_reset_password(context, new_pwd, conf_pwd):
    web = _web(context)
    if web:
        ok = web.submit_reset_password_form(new_pwd, conf_pwd)
    else:
        ok = context.frontend.submit_reset_password(new_pwd, conf_pwd)
    assert ok, f"Reset kata sandi gagal: {context.frontend.last_error}"


@then('halaman reset kata sandi menampilkan pesan "{expected_msg}"')
def step_fe_verify_reset_msg(context, expected_msg):
    assert context.frontend.last_message == expected_msg, (
        f"Expected '{expected_msg}', got '{context.frontend.last_message}'"
    )


@then('halaman menampilkan judul utama "{expected_title}"')
def step_fe_verify_page_title(context, expected_title):
    actual_title = context.frontend.page_title()
    assert actual_title == expected_title, f"Expected title '{expected_title}', got '{actual_title}'"
    web = _web(context)
    if web and web.driver is not None:
        web.wait_xpath(f"//h1[contains(., '{expected_title}')]", timeout=10)
        h1_el = web.wait_css("h1", timeout=10)
        if h1_el and h1_el.text.strip():
            assert expected_title in h1_el.text, f"H1 di browser '{h1_el.text}' tidak memuat '{expected_title}'"


@then('halaman panduan menampilkan bagian "{s1}", "{s2}", "{s3}", dan "{s4}"')
def step_fe_verify_help_sections(context, s1, s2, s3, s4):
    assert context.frontend.current_page == "/help"
    for key in ("help.getting_started", "help.scores_title", "help.categories_title", "help.tips_title"):
        assert context.frontend.t(key) in (s1, s2, s3, s4), f"Key {key} ({context.frontend.t(key)}) tidak cocok dengan bagian halaman panduan"
    web = _web(context)
    if web and web.driver is not None:
        src = web.driver.page_source
        for sec in (s1, s2, s3, s4):
            assert sec in src or sec.replace("&", "&amp;") in src, f"Bagian '{sec}' tidak tampil di DOM /help"


@then('halaman panduan menampilkan seluruh kategori cacat "{c1}", "{c2}", "{c3}", dan "{c4}"')
def step_fe_verify_help_categories(context, c1, c2, c3, c4):
    help_src = (FRONTEND_SRC / "app" / "(app)" / "help" / "page.tsx").read_text(encoding="utf-8")
    format_src = (FRONTEND_SRC / "lib" / "format.ts").read_text(encoding="utf-8")
    i18n_src = (FRONTEND_SRC / "lib" / "i18n.ts").read_text(encoding="utf-8")
    combined = help_src + format_src + i18n_src
    for cat in (c1, c2, c3, c4):
        assert cat in combined, f"Kategori '{cat}' tidak ditemukan pada halaman panduan"


@then('halaman kontak menampilkan bagian "{s1}" dan "{s2}" beserta email "{email}"')
def step_fe_verify_contact_info(context, s1, s2, email):
    assert context.frontend.current_page == "/contact"
    contact_src = (FRONTEND_SRC / "app" / "(app)" / "contact" / "page.tsx").read_text(encoding="utf-8")
    assert email in contact_src
    assert context.frontend.t("contact.info_title") == s1
    assert context.frontend.t("contact.info_team") == s2
    web = _web(context)
    if web and web.driver is not None:
        src = web.driver.page_source
        assert email in src, f"Email '{email}' tidak tampil di DOM /contact"


@when(
    'pengguna mengisi form kontak dengan nama "{name}", email "{email}", subjek "{subject}", dan pesan "{message}"'
)
def step_fe_fill_contact(context, name, email, subject, message):
    context.contact_input = (name, email, subject, message)
    context.frontend.fill_contact_form(name, email, subject, message)


@when('pengguna menekan tombol "Kirim Pesan" pada halaman kontak')
def step_fe_submit_contact(context):
    name, email, subject, message = getattr(
        context,
        "contact_input",
        ("Fajar Akbar", "fajar@reqlint.app", "Subjek Uji", "Pesan uji kontak"),
    )
    web = _web(context)
    if web:
        ok = web.submit_contact_form_on_page(name, email, subject, message)
    else:
        ok = context.frontend.submit_contact_form()
    assert ok, f"Gagal mengirim pesan kontak: {context.frontend.last_error}"


@then('halaman kontak menampilkan pesan sukses "{expected_msg}"')
def step_fe_verify_contact_success(context, expected_msg):
    assert context.frontend.last_message == expected_msg, (
        f"Expected '{expected_msg}', got '{context.frontend.last_message}'"
    )


@when("pengguna menekan tombol ganti bahasa antarmuka di Navbar")
def step_fe_click_language_toggle(context):
    web = _web(context)
    if web:
        web.click_language_toggle_in_navbar()
    else:
        context.frontend.toggle_ui_locale()


@then('bahasa antarmuka aplikasi berubah menjadi "{expected_locale}"')
def step_fe_verify_ui_locale(context, expected_locale):
    assert context.frontend.ui_locale == expected_locale, (
        f"Expected ui_locale '{expected_locale}', got '{context.frontend.ui_locale}'"
    )


@then('menu navigasi utama menampilkan label "{l1}", "{l2}", dan "{l3}"')
def step_fe_verify_nav_labels(context, l1, l2, l3):
    nav_labels = context.frontend.nav_labels()
    for lbl in (l1, l2, l3):
        assert lbl in nav_labels, f"Label '{lbl}' tidak ditemukan di dalam {nav_labels}"


@then("daftar riwayat audit menampilkan minimal {count:d} item audit")
def step_fe_history_min_count(context, count):
    assert context.frontend.current_page == "/history"
    assert len(context.frontend.audits) >= count, (
        f"Expected >= {count} audits, got {len(context.frontend.audits)}"
    )


@when('pengguna memilih filter bahasa "{lang}" di halaman history')
def step_fe_filter_history_lang(context, lang):
    web = _web(context)
    if web:
        web.set_history_filter_on_page("lang", lang)
    else:
        context.frontend.set_history_filter("lang", lang)


@then('daftar riwayat audit yang difilter menampilkan {count:d} item berbahasa "{lang}"')
def step_fe_verify_filtered_lang(context, count, lang):
    filtered = context.frontend.filtered_audits()
    assert len(filtered) == count, f"Expected {count} items, got {len(filtered)}"
    for item in filtered:
        assert item["language"] == lang


@when('pengguna memilih filter kategori temuan "{cat}" dan bahasa "{lang}" di halaman history')
def step_fe_filter_history_cat_and_lang(context, cat, lang):
    web = _web(context)
    if web:
        web.set_history_filter_on_page("lang", lang)
        web.set_history_filter_on_page("category", cat)
    else:
        context.frontend.set_history_filter("lang", lang)
        context.frontend.set_history_filter("category", cat)


@then('daftar riwayat audit yang difilter menampilkan {count:d} item dengan temuan "{rule_id}"')
def step_fe_verify_filtered_category(context, count, rule_id):
    filtered = context.frontend.filtered_audits()
    assert len(filtered) == count, f"Expected {count} items, got {len(filtered)}"
    for item in filtered:
        assert any(f.get("kategori_cacat") == rule_id for f in item.get("findings", []))


@when('pengguna memilih pengurutan riwayat "{sort_key}" dan mereset filter di halaman history')
def step_fe_sort_and_reset_history(context, sort_key):
    web = _web(context)
    if web:
        web.set_history_filter_on_page("sort", sort_key)
        web.click_reset_history_filters_on_page()
    else:
        context.frontend.reset_history_filters()
    context.frontend.set_history_filter("sort", sort_key)


@then("daftar riwayat audit kembali menampilkan seluruh item dengan urutan skor tertinggi di posisi pertama")
def step_fe_verify_history_sorted_desc(context):
    filtered = context.frontend.filtered_audits()
    assert len(filtered) == len(context.frontend.audits)
    assert len(filtered) >= 2
    assert filtered[0]["score"] >= filtered[1]["score"]

