@audit @input_story @bdd
Feature: Input Teks User Story dan Inisiasi Audit
  Sebagai System Analyst
  Saya ingin memasukkan draf Agile User Story berbasis format Connextra
  Agar ReqLint dapat menganalisis kejelasan kalimat dan memulai pipeline audit

  Scenario: Penolakan draf kebutuhan kosong atau hanya spasi
    Given pengguna terotentikasi sebagai "analyst_input@example.com"
    When pengguna mengirimkan draf kebutuhan yang kosong
    Then sistem mengembalikan kode status 422
    And status respons bernilai "error"
    And kode error adalah "EMPTY_DRAFT"
    And pesan respons adalah "Draf kebutuhan tidak boleh kosong"

  Scenario: Penerimaan draf kebutuhan valid untuk dianalisis
    Given pengguna terotentikasi sebagai "analyst_input@example.com"
    When pengguna mengirimkan draf kebutuhan "Sebagai pengguna, saya ingin sistem merespons cepat agar pekerjaan selesai." dengan judul "Kecepatan Respon"
    Then sistem mengembalikan kode status 202
    And status respons bernilai "success"
    And pesan respons adalah "Draf diterima dan sedang dianalisis"
    And respons memuat id_audit dan url polling status

  Scenario: Eksekusi pipeline audit selesai dengan status COMPLETED
    Given pengguna terotentikasi sebagai "analyst_input@example.com"
    And draf kebutuhan "Sebagai user, saya ingin proses login sistem berjalan dengan sangat cepat dan user-friendly agar tidak membuang waktu." telah diterima sistem
    When pipeline audit selesai diproses
    And pengguna memeriksa status audit
    Then status audit adalah "COMPLETED"
    And status stage2 adalah "DONE"

  Scenario: Audit langsung spesifikasi kebutuhan via endpoint heuristik dwibahasa
    Given teks kebutuhan Bahasa Indonesia: "Sebagai pembeli, saya sebaiknya dapat membayar transaksi dengan cepat, sehingga pesanan segera diproses."
    When pengguna meminta audit heuristik langsung dengan bahasa "id"
    Then sistem mengembalikan kode status 200
    And bahasa terdeteksi adalah "id"
    And skor kualitas tersedia dalam respons
    And daftar temuan smells tidak kosong
    And rekomendasi revisi INVEST tersedia dalam respons

