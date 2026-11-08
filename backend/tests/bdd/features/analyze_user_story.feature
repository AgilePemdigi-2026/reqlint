Feature: User Story INVEST Linter
  Sebagai pengguna ReqLint
  Saya ingin sistem dapat menganalisis kelemahan user story
  Agar saya bisa mendapatkan rekomendasi perbaikan berdasarkan kriteria INVEST

  Scenario: Menganalisis user story Bahasa Indonesia yang lemah
    Given sistem ReqLint berjalan dan endpoint API siap
    When saya mengirimkan user story "Sebagai pembeli, saya sebaiknya dapat membayar transaksi dengan cepat."
    Then sistem mendeteksi input sebagai bahasa "id"
    And sistem mengembalikan temuan cacat "WEAK_DIRECTIVE" dan "AMBIGUITY"
    And sistem memberikan rekomendasi revisi user story
