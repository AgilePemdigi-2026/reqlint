@backend @audits
Feature: Siklus Hidup Audit Kebutuhan, Revisi, Riwayat, dan Ekspor Laporan (Backend)
  Sebagai pengguna terautentikasi ReqLint
  Saya ingin membuat audit, melihat scorecard ISO 29148 & INVEST, menerapkan revisi AI atau manual, mencari riwayat, serta mengekspor laporan
  Agar proses penjaminan kualitas dokumen kebutuhan berjalan menyeluruh

  Scenario: Menolak pembuatan audit jika draf kebutuhan kosong
    Given saya sudah login sebagai pengguna terautentikasi
    When saya membuat audit baru dengan judul "Draf Kosong" dan konten "   "
    Then server merespons dengan status 422
    And field JSON "error_code" bernilai "EMPTY_DRAFT"

  Scenario: Siklus penuh audit kebutuhan dari pembuatan hingga penerapan rekomendasi AI (1-Click Apply) dan revisi manual
    Given saya sudah login sebagai pengguna terautentikasi
    When saya membuat audit baru dengan judul "Kecepatan Sistem" dan konten "Sebagai pengguna, saya sebaiknya dapat mengakses dashboard dengan cepat."
    Then server merespons dengan status 202
    And saya memeriksa status polling audit hingga "COMPLETED"
    When saya mengambil detail hasil audit tersebut
    Then detail audit memiliki scorecard, ringkasan cacat, daftar temuan, dan rekomendasi AI
    When saya menerapkan rekomendasi AI "rewrite" dan "acceptance_criteria" pada audit tersebut
    Then server merespons dengan status 200
    And field JSON "data.status_revisi" bernilai "SUDAH_DIREVISI"
    And teks revisi memuat "Acceptance Criteria"
    When saya menyimpan revisi manual "Sebagai pengguna, saya ingin mengakses dashboard dalam waktu kurang dari 2 detik agar dapat memantau data." pada audit tersebut
    Then server merespons dengan status 200
    And field JSON "data.status_revisi" bernilai "SUDAH_DIREVISI"

  Scenario: Proteksi keamanan kepemilikan audit antar-pengguna (SEC-4: mengembalikan 404, bukan 403)
    Given saya sudah login sebagai pengguna terautentikasi
    And saya telah membuat audit dengan judul "Audit Rahasia User A" dan konten "Sebagai admin, saya ingin sistem aman agar data terlindungi."
    And pengguna kedua terdaftar dan login
    When pengguna kedua mencoba mengakses detail audit milik pengguna pertama
    Then server merespons dengan status 404
    And field JSON "error_code" bernilai "AUDIT_NOT_FOUND"

  Scenario: Mencari dan memfilter daftar riwayat audit pengguna
    Given saya sudah login sebagai pengguna terautentikasi
    And saya telah membuat audit dengan judul "Modul Pembayaran Cepat" dan konten "Sebagai pembeli, saya ingin pembayaran cepat agar pesanan selesai."
    When saya mengambil daftar riwayat audit
    Then server merespons dengan status 200
    And field JSON "data.has_any_history" bernilai boolean true
    When saya mencari riwayat audit dengan kata kunci "kata_kunci_tidak_ada_xyz"
    Then server merespons dengan status 200
    And field JSON "message" bernilai "Tidak ada riwayat yang cocok dengan pencarian"

  Scenario: Mengekspor laporan audit ke format JSON, Markdown, dan PDF serta menolak format tidak valid
    Given saya sudah login sebagai pengguna terautentikasi
    And saya telah membuat audit dengan judul "Laporan Ekspor" dan konten "Sebagai manajer, saya ingin laporan cepat agar keputusan tepat."
    When saya mengekspor audit tersebut dalam format "json"
    Then server merespons dengan status 200
    And header respons "content-type" memuat "application/json"
    When saya mengekspor audit tersebut dalam format "md"
    Then server merespons dengan status 200
    And header respons "content-type" memuat "text/markdown"
    When saya mengekspor audit tersebut dalam format "pdf"
    Then server merespons dengan status 200
    And header respons "content-type" memuat "application/pdf"
    When saya mengekspor audit tersebut dalam format "docx"
    Then server merespons dengan status 422
    And field JSON "error_code" bernilai "UNSUPPORTED_FORMAT"

  Scenario: Menjalankan analisis ulang (Reanalyze) pada audit yang sudah selesai
    Given saya sudah login sebagai pengguna terautentikasi
    And saya telah membuat audit dengan judul "Uji Analisis Ulang" dan konten "Sebagai user, saya ingin fitur mudah digunakan agar efisien."
    When saya meminta analisis ulang pada audit tersebut
    Then server merespons dengan status 202
    And field JSON "message" bernilai "Analisis ulang dimulai"

