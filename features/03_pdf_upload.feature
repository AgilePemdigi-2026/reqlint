@backend @pdf
Feature: Upload dan Ekstraksi Dokumen PDF (Backend)
  Sebagai pengguna dari antarmuka web ReqLint
  Saya ingin dapat mengunggah dokumen SRS berbasis PDF
  Agar layanan backend FastAPI dapat memvalidasi dan mengekstrak teks kebutuhan di dalamnya

  Scenario: Berhasil mengunggah dokumen PDF SRS yang valid
    Given endpoint upload PDF pada server FastAPI tersedia
    When saya mengunggah file "UTS_I4_REQLINT_SRS.pdf"
    Then server merespons dengan status 200 OK
    And respons mengonfirmasi bahwa teks dokumen berhasil diekstrak

  Scenario: Berhasil mengunggah dokumen PDF sebagai pengguna terautentikasi dan menyimpan ID dokumen
    Given saya sudah login sebagai pengguna terautentikasi
    When saya mengunggah dokumen PDF valid berisi teks "Sebagai pengguna, saya ingin sistem memproses pesanan dalam 2 detik agar transaksi lancar."
    Then server merespons dengan status 200
    And field JSON "message" bernilai "Dokumen berhasil diekstraksi"
    And data respons memiliki "id_dokumen" yang tidak kosong

  Scenario: Menolak unggahan berkas dengan ekstensi selain PDF (.txt)
    Given endpoint upload PDF pada server FastAPI tersedia
    When saya mengunggah berkas bernama "catatan.txt" dengan isi "Ini bukan PDF"
    Then server merespons dengan status 422
    And field JSON "error_code" bernilai "INVALID_FILE_FORMAT"

  Scenario: Menolak unggahan berkas PDF yang rusak (corrupt magic bytes)
    Given endpoint upload PDF pada server FastAPI tersedia
    When saya mengunggah berkas bernama "rusak.pdf" dengan isi "bukan header pdf asli"
    Then server merespons dengan status 422
    And field JSON "error_code" bernilai "INVALID_FILE_FORMAT"

  Scenario: Menolak unggahan PDF hasil pindaian tanpa lapisan teks (kosong)
    Given endpoint upload PDF pada server FastAPI tersedia
    When saya mengunggah dokumen PDF kosong tanpa lapisan teks
    Then server merespons dengan status 422
    And field JSON "error_code" bernilai "EMPTY_PDF_TEXT"

  Scenario: Menolak unggahan berkas PDF yang melebihi batas 10 MB
    Given endpoint upload PDF pada server FastAPI tersedia
    When saya mengunggah dokumen PDF berukuran lebih dari 10 MB
    Then server merespons dengan status 413
    And field JSON "error_code" bernilai "FILE_TOO_LARGE"

