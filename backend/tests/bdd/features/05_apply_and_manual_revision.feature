@revision @apply @bdd
Feature: Penerapan Rekomendasi 1-Click dan Revisi Manual
  Sebagai System Analyst
  Saya ingin menerapkan rekomendasi AI dengan 1-Click atau menyunting draf secara manual
  Agar spesifikasi kebutuhan segera diperbaiki ke versi terstandarisasi

  Scenario: Penerapan 1-Click rekomendasi AI memperbarui draf
    Given pengguna terotentikasi sebagai "analyst_rev@example.com"
    And audit yang telah selesai untuk draf "Sebagai pengguna, saya ingin sistem cepat agar hemat waktu."
    When pengguna menekan 1-Click Apply untuk menerapkan saran perbaikan
    Then sistem mengembalikan kode status 200
    And pesan respons adalah "Draf berhasil diperbarui"
    And status revisi draf berubah menjadi "SUDAH_DIREVISI"
    And label skor diperbarui menjadi "Skor Kualitas Terkini"

  Scenario: Penyuntingan revisi manual dengan teks baru yang terukur
    Given pengguna terotentikasi sebagai "analyst_rev@example.com"
    And audit yang telah selesai untuk draf "Sebagai pengguna, saya ingin sistem cepat agar hemat waktu."
    When pengguna mengirimkan revisi manual "Sebagai pengguna, saya ingin respons sistem kurang dari 2 detik agar pekerjaan tuntas."
    Then sistem mengembalikan kode status 200
    And status respons bernilai "success"
    And pesan respons adalah "Draf berhasil diperbarui"
    And skor kualitas draf setelah revisi lebih besar dari 0

  Scenario: Penolakan penyimpanan revisi manual jika teks revisi kosong
    Given pengguna terotentikasi sebagai "analyst_rev@example.com"
    And audit yang telah selesai untuk draf "Sebagai pengguna, saya ingin sistem cepat agar hemat waktu."
    When pengguna mengirimkan revisi manual berupa teks kosong
    Then sistem mengembalikan kode status 422
    And status respons bernilai "error"
    And pesan respons adalah "Draf kebutuhan tidak boleh kosong"

