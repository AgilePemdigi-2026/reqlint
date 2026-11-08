@backend @auth
Feature: Autentikasi dan Manajemen Profil Pengguna (Backend)
  Sebagai pengguna ReqLint
  Saya ingin dapat mendaftar, masuk (login), dan mengakses profil saya secara aman
  Agar riwayat audit dan dokumen saya tersimpan secara privat di akun saya

  Scenario: Registrasi pengguna baru berhasil
    Given sistem ReqLint berjalan dan endpoint API siap
    When saya mendaftarkan akun baru dengan nama "Budi Santoso", email "${email_unik}", sandi "SecretP@ss123", dan konfirmasi "SecretP@ss123"
    Then server merespons dengan status 201
    And field JSON "status" bernilai "success"
    And field JSON "message" bernilai "Pendaftaran berhasil, silakan masuk"
    And field JSON "data.email" bernilai "${email_unik}"

  Scenario: Registrasi ditolak jika konfirmasi kata sandi tidak cocok
    Given sistem ReqLint berjalan dan endpoint API siap
    When saya mendaftarkan akun baru dengan nama "Budi Santoso", email "${email_unik}", sandi "SecretP@ss123", dan konfirmasi "SalahSandi999"
    Then server merespons dengan status 422
    And field JSON "error_code" bernilai "INVALID_PASSWORD"

  Scenario: Registrasi ditolak jika kata sandi kurang dari 8 karakter atau tanpa angka
    Given sistem ReqLint berjalan dan endpoint API siap
    When saya mendaftarkan akun baru dengan nama "Budi Santoso", email "${email_unik}", sandi "pendek", dan konfirmasi "pendek"
    Then server merespons dengan status 422
    And field JSON "error_code" bernilai "INVALID_PASSWORD"

  Scenario: Registrasi ditolak jika email sudah terdaftar
    Given pengguna dengan email "${email_unik}" dan sandi "SecretP@ss123" sudah terdaftar
    When saya mendaftarkan akun baru dengan nama "Duplikat User", email "${email_unik}", sandi "SecretP@ss123", dan konfirmasi "SecretP@ss123"
    Then server merespons dengan status 409
    And field JSON "error_code" bernilai "EMAIL_TAKEN"

  Scenario: Login berhasil dan mendapatkan token JWT Bearer
    Given pengguna dengan email "${email_unik}" dan sandi "SecretP@ss123" sudah terdaftar
    When saya login dengan email "${email_unik}" dan sandi "SecretP@ss123"
    Then server merespons dengan status 200
    And field JSON "message" bernilai "Login berhasil"
    And field JSON "data.token_type" bernilai "bearer"
    And respons memiliki token akses yang valid

  Scenario: Login gagal dengan kata sandi yang salah
    Given pengguna dengan email "${email_unik}" dan sandi "SecretP@ss123" sudah terdaftar
    When saya login dengan email "${email_unik}" dan sandi "SandiSalah123"
    Then server merespons dengan status 401
    And field JSON "error_code" bernilai "INVALID_CREDENTIALS"

  Scenario: Mengakses profil pengguna (/api/v1/auth/me) saat sudah terautentikasi
    Given saya sudah login sebagai pengguna terautentikasi
    When saya meminta profil pengguna saat ini di "/api/v1/auth/me"
    Then server merespons dengan status 200
    And field JSON "status" bernilai "success"

  Scenario: Mengakses profil pengguna ditolak jika tanpa token autentikasi
    Given sistem ReqLint berjalan dan endpoint API siap
    When saya mengirim request GET ke "/api/v1/auth/me"
    Then server merespons dengan status 401
    And field JSON "error_code" bernilai "UNAUTHORIZED"

