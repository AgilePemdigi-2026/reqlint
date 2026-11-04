@auth @bdd
Feature: Autentikasi dan Manajemen Sesi Pengguna
  Sebagai System Analyst atau Pengguna ReqLint
  Saya ingin mendaftar akun dan login ke sistem
  Agar dapat mengelola dan mengisolasi draf User Story serta riwayat audit secara aman

  Scenario: Pendaftaran akun baru berhasil dengan data valid
    Given data pendaftaran pengguna dengan nama "Bima Akbar", email "bima@example.com", dan sandi "SecureP@ss123"
    When pengguna mengirimkan permintaan registrasi
    Then sistem mengembalikan kode status 201
    And status respons bernilai "success"
    And pesan respons adalah "Pendaftaran berhasil, silakan masuk"
    And data pengguna memuat email "bima@example.com"
    And data pengguna tidak memuat kata sandi mentah

  Scenario: Pendaftaran gagal jika konfirmasi kata sandi tidak cocok
    Given data pendaftaran pengguna dengan nama "Farhan Akbar", email "mismatch@example.com", sandi "SecretP@ss123", dan konfirmasi salah "WrongPass999"
    When pengguna mengirimkan permintaan registrasi
    Then sistem mengembalikan kode status 422
    And status respons bernilai "error"
    And kode error adalah "INVALID_PASSWORD"
    And pesan respons adalah "Format sandi tidak valid atau konfirmasi sandi tidak cocok"

  Scenario: Pendaftaran gagal jika kata sandi terlalu pendek
    Given data pendaftaran pengguna dengan nama "Daniel P", email "short@example.com", sandi "pass1", dan konfirmasi "pass1"
    When pengguna mengirimkan permintaan registrasi
    Then sistem mengembalikan kode status 422
    And status respons bernilai "error"

  Scenario: Pendaftaran gagal jika email sudah terdaftar sebelumnya
    Given akun pengguna sudah terdaftar dengan email "duplicate@example.com" dan sandi "SecretP@ss123"
    When pengguna lain mencoba mendaftar dengan email "duplicate@example.com" yang sama
    Then sistem mengembalikan kode status 409
    And status respons bernilai "error"
    And kode error adalah "EMAIL_TAKEN"
    And pesan respons adalah "Email sudah terdaftar"

  Scenario: Login berhasil dengan kredensial valid
    Given akun terdaftar dengan email "analyst@example.com" dan sandi "SecretP@ss123"
    When pengguna login dengan email "analyst@example.com" dan sandi "SecretP@ss123"
    Then sistem mengembalikan kode status 200
    And status respons bernilai "success"
    And pesan respons adalah "Login berhasil"
    And respons memuat token akses bertipe "bearer"

  Scenario: Login gagal jika kata sandi salah
    Given akun terdaftar dengan email "analyst@example.com" dan sandi "SecretP@ss123"
    When pengguna login dengan email "analyst@example.com" dan sandi "WrongPassword456"
    Then sistem mengembalikan kode status 401
    And status respons bernilai "error"
    And kode error adalah "INVALID_CREDENTIALS"
    And pesan respons adalah "Kredensial tidak valid"

