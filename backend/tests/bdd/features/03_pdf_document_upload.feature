@pdf @upload @bdd
Feature: Upload Dokumen PDF Spesifikasi Kebutuhan
  Sebagai System Analyst
  Saya ingin mengunggah berkas PDF dokumen kebutuhan
  Agar sistem dapat mengekstrak klausul teks secara otomatis tanpa entri manual

  Scenario: Ekstraksi teks berhasil dari berkas PDF valid
    Given pengguna terotentikasi sebagai "analyst_pdf@example.com"
    And berkas PDF digital valid "spesifikasi.pdf" berisi teks "Sebagai pengguna, saya ingin sistem merespons cepat agar pekerjaan selesai."
    When pengguna mengunggah berkas PDF tersebut ke endpoint upload
    Then sistem mengembalikan kode status 200
    And status respons bernilai "success"
    And pesan respons adalah "Dokumen berhasil diekstraksi"
    And data respons memuat id_dokumen
    And teks hasil ekstraksi memuat "Sebagai pengguna, saya ingin sistem merespons cepat"

  Scenario: Pengguna tamu mengunggah berkas PDF dalam mode guest
    Given pengguna tidak menyertakan token autentikasi
    And berkas PDF digital valid "guest_spec.pdf" berisi teks "Sebagai guest, saya ingin mencoba ekstraksi PDF agar tahu fiturnya."
    When pengguna mengunggah berkas PDF tersebut ke endpoint upload
    Then sistem mengembalikan kode status 200
    And status respons bernilai "success"
    And nama dokumen yang diekstrak adalah "guest_spec.pdf"
    And id dokumen bernilai null

  Scenario: Penolakan berkas dengan ekstensi bukan PDF
    Given pengguna terotentikasi sebagai "analyst_pdf@example.com"
    And berkas tidak valid "catatan.txt" dengan konten teks biasa
    When pengguna mengunggah berkas tersebut ke endpoint upload
    Then sistem mengembalikan kode status 422
    And status respons bernilai "error"
    And kode error adalah "INVALID_FILE_FORMAT"
    And pesan respons adalah "Format file tidak valid, harap unggah dokumen .pdf"

  Scenario: Penolakan berkas PDF korup atau rusak
    Given pengguna terotentikasi sebagai "analyst_pdf@example.com"
    And berkas PDF rusak "corrupt.pdf" dengan byte acak tidak valid
    When pengguna mengunggah berkas tersebut ke endpoint upload
    Then sistem mengembalikan kode status 422
    And status respons bernilai "error"
    And pesan respons adalah "Format file tidak valid, harap unggah dokumen .pdf"

  Scenario: Penolakan berkas PDF hasil scan tanpa lapisan teks
    Given pengguna terotentikasi sebagai "analyst_pdf@example.com"
    And berkas PDF hasil scan "scanned.pdf" tanpa lapisan teks digital
    When pengguna mengunggah berkas tersebut ke endpoint upload
    Then sistem mengembalikan kode status 422
    And status respons bernilai "error"
    And kode error adalah "EMPTY_PDF_TEXT"
    And pesan respons adalah "PDF tidak memuat lapisan teks (hasil pemindaian), harap unggah dokumen digital"

  Scenario: Penolakan berkas PDF melebihi batas ukuran 10 MB
    Given pengguna terotentikasi sebagai "analyst_pdf@example.com"
    And berkas PDF "jumbo.pdf" dengan ukuran melebihi 10 megabyte
    When pengguna mengunggah berkas tersebut ke endpoint upload
    Then sistem mengembalikan kode status 413
    And status respons bernilai "error"
    And pesan respons adalah "Ukuran file melebihi batas 10 MB"

