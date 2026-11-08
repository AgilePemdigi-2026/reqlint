Feature: PDF Document Upload Integration
  Sebagai pengguna dari antarmuka web
  Saya ingin dapat mengunggah dokumen SRS berbasis PDF
  Agar layanan backend FastAPI dapat mengekstrak teks kebutuhan di dalamnya

  Scenario: Berhasil mengunggah dokumen PDF yang valid
    Given endpoint upload PDF pada server FastAPI tersedia
    When saya mengunggah file "UTS_I4_REQLINT_SRS.pdf"
    Then server merespons dengan status 200 OK
    And respons mengonfirmasi bahwa teks dokumen berhasil diekstrak
