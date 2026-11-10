@security @isolation @sec4 @bdd
Feature: Keamanan Data dan Isolasi Akses Lintas Pengguna
  Sebagai Administrator Keamanan Sistem
  Saya ingin memastikan bahwa data audit terisolasi secara ketat per pengguna
  Agar tidak terjadi kebocoran informasi klausul kebutuhan antar akun (SEC-4)

  Scenario: Akses ke audit milik pengguna lain mengembalikan 404 Not Found bukan 403
    Given pengguna "user_alpha@example.com" telah membuat audit klausul rahasia
    And pengguna "user_beta@example.com" telah login ke dalam sistem
    When pengguna "user_beta@example.com" mencoba mengakses audit milik "user_alpha@example.com"
    Then sistem mengembalikan kode status 404
    And pesan respons adalah "Data audit tidak ditemukan"

  Scenario: Ekspor dokumen audit milik pengguna lain ditolak dengan 404 Not Found
    Given pengguna "user_alpha@example.com" telah membuat audit klausul rahasia
    And pengguna "user_beta@example.com" telah login ke dalam sistem
    When pengguna "user_beta@example.com" mencoba mengekspor laporan audit milik "user_alpha@example.com"
    Then sistem mengembalikan kode status 404
    And pesan respons adalah "Data audit tidak ditemukan"

  Scenario: Akses ke endpoint terproteksi tanpa token autentikasi ditolak
    Given pengguna tidak menyertakan header Authorization
    When pengguna mencoba mengakses riwayat audit
    Then sistem mengembalikan kode status 401
    And pesan respons adalah "Sesi tidak valid atau telah berakhir"
