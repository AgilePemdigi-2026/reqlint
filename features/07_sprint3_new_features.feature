@frontend @sprint3
Feature: Fitur Baru Sprint 3 ReqLint (Lupa & Reset Kata Sandi, Panduan Pengguna, Hubungi Kami, Toggle Bahasa UI ID/EN, dan Filter Riwayat)
  Sebagai pengguna aplikasi web ReqLint (Next.js frontend-qa & FastAPI backend)
  Saya ingin dapat memulihkan kata sandi, membaca panduan pengguna, menghubungi tim melalui formulir kontak, mengganti bahasa antarmuka (ID/EN), serta memfilter riwayat audit
  Agar pengalaman penggunaan aplikasi ReqLint menjadi lebih lengkap, dwibahasa, dan mudah dinavigasi

  Scenario: Proteksi halaman terproteksi baru (/help dan /contact) mengarahkan pengguna yang belum login ke /login
    Given pengguna belum login pada frontend ReqLint
    When pengguna mencoba membuka halaman "/help"
    Then halaman diarahkan ke "/login"
    When pengguna mencoba membuka halaman "/contact"
    Then halaman diarahkan ke "/login"

  Scenario: Mengajukan permintaan Lupa Kata Sandi pada halaman /forgot-password
    Given pengguna dengan email "budi.sprint3@reqlint.app" dan sandi "SandiLama123!" sudah terdaftar
    And pengguna membuka halaman "/forgot-password" pada frontend ReqLint
    When pengguna mengisi email "budi.sprint3@reqlint.app" pada form lupa kata sandi dan menekan tombol "Kirim Tautan Reset"
    Then halaman lupa kata sandi menampilkan pesan konfirmasi "Jika email terdaftar, tautan reset telah dikirim. Silakan cek email Anda."

  Scenario: Membuka halaman /reset-password tanpa parameter token menampilkan peringatan token tidak valid
    Given pengguna membuka halaman "/reset-password" pada frontend ReqLint
    Then halaman reset kata sandi menampilkan pesan "Token reset tidak valid atau sudah kedaluwarsa."

  Scenario: Mereset kata sandi melalui halaman /reset-password dengan token valid lalu login menggunakan sandi baru
    Given pengguna dengan email "citra.reset@reqlint.app" dan sandi "SandiAwal123!" sudah terdaftar
    When pengguna meminta tautan reset kata sandi pada halaman "/forgot-password" untuk email "citra.reset@reqlint.app"
    And pengguna membuka halaman "/reset-password" menggunakan token reset yang diterima
    And pengguna mengisi kata sandi baru "SandiBaru999!" dan konfirmasi "SandiBaru999!" lalu menekan tombol "Reset Kata Sandi"
    Then halaman reset kata sandi menampilkan pesan "Kata sandi berhasil diperbarui. Silakan masuk."
    When pengguna masuk melalui halaman "/login" dengan email "citra.reset@reqlint.app" dan sandi "SandiBaru999!"
    Then pengguna berhasil masuk dan diarahkan ke halaman "/editor"

  Scenario: Membuka halaman Panduan Pengguna (/help) dan melihat panduan memulai, tabel Grade A-E, kategori temuan, serta tips
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    When pengguna membuka halaman "/help"
    Then halaman menampilkan judul utama "Panduan Pengguna"
    And halaman panduan menampilkan bagian "Memulai", "Memahami Skor & Grade", "Kategori Temuan", dan "Tips Menulis User Story"
    And halaman panduan menampilkan seluruh kategori cacat "Ambiguity", "Tidak Lengkap", "Weak Directive", dan "Passive Voice"

  Scenario: Membuka halaman Hubungi Kami (/contact), melihat informasi kontak & tim pengembang, serta mengirim pesan
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    When pengguna membuka halaman "/contact"
    Then halaman menampilkan judul utama "Hubungi Kami"
    And halaman kontak menampilkan bagian "Informasi Kontak" dan "Tim Pengembang" beserta email "support@reqlint.app"
    When pengguna mengisi form kontak dengan nama "Fajar Akbar", email "fajar@reqlint.app", subjek "Masukan Fitur Sprint 3", dan pesan "Fitur panduan dan dwibahasa sangat membantu tim QA kami."
    And pengguna menekan tombol "Kirim Pesan" pada halaman kontak
    Then halaman kontak menampilkan pesan sukses "Pesan berhasil dikirim! Kami akan segera membalas."

  Scenario: Mengganti bahasa antarmuka (Language Toggle ID ke EN dan kembali ke ID) pada Navbar
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    When pengguna membuka halaman "/help"
    Then halaman menampilkan judul utama "Panduan Pengguna"
    When pengguna menekan tombol ganti bahasa antarmuka di Navbar
    Then bahasa antarmuka aplikasi berubah menjadi "en"
    And menu navigasi utama menampilkan label "Audit History", "Help", dan "Contact"
    And halaman menampilkan judul utama "User Guide"
    When pengguna membuka halaman "/contact"
    Then halaman menampilkan judul utama "Contact Us"
    When pengguna menekan tombol ganti bahasa antarmuka di Navbar
    Then bahasa antarmuka aplikasi berubah menjadi "id"
    And halaman menampilkan judul utama "Hubungi Kami"

  Scenario: Memfilter dan mengurutkan riwayat audit di halaman History Audit (/history) serta mereset filter
    Given pengguna sudah masuk menggunakan akun demo di halaman "/editor"
    When pengguna menulis draf "Sebagai pelanggan, saya ingin proses pembayaran berjalan sangat cepat agar praktis." di editor
    And pengguna menekan tombol "Analisis" di halaman editor
    When pengguna memilih bahasa analisis "en" pada editor
    And pengguna menulis draf "As a customer, I want to receive payment confirmation within 2 seconds so that I know my order succeeded." di editor
    And pengguna menekan tombol "Analisis" di halaman editor
    When pengguna membuka halaman "/history"
    Then daftar riwayat audit menampilkan minimal 2 item audit
    When pengguna memilih filter bahasa "en" di halaman history
    Then daftar riwayat audit yang difilter menampilkan 1 item berbahasa "en"
    When pengguna memilih filter kategori temuan "ambiguity" dan bahasa "all" di halaman history
    Then daftar riwayat audit yang difilter menampilkan 1 item dengan temuan "AMBIGUITY"
    When pengguna memilih pengurutan riwayat "score-desc" dan mereset filter di halaman history
    Then daftar riwayat audit kembali menampilkan seluruh item dengan urutan skor tertinggi di posisi pertama

