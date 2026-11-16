# SECURITY_REVIEW (Task 07)

**Fokus:** area yang disebut brief + regressions pada perubahan Task 06. Tidak ada framework baru.

## 1. Password reset token — ✅ aman (1 penyempurnaan kecil ditambahkan)

- Token raw 48-byte URL-safe; **hanya SHA-256 hash** disimpan (Task 06 mempertahankan mekanisme).
- **Single-use & expiry:** `reset_password` memfilter `used_at IS NULL` + `expires_at` dan menandai `used_at = now()` setelah dipakai (auth_service) → token tak dapat dipakai ulang / kedaluwarsa 1 jam. ✅
- **Anti-enumeration:** respons selalu generik. ✅
- **Tidak ada token di log/respons:** ✅ — test `test_forgot_password_without_smtp_never_leaks_token` memastikan respons tanpa kata "token"/"SMTP". Koordinator mengirim email berisi token via SMTP; **log hanya "Password-reset email delivered to <email>"** — tanpa token. Catatan kecil: log memuat alamat email penerima (acceptable untuk operasional; dapat dihilangkan bila diinginkan).

## 2. Authentication & authorization — ✅

- JWT Bearer (`get_current_user`); `GET /auth/me`; ownership audit: semua query audit join `DrafKebutuhan.id_user == user_id` → akses milik orang lain = **404 AUDIT_NOT_FOUND** (bukan 403) — sesuai SEC-4, teruji (`test_08_security_bdd`).

## 3. Audit ownership isolation — ✅ termasuk export

- `GET /audits/{id}/export` **memfilter ownership** di WHERE (`DrafKebutuhan.id_user == current_user.id_user`) → export milik orang lain = 404 (terverifikasi statis + BDD test_08 "ekspor dokumen audit milik pengguna lain ditolak 404").
- `POST /{id}/apply`, `PUT /{id}/revision`, `GET /{id}/status` — pola ownership sama.

## 4. API input validation — ✅

- Pydantic schema pada semua payload; `evaluator` divalidasi whitelist (`INVALID_EVALUATOR` 422); format export divalidasi (`UNSUPPORTED_FORMAT`); konten kosong/kepanjangan divalidasi; PDF ≤ MAX_UPLOAD_MB.

## 5. SQL injection — ✅ tidak ada permukaan

- Semua query lewat SQLAlchemy ORM/`select()` dengan parameter binding. `text()` hanya dipakai untuk DDL migrasi statis (string konstan, tanpa interpolasi input user) dan `SELECT 1` health.

## 6. Sensitive information — ✅ dengan 1 catatan kecil

- Token reset: tidak di respons/log (Task 07 regression test).
- `error_message` internal tidak diekspos di detail publik; kegagalan evaluator diekspos sebagai **coded** `evaluator_error` (pesan milik ReqLint, tanpa secret) — diperiksa: pesan berisi konfigurasi provider (nama provider/model) tanpa kredensial. ✅
- Frontend bundle: hanya `NEXT_PUBLIC_API_URL` (URL, bukan secret). ✅
- 🟡 Catatan: `auth_service` logger memuat **alamat email** penerima reset pada log "delivered" — acceptable operasional, tandai untuk review bila log dikirim ke pihak ketiga.

## 7. Environment variable exposure — ✅

- Konfigurasi SMTP/LLM dibaca di backend; tidak ada penambahan env frontend selain yang sudah ada.
- `.env.example` hanya template kosong.

## 8. Database migration safety — ✅

- Migrasi ringan idempotent (PRAGMA guard di SQLite; exception-guard di PostgreSQL); hanya ADD COLUMN nullable/default — tidak ada drop/rename/data loss. Terverifikasi live pada DB eksisting.

## 9. Perubahan keamanan pada Task 07

- Tidak ada defect keamanan baru yang perlu fix kode; dua defect integritas (advisory terbalik, export tanpa identitas) ditangani + 7 regression test export (lihat `TEST_RESULTS.md`).
- Regression security yang dipertahankan: ownership 404, anti-enumeration, token single-use, sanitasi prompt (ML-20), audit security BDD `test_08`.
