@backend @frontend @evaluators
Feature: Arsitektur 3 Evaluator (Rule-Based, Traditional ML, LLM/SLM), Hasil Dimensi INVEST, Integritas Hasil, dan Ekspor Dwibahasa
  Sebagai pengguna aplikasi ReqLint
  Saya ingin dapat memilih metode evaluator (Rule-Based, Traditional ML, atau LLM/SLM), melihat rincian penilaian 6 dimensi INVEST beserta atribusi evaluatornya, serta mengekspor laporan dalam bahasa Indonesia maupun Inggris
  Agar hasil evaluasi kualitas User Story transparan, akurat sesuai evaluator yang dipilih, dan tidak pernah mengalami fallback diam-diam

  Scenario: Evaluasi menggunakan evaluator Rule-Based menghasilkan kontrak evaluasi standar dengan dimensi tidak didukung bernilai INSUFFICIENT_EVIDENCE
    Given saya sudah login sebagai pengguna terautentikasi
    When saya membuat audit baru menggunakan evaluator "rule_based" dengan judul "Audit Rule-Based" dan konten "Sebagai pelanggan, saya ingin melihat status pesanan dengan sangat cepat agar tenang."
    Then server merespons dengan status 202
    And field JSON "data.requested_evaluator" bernilai "rule_based"
    When saya mengambil detail hasil audit tersebut
    Then server merespons dengan status 200
    And field JSON "data.actual_evaluator" bernilai "rule_based"
    And field JSON "data.evaluation.evaluator" bernilai "rule_based"
    And field JSON "data.evaluation.dimensions.independent.label" bernilai "INSUFFICIENT_EVIDENCE"
    And field JSON "data.evaluation.dimensions.valuable.label" bernilai "PASS"
    And field JSON "data.evaluation.dimensions.testable.label" bernilai "FAIL"

  Scenario: Evaluasi menggunakan evaluator Traditional ML menilai keenam dimensi INVEST dengan probabilitas model
    Given saya sudah login sebagai pengguna terautentikasi
    When saya membuat audit baru menggunakan evaluator "traditional_ml" dengan judul "Audit Traditional ML" dan konten "As a registered customer, I want to view my order status within 2 seconds so that I can track my delivery."
    Then server merespons dengan status 202
    When saya mengambil detail hasil audit tersebut
    Then server merespons dengan status 200
    And field JSON "data.requested_evaluator" bernilai "traditional_ml"
    And field JSON "data.actual_evaluator" bernilai "traditional_ml"
    And field JSON "data.model_version" bernilai "2.1.0-srs-hybrid"
    And kontrak evaluasi menilai seluruh 6 dimensi INVEST lengkap dengan nilai confidence

  Scenario: Evaluasi menggunakan evaluator LLM/SLM menilai keenam dimensi INVEST beserta alasan per kriteria dan status generator
    Given saya sudah login sebagai pengguna terautentikasi
    When saya membuat audit baru menggunakan evaluator "llm" dengan judul "Audit LLM" dan konten "As a registered customer, I want to view my order status so that I can track the delivery of my purchase."
    Then server merespons dengan status 202
    When saya mengambil detail hasil audit tersebut
    Then server merespons dengan status 200
    And field JSON "data.requested_evaluator" bernilai "llm"
    And field JSON "data.actual_evaluator" bernilai "llm"
    And field JSON "data.generation.status" bernilai "DONE"
    And kontrak evaluasi memiliki alasan (rationale) pada seluruh 6 dimensi INVEST

  Scenario: Validasi evaluator tidak dikenal dan integritas hasil saat evaluator gagal tanpa fallback diam-diam
    Given saya sudah login sebagai pengguna terautentikasi
    When saya membuat audit baru menggunakan evaluator "evaluator_asing" dengan judul "Evaluator Salah" dan konten "Sebagai user, saya ingin login."
    Then server merespons dengan status 422
    And field JSON "error_code" bernilai "INVALID_EVALUATOR"
    When saya membuat audit baru menggunakan evaluator "llm" dengan judul "Simulasi Gagal LLM" dan konten "[FORCE_EVAL_FAIL] Sebagai user, saya ingin login cepat agar hemat waktu."
    Then server merespons dengan status 202
    When saya mengambil detail hasil audit tersebut
    Then server merespons dengan status 200
    And field JSON "data.status_audit" bernilai "FAILED"
    And field JSON "data.evaluator_error_code" bernilai "LLM_EVALUATOR_UNAVAILABLE"
    And detail audit gagal tidak menampilkan scorecard palsu

  Scenario: Ekspor laporan audit Markdown mendukung lokalisasi bahasa Indonesia (id) dan Inggris (en)
    Given saya sudah login sebagai pengguna terautentikasi
    And saya telah membuat audit menggunakan evaluator "traditional_ml" dengan judul "Laporan Dwibahasa" dan konten "Sebagai manajer, saya ingin melihat laporan penjualan harian dalam 2 detik agar keputusan akurat."
    When saya mengunduh laporan ekspor audit dalam format "md" berbahasa "id"
    Then server merespons dengan status 200
    And isi laporan unduhan memuat "# Laporan Audit Kebutuhan"
    When saya mengunduh laporan ekspor audit dalam format "md" berbahasa "en"
    Then server merespons dengan status 200
    And isi laporan unduhan memuat "# Requirements Audit Report"
    When saya mengunduh laporan ekspor audit dalam format "md" berbahasa "fr"
    Then server merespons dengan status 422
    And field JSON "error_code" bernilai "UNSUPPORTED_LANG"

  Scenario: Memilih evaluator Traditional ML dan LLM/SLM di halaman Editor frontend serta melihat panel Hasil Dimensi INVEST
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    When pengguna memilih mode evaluator "traditional_ml" pada halaman editor
    And pengguna menulis draf "Sebagai pelanggan, saya ingin melihat status pengiriman pesanan dalam waktu kurang dari 2 detik agar dapat memantau paket." di editor
    And pengguna menekan tombol "Analisis" di halaman editor
    Then halaman hasil audit menampilkan atribusi evaluator diminta "Traditional ML" dan evaluator aktual "Traditional ML"
    And halaman hasil audit menampilkan panel "Hasil Dimensi INVEST" dengan 6 dimensi INVEST
    When pengguna membuka halaman "/editor"
    And pengguna memilih mode evaluator "llm" pada halaman editor
    And pengguna menekan tombol "Analisis" di halaman editor
    Then halaman hasil audit menampilkan atribusi evaluator diminta "LLM/SLM" dan evaluator aktual "LLM/SLM"
    And halaman hasil audit menampilkan panel "Hasil Dimensi INVEST" dengan 6 dimensi INVEST

  Scenario: Mengganti bahasa antarmuka (ID ke EN) pada halaman Editor dan Hasil Audit menerjemahkan judul serta panel dimensi INVEST
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    Then halaman menampilkan judul utama "Editor User Story"
    When pengguna menekan tombol ganti bahasa antarmuka di Navbar
    Then bahasa antarmuka aplikasi berubah menjadi "en"
    And halaman menampilkan judul utama "User Story Editor"
    When pengguna memilih mode evaluator "traditional_ml" pada halaman editor
    And pengguna menekan tombol "Analisis" di halaman editor
    Then halaman menampilkan judul utama "User Story Audit Results"
    And halaman hasil audit menampilkan panel berlabel "INVEST Dimension Results"
    When pengguna menekan tombol ganti bahasa antarmuka di Navbar
    Then bahasa antarmuka aplikasi berubah menjadi "id"
    And halaman menampilkan judul utama "Hasil Audit User Story"
