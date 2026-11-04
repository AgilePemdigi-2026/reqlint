@scorecard @invest @bdd
Feature: Scorecard Kualitas, Deteksi Smells, dan Rekomendasi AI
  Sebagai System Analyst atau QA Engineer
  Saya ingin melihat kartu skor kualitas, daftar temuan kecacatan, usulan AI Rewrite, dan kriteria penerimaan Gherkin
  Agar klausul kebutuhan memenuhi standar INVEST dan bebas dari ambiguitas

  Scenario: Evaluasi User Story bermasalah menghasilkan skor rendah dan temuan cacat
    Given pengguna terotentikasi sebagai "analyst_eval@example.com"
    And draf audit tersimpan untuk teks:
      """
      Sebagai user, saya ingin proses login sistem berjalan dengan sangat cepat dan user-friendly agar tidak membuang waktu.
      """
    When proses analisis pipeline selesai dijalankan
    And pengguna mengambil rincian detail audit
    Then sistem mengembalikan kode status 200
    And status kualitas audit berstatus "Needs Improvement"
    And skor kualitas berada di bawah 70
    And temuan cacat mendeteksi kategori ambiguitas "sangat cepat"
    And rekomendasi AI menghasilkan "ai_rewrite"
    And kriteria penerimaan otomatis memiliki format Given When Then

  Scenario: Evaluasi User Story ideal menghasilkan skor tinggi dan nol cacat
    Given pengguna terotentikasi sebagai "analyst_eval@example.com"
    And draf audit tersimpan untuk teks ideal:
      """
      Sebagai System Analyst, saya ingin melihat riwayat audit pada tabel log agar dapat melacak perkembangan revisi draf kebutuhan.
      """
    When proses analisis pipeline selesai dijalankan
    And pengguna mengambil rincian detail audit
    Then sistem mengembalikan kode status 200
    And skor kualitas mencapai minimal 85
    And jumlah temuan cacat adalah 0
    And analisis kepatuhan INVEST terpenuhi

