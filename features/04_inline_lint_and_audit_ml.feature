@backend @lint @analyzer
Feature: Analisis User Story INVEST ML dan Real-Time Inline Linting (Backend)
  Sebagai pengguna ReqLint
  Saya ingin sistem dapat menganalisis kelemahan user story dalam Bahasa Indonesia maupun Inggris
  Agar saya mendapatkan deteksi cacat (Ambiguity, Weak Directive, Incompleteness, Passive Voice) dan saran revisi INVEST

  Scenario: Menganalisis user story Bahasa Indonesia yang lemah
    Given sistem ReqLint berjalan dan endpoint API siap
    When saya mengirimkan user story "Sebagai pembeli, saya sebaiknya dapat membayar transaksi dengan cepat."
    Then sistem mendeteksi input sebagai bahasa "id"
    And sistem mengembalikan temuan cacat "WEAK_DIRECTIVE" dan "AMBIGUITY"
    And sistem memberikan rekomendasi revisi user story

  Scenario: Menganalisis user story Bahasa Inggris yang memiliki cacat ambiguitas dan direktif lemah
    Given sistem ReqLint berjalan dan endpoint API siap
    When saya mengirimkan user story "As a buyer, I should be able to checkout easily and fast."
    Then sistem mendeteksi input sebagai bahasa "en"
    And sistem mengembalikan temuan cacat "WEAK_DIRECTIVE" dan "AMBIGUITY"
    And sistem memberikan rekomendasi revisi user story

  Scenario: Mendeteksi kalimat pasif (Passive Voice) dan ketidaklengkapan struktur Connextra
    Given sistem ReqLint berjalan dan endpoint API siap
    When saya mengirimkan user story "Transaksi pengguna diproses oleh sistem."
    Then sistem mendeteksi input sebagai bahasa "en"
    And sistem mengembalikan temuan cacat "PASSIVE_VOICE" dan "TIDAK_LENGKAP"

  Scenario: Inline Linting (/api/v1/lint) pada teks kosong menghasilkan skor 100
    Given saya sudah login sebagai pengguna terautentikasi
    When saya menjalankan inline lint dengan konten ""
    Then server merespons dengan status 200
    And field JSON "data.skor_perkiraan" bernilai angka 100.0
    And field JSON "data.ringkasan.total" bernilai angka 0

  Scenario: Inline Linting (/api/v1/lint) mendeteksi kata ambigu secara real-time
    Given saya sudah login sebagai pengguna terautentikasi
    When saya menjalankan inline lint dengan konten "Sebagai admin, saya ingin aplikasi berjalan cepat dan mudah agar pekerjaan lancar."
    Then server merespons dengan status 200
    And jumlah temuan pada inline lint lebih dari 0

