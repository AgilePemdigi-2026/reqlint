@history @search @bdd
Feature: Riwayat Audit dan Penelusuran Log
  Sebagai System Analyst
  Saya ingin melihat daftar seluruh riwayat audit dan melakukan pencarian
  Agar dapat memantau evolusi kualitas spesifikasi dari waktu ke waktu

  Scenario: Pengguna baru memiliki daftar riwayat audit kosong
    Given akun pengguna baru terdaftar sebagai "fresh_user@example.com"
    When pengguna membuka daftar riwayat audit
    Then sistem mengembalikan kode status 200
    And status riwayat memiliki has_any_history bernilai false
    And pesan respons adalah "Belum ada riwayat audit yang tersedia"

  Scenario: Pengguna dengan beberapa audit melihat daftar riwayat terurut
    Given pengguna terotentikasi sebagai "history_user@example.com"
    And pengguna telah menyelesaikan audit untuk klausul "Klausul Fitur Login"
    And pengguna telah menyelesaikan audit untuk klausul "Klausul Upload PDF"
    When pengguna membuka daftar riwayat audit
    Then sistem mengembalikan kode status 200
    And status riwayat memiliki has_any_history bernilai true
    And daftar item riwayat memiliki panjang minimal 2

  Scenario: Pencarian riwayat dengan kata kunci yang cocok
    Given pengguna terotentikasi sebagai "history_user@example.com"
    When pengguna mencari riwayat dengan kata kunci "Login"
    Then sistem mengembalikan kode status 200
    And item hasil pencarian memuat klausul terkait "Login"

  Scenario: Pencarian riwayat dengan kata kunci yang tidak ditemukan
    Given pengguna terotentikasi sebagai "history_user@example.com"
    When pengguna mencari riwayat dengan kata kunci "KataKunciTidakAdaSamaSekali123"
    Then sistem mengembalikan kode status 200
    And pesan respons adalah "Tidak ada riwayat yang cocok dengan pencarian"
    And daftar item pencarian adalah kosong

