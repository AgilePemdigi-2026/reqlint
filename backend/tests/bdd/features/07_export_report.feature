@export @reporting @bdd
Feature: Ekspor Laporan Hasil Audit Multi-Format
  Sebagai System Analyst atau Product Manager
  Saya ingin mengekspor laporan hasil audit ke dalam format JSON, Markdown, dan PDF
  Agar dapat didokumentasikan ke repositori atau dipresentasikan ke pemangku kepentingan

  Scenario: Ekspor hasil audit ke format JSON
    Given pengguna terotentikasi sebagai "exporter@example.com"
    And audit yang telah selesai dengan ID siap diekspor
    When pengguna meminta ekspor hasil audit dengan format "json"
    Then sistem mengembalikan kode status 200
    And tipe konten header adalah "application/json"
    And header content-disposition memuat nama file "reqlint-audit"

  Scenario: Ekspor hasil audit ke format Markdown
    Given pengguna terotentikasi sebagai "exporter@example.com"
    And audit yang telah selesai dengan ID siap diekspor
    When pengguna meminta ekspor hasil audit dengan format "md"
    Then sistem mengembalikan kode status 200
    And tipe konten header memuat "text/markdown"

  Scenario: Ekspor hasil audit ke format PDF
    Given pengguna terotentikasi sebagai "exporter@example.com"
    And audit yang telah selesai dengan ID siap diekspor
    When pengguna meminta ekspor hasil audit dengan format "pdf"
    Then sistem mengembalikan kode status 200
    And tipe konten header adalah "application/pdf"

  Scenario: Penolakan ekspor untuk format yang tidak didukung
    Given pengguna terotentikasi sebagai "exporter@example.com"
    And audit yang telah selesai dengan ID siap diekspor
    When pengguna meminta ekspor hasil audit dengan format "docx"
    Then sistem mengembalikan kode status 422
    And pesan respons adalah "Format tidak didukung"

