@frontend @ui
Feature: Antarmuka Pengguna Frontend ReqLint (Landing, Auth, Editor, Upload PDF, Hasil Audit, Riwayat, dan Tema)
  Sebagai pengguna aplikasi web ReqLint (Next.js frontend-qa)
  Saya ingin menggunakan seluruh fitur UI dari halaman publik, autentikasi, editor, hingga hasil audit dan riwayat
  Agar saya dapat menganalisis dan memperbaiki User Story secara interaktif

  Scenario: Membuka Landing Page publik dan melihat bagian fitur serta standar ISO 29148 & INVEST
    Given pengguna membuka halaman utama "/" pada frontend ReqLint
    Then halaman menampilkan komponen Landing Page beserta bagian "ISO/IEC/IEEE 29148" dan "INVEST"

  Scenario: Proteksi halaman terproteksi (/editor dan /history) mengarahkan pengguna yang belum login ke /login
    Given pengguna belum login pada frontend ReqLint
    When pengguna mencoba membuka halaman "/editor"
    Then halaman diarahkan ke "/login"

  Scenario: Registrasi akun baru pada halaman Register frontend mengarahkan ke halaman Login
    Given pengguna membuka halaman "/register" pada frontend ReqLint
    When pengguna mengisi form registrasi dengan nama "Andi Pratama", email "andi@reqlint.app", sandi "AndiPass123!", dan menyetujui ketentuan layanan
    Then notifikasi toast frontend menampilkan "Pendaftaran berhasil, silakan masuk"
    And halaman diarahkan ke "/login"
    When pengguna masuk melalui halaman "/login" dengan email "andi@reqlint.app" dan sandi "AndiPass123!"
    Then pengguna berhasil masuk dan diarahkan ke halaman "/editor"

  Scenario: Masuk menggunakan tombol Akun Demo pada halaman Login frontend
    Given pengguna membuka halaman "/login" pada frontend ReqLint
    When pengguna menekan tombol "Gunakan akun demo"
    Then pengguna berhasil masuk sebagai "Fajar Akbar" dan diarahkan ke halaman "/editor"

  Scenario: Memilih bahasa analisis, memuat Contoh Template, dan mengunggah dokumen PDF ke Editor
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    When pengguna memilih bahasa analisis "en" pada editor
    And pengguna memilih contoh template "login" pada editor
    Then editor memuat draf user story berbahasa "en"
    When pengguna mengunggah berkas PDF "UTS_I4_REQLINT_SRS.pdf" melalui tombol Upload PDF di editor
    Then notifikasi toast frontend menampilkan "Berkas dimuat ke editor."
    And teks di dalam editor terisi dengan hasil ekstraksi dokumen PDF

  Scenario: Menjalankan analisis dari Editor, melihat Quality Scorecard, Acceptance Criteria, dan menerapkan Rekomendasi Perbaikan
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    When pengguna menulis draf "Sebagai pembeli, saya sebaiknya dapat membayar pesanan dengan sangat cepat dan user-friendly agar hemat waktu." di editor
    And pengguna menekan tombol "Analisis" di halaman editor
    Then pengguna diarahkan ke halaman hasil audit "/audit/AUD-101"
    And halaman hasil audit menampilkan "Quality Scorecard", "Temuan cacat", "Rekomendasi Perbaikan", dan "Acceptance Criteria"
    When pengguna menekan tombol "Apply" pada kartu Rekomendasi Perbaikan
    Then audit baru "/audit/AUD-102" dibuat dengan skor kualitas yang lebih tinggi dari sebelumnya

  Scenario: Mengekspor hasil audit dari halaman Audit Frontend ke Markdown, CSV, dan JSON
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    And pengguna telah menjalankan analisis draf di editor
    When pengguna mengekspor hasil audit di frontend ke format "md"
    Then berkas unduhan berakhir dengan ekstensi ".md"
    When pengguna mengekspor hasil audit di frontend ke format "csv"
    Then berkas unduhan berakhir dengan ekstensi ".csv"
    When pengguna mengekspor hasil audit di frontend ke format "json"
    Then berkas unduhan berakhir dengan ekstensi ".json"

  Scenario: Mengelola riwayat audit di halaman History Audit (cari, hapus item, dan hapus semua)
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    And pengguna telah menjalankan analisis draf di editor
    When pengguna membuka halaman "/history"
    Then daftar riwayat audit menampilkan minimal 1 item audit
    When pengguna menghapus seluruh riwayat audit di halaman history
    Then daftar riwayat audit menjadi kosong dan menampilkan pesan "Belum ada riwayat audit"

  Scenario: Mengganti tema tampilan (Gelap / Terang) dan Keluar (Logout) dari akun
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    When pengguna menekan tombol ganti tema di menu akun
    Then tema aplikasi berubah menjadi "dark"
    When pengguna menekan tombol "Keluar" di menu akun
    Then pengguna keluar dari sesi dan diarahkan ke "/login"

