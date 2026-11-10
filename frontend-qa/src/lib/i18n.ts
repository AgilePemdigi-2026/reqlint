'use client';

import { createLocalStore } from './store';

export type UILocale = 'id' | 'en';

const localeStore = createLocalStore<UILocale>('reqlint.ui_locale', 'id');

export function getUILocale(): UILocale {
  return localeStore.get();
}

export function setUILocale(locale: UILocale) {
  localeStore.set(locale);
}

export function useUILocale(): UILocale {
  return localeStore.useValue();
}

/* ────────────────────────────────────────────
   Kamus terjemahan UI Lengkap (Bahasa Indonesia & English)
   ──────────────────────────────────────────── */

const translations: Record<string, Record<UILocale, string>> = {
  // ─── Navbar & Shell ───
  'nav.editor': { id: 'Editor', en: 'Editor' },
  'nav.history': { id: 'History Audit', en: 'Audit History' },
  'nav.help': { id: 'Panduan', en: 'Help Guide' },
  'nav.contact': { id: 'Kontak', en: 'Contact' },
  'nav.workspace': { id: 'Personal workspace', en: 'Personal workspace' },
  'nav.notifications': { id: 'Notifikasi', en: 'Notifications' },
  'nav.notif_welcome': { id: 'Selamat datang di ReqLint. Belum ada notifikasi lain.', en: 'Welcome to ReqLint. No other notifications.' },
  'nav.account_menu': { id: 'Menu akun', en: 'Account menu' },
  'nav.theme_light': { id: 'Tema terang', en: 'Light theme' },
  'nav.theme_dark': { id: 'Tema gelap', en: 'Dark theme' },
  'nav.logout': { id: 'Keluar', en: 'Sign out' },
  'nav.footer_jwt': { id: 'Sesi autentikasi diamankan dengan token JWT FastAPI.', en: 'Authentication session secured with FastAPI JWT token.' },
  'nav.version': { id: 'ReqLint v1.0 · Arsitektur Terintegrasi', en: 'ReqLint v1.0 · Integrated Architecture' },

  // ─── Landing Navigation ───
  'landing.features': { id: 'Fitur', en: 'Features' },
  'landing.how_it_works': { id: 'Cara Kerja', en: 'How It Works' },
  'landing.standards': { id: 'Standar', en: 'Standards' },
  'landing.faq': { id: 'FAQ', en: 'FAQ' },
  'landing.open_workspace': { id: 'Buka workspace', en: 'Open workspace' },
  'landing.login': { id: 'Masuk', en: 'Sign in' },
  'landing.open_editor': { id: 'Buka editor', en: 'Open editor' },
  'landing.start_free': { id: 'Mulai gratis', en: 'Get started free' },

  // ─── Landing Hero & Sections ───
  'hero.badge': { id: 'Mengacu pada ISO 29148 & INVEST', en: 'Aligned with ISO 29148 & INVEST' },
  'hero.title_1': { id: 'Cek kualitas User Story', en: 'Check User Story quality' },
  'hero.title_2': { id: 'sebelum jadi bug.', en: 'before it becomes a bug.' },
  'hero.description': {
    id: 'ReqLint mengaudit draf kebutuhan Anda secara real-time: menandai istilah ambigu, kalimat pasif, dan klausul yang tidak bisa diuji — lengkap dengan skor, saran revisi, dan acceptance criteria. Cocok untuk analis bisnis, product owner, QA, dan mahasiswa rekayasa perangkat lunak.',
    en: 'ReqLint audits your requirements draft in real-time: flagging ambiguous terms, passive voice, and non-testable clauses — complete with score, revision recommendations, and acceptance criteria. Ideal for business analysts, product owners, QA, and software engineering students.',
  },
  'hero.start_box_title': { id: 'Mulai dalam hitungan detik', en: 'Start in seconds' },
  'hero.start_box_desc': {
    id: 'Tempel dari Jira, Confluence, Notion, atau Google Docs — atau unggah PDF. Tanpa instalasi.',
    en: 'Paste from Jira, Confluence, Notion, or Google Docs — or upload PDF. No installation required.',
  },
  'hero.cta_register': { id: 'Daftar gratis', en: 'Sign up free' },
  'hero.cta_editor': { id: 'Buka editor', en: 'Open editor' },
  'hero.security_note': {
    id: 'Analisis berjalan di browser Anda — teks tidak dikirim ke server pihak ketiga.',
    en: 'Analysis runs in your browser — text is never shared with third-party servers.',
  },

  // ─── Login Page ───
  'login.title': { id: 'Selamat datang kembali', en: 'Welcome back' },
  'login.subtitle': { id: 'Masuk untuk melanjutkan ke ruang kerja Anda.', en: 'Sign in to continue to your workspace.' },
  'login.email': { id: 'Email', en: 'Email' },
  'login.password': { id: 'Kata Sandi', en: 'Password' },
  'login.password_placeholder': { id: 'Masukkan kata sandi Anda', en: 'Enter your password' },
  'login.forgot': { id: 'Lupa kata sandi?', en: 'Forgot password?' },
  'login.submit': { id: 'Masuk', en: 'Sign in' },
  'login.processing': { id: 'Memproses...', en: 'Processing...' },
  'login.no_account': { id: 'Belum punya akun?', en: "Don't have an account?" },
  'login.register': { id: 'Daftar', en: 'Register' },
  'login.demo': { id: 'Gunakan akun demo', en: 'Use demo account' },
  'login.demo_connecting': { id: 'Menghubungkan...', en: 'Connecting...' },
  'login.demo_success': { id: 'Masuk menggunakan akun demo.', en: 'Signed in with demo account.' },
  'login.success': { id: 'Login berhasil. Mengalihkan ke editor...', en: 'Login successful. Redirecting to editor...' },
  'login.jwt_info': { id: 'Terhubung dengan REST API Backend FastAPI & JWT Token.', en: 'Connected with FastAPI Backend REST API & JWT Token.' },

  // ─── Register Page ───
  'register.title': { id: 'Buat akun baru', en: 'Create a new account' },
  'register.subtitle': { id: 'Mulai audit kualitas User Story Anda dengan standar ISO 29148 dan INVEST.', en: 'Start auditing your User Story quality with ISO 29148 and INVEST standards.' },
  'register.name': { id: 'Nama', en: 'Name' },
  'register.name_placeholder': { id: 'Nama lengkap Anda', en: 'Your full name' },
  'register.email': { id: 'Email', en: 'Email' },
  'register.password': { id: 'Kata Sandi', en: 'Password' },
  'register.password_placeholder': { id: 'Minimal 8 karakter (huruf dan angka)', en: 'Minimum 8 characters (letters and numbers)' },
  'register.password_hint': { id: 'Gunakan huruf dan angka (minimal 8 karakter)', en: 'Use letters and numbers (minimum 8 characters)' },
  'register.confirm': { id: 'Konfirmasi Kata Sandi', en: 'Confirm Password' },
  'register.confirm_placeholder': { id: 'Ulangi kata sandi Anda', en: 'Repeat your password' },
  'register.terms_agree': { id: 'Saya menyetujui', en: 'I agree to the' },
  'register.terms_tos': { id: 'Ketentuan Layanan', en: 'Terms of Service' },
  'register.terms_and': { id: 'dan', en: 'and' },
  'register.terms_privacy': { id: 'Kebijakan Privasi', en: 'Privacy Policy' },
  'register.submit': { id: 'Daftar', en: 'Register' },
  'register.submitting': { id: 'Mendaftarkan...', en: 'Registering...' },
  'register.has_account': { id: 'Sudah punya akun?', en: 'Already have an account?' },
  'register.login': { id: 'Masuk', en: 'Sign in' },
  'register.success': { id: 'Pendaftaran berhasil, silakan masuk', en: 'Registration successful, please sign in' },
  'register.terms_toast': { id: 'Halaman kebijakan privasi dan ketentuan dapat diakses di portal dokumentasi.', en: 'Privacy policy and terms pages are accessible in the documentation portal.' },

  // ─── Editor Page ───
  'editor.crumb': { id: 'Workspace / Draf Kebutuhan', en: 'Workspace / Requirements Draft' },
  'editor.title': { id: 'Editor User Story', en: 'User Story Editor' },
  'editor.subtitle': {
    id: 'Tulis atau tempel draf kebutuhan Anda. ReqLint akan mengauditnya menggunakan model INVEST & ISO 29148.',
    en: 'Write or paste your requirements draft. ReqLint will audit it using INVEST & ISO 29148 models.',
  },
  'editor.backend_connected': { id: 'Backend FastAPI Terhubung', en: 'FastAPI Backend Connected' },
  'editor.select_lang': { id: 'Pilih bahasa analisis', en: 'Select analysis language' },
  'editor.upload_pdf': { id: 'Upload PDF', en: 'Upload PDF' },
  'editor.extracting': { id: 'Mengekstrak…', en: 'Extracting…' },
  'editor.template_samples': { id: 'Contoh Template', en: 'Sample Templates' },
  'editor.empty_prompt': { id: 'Tulis atau tempel draf kebutuhan untuk mulai.', en: 'Write or paste a requirements draft to get started.' },
  'editor.flagged_warn': {
    id: 'Istilah yang digarisbawahi mungkin tidak terukur. Jalankan analisis untuk melihat evaluasi model INVEST.',
    en: 'Underlined terms may be non-measurable. Run analysis to see the INVEST model evaluation.',
  },
  'editor.clean_info': {
    id: 'Belum ada istilah tidak terukur yang terdeteksi saat mengetik. Jalankan analisis untuk audit lengkap.',
    en: 'No non-measurable terms detected while typing. Run analysis for a full audit.',
  },
  'editor.clauses': { id: 'klausul', en: 'clauses' },
  'editor.words': { id: 'kata', en: 'words' },
  'editor.auto_saved': { id: 'Tersimpan otomatis', en: 'Auto-saved' },
  'editor.btn_audit': { id: 'Audit User Story', en: 'Audit User Story' },
  'editor.btn_analyzing': { id: 'Menganalisis...', en: 'Analyzing...' },
  'editor.tip_title': { id: 'Kebutuhan yang baik dimulai dari tiga hal.', en: 'Good requirements start from three things.' },
  'editor.tip_desc': {
    id: 'Tentukan siapa penggunanya (Role), apa yang dibutuhkan (Action), dan mengapa itu penting (Benefit). Model AI kami membantu menyempurnakan sisanya.',
    en: 'Define who the user is (Role), what they need (Action), and why it matters (Benefit). Our AI model helps refine the rest.',
  },
  'editor.tip_learn': { id: 'Pelajari INVEST', en: 'Learn INVEST' },
  'editor.tip_close': { id: 'Tutup tips', en: 'Dismiss tips' },
  'editor.toast_accepted': {
    id: 'Draf diterima backend. Menjalankan model klasifikasi INVEST...',
    en: 'Draft accepted by backend. Running INVEST classification model...',
  },
  'editor.toast_pdf_success': {
    id: 'PDF berhasil diekstrak ({pages} hal, {chars} karakter).',
    en: 'PDF extracted successfully ({pages} pages, {chars} characters).',
  },
  'editor.toast_pdf_truncated': {
    id: 'PDF dipotong karena melebihi batas 100.000 karakter.',
    en: 'PDF was truncated because it exceeds the 100,000 character limit.',
  },

  // ─── Audit Detail Page ───
  'audit.crumb': { id: 'Workspace / Analisis Kebutuhan', en: 'Workspace / Requirements Analysis' },
  'audit.title': { id: 'Hasil Audit User Story', en: 'User Story Audit Results' },
  'audit.rerun': { id: 'Analisis Ulang', en: 'Re-analyze' },
  'audit.copy': { id: 'Salin', en: 'Copy' },
  'audit.export': { id: 'Ekspor', en: 'Export' },
  'audit.open_editor': { id: 'Buka di Editor', en: 'Open in Editor' },
  'audit.running_pipeline': { id: 'Menjalankan Pipeline Audit Kebutuhan', en: 'Running Requirements Audit Pipeline' },
  'audit.stage1_name': { id: 'Stage 1: Rule-based & Linting', en: 'Stage 1: Rule-based & Linting' },
  'audit.stage2_name': { id: 'Stage 2: INVEST Model (spaCy + ML)', en: 'Stage 2: INVEST Model (spaCy + ML)' },
  'audit.stage_done': { id: 'Selesai', en: 'Completed' },
  'audit.stage_processing': { id: 'Memproses...', en: 'Processing...' },
  'audit.not_found_title': { id: 'Audit tidak ditemukan', en: 'Audit not found' },
  'audit.not_found_desc': {
    id: 'Audit #{id} tidak ditemukan di server maupun di browser ini.',
    en: 'Audit #{id} was not found on the server or in this browser.',
  },
  'audit.back_editor': { id: 'Kembali ke editor', en: 'Back to editor' },
  'audit.findings_title': { id: 'Temuan Cacat', en: 'Defect Findings' },
  'audit.findings_view_editor': { id: 'Lihat dalam editor', en: 'View in editor' },
  'audit.no_defects': { id: 'Tidak ada cacat yang terdeteksi', en: 'No defects detected' },
  'audit.clean_pass': { id: 'Draf ini lolos seluruh aturan audit ReqLint.', en: 'This draft passed all ReqLint audit rules.' },
  'audit.col_location': { id: 'Lokasi', en: 'Location' },
  'audit.col_category': { id: 'Kategori', en: 'Category' },
  'audit.col_term': { id: 'Istilah Terdeteksi', en: 'Detected Term' },
  'audit.col_recommendation': { id: 'Rekomendasi', en: 'Recommendation' },
  'audit.sentence': { id: 'Kalimat', en: 'Sentence' },
  'audit.summary_title': { id: 'Ringkasan Hasil Analisis', en: 'Analysis Summary' },
  'audit.findings_count': { id: '{count} temuan', en: '{count} findings' },
  'audit.analysis_done': { id: 'Analisis selesai', en: 'Analysis complete' },
  'audit.standard_compliance': { id: 'Kepatuhan standar', en: 'Standard compliance' },
  'audit.details_invest': { id: 'Lihat detail INVEST', en: 'View INVEST details' },
  'audit.scorecard_title': { id: 'Quality Scorecard', en: 'Quality Scorecard' },
  'audit.score_desc': {
    id: 'Skor = 100 − bobot temuan (ambiguity 14, non-testable 16, tidak lengkap 18, weak directive 10, passive 12), diredam untuk teks panjang.',
    en: 'Score = 100 − finding weights (ambiguity 14, non-testable 16, incomplete 18, weak directive 10, passive 12), scaled for long text.',
  },
  'audit.revision_title': { id: 'Rekomendasi Perbaikan', en: 'Improvement Recommendation' },
  'audit.auto_badge': { id: '(Otomatis)', en: '(Automated)' },
  'audit.revision_eyebrow': { id: 'Saran revisi', en: 'Revision suggestion' },
  'audit.no_auto_revision': {
    id: 'Tidak ada perubahan otomatis yang aman untuk draf ini. Perbaiki temuan pada tabel di atas secara manual.',
    en: 'No automated changes are safe for this draft. Please fix findings in the table above manually.',
  },
  'audit.apply': { id: 'Terapkan Revisi', en: 'Apply' },
  'audit.edit_manual': { id: 'Edit Manual', en: 'Manual Edit' },
  'audit.acceptance_title': { id: 'Kriteria Penerimaan Terstandar', en: 'Standard Acceptance Criteria' },
  'audit.criteria_eyebrow': { id: 'Gherkin BDD (Given-When-Then)', en: 'Gherkin BDD (Given-When-Then)' },
  'audit.diff_title': { id: 'Perbandingan Sebelum & Sesudah', en: 'Before & After Comparison' },
  'audit.diff_before': { id: 'Sebelum (Draf Asli)', en: 'Before (Original Draft)' },
  'audit.diff_after': { id: 'Sesudah (Revisi)', en: 'After (Revision)' },
  'audit.original_badge': { id: 'Asli', en: 'Original' },
  'audit.revised_badge': { id: 'Rekomendasi', en: 'Recommendation' },
  'audit.toast_copied': { id: 'Hasil audit disalin (Markdown).', en: 'Audit results copied (Markdown).' },
  'audit.toast_apply_success': { id: 'Rekomendasi AI berhasil diterapkan ke draf!', en: 'AI recommendation successfully applied to draft!' },

  // ─── History Page ───
  'history.crumb': { id: 'Workspace / Riwayat', en: 'Workspace / History' },
  'history.title': { id: 'History Audit', en: 'Audit History' },
  'history.subtitle_count': { id: 'Menampilkan {visible} dari {total} audit di akun Anda.', en: 'Showing {visible} of {total} audits in your account.' },
  'history.subtitle_empty': { id: 'Seluruh riwayat evaluasi User Story yang pernah Anda jalankan.', en: 'All User Story evaluation history you have run.' },
  'history.search_placeholder': { id: 'Cari ID, judul, atau isi…', en: 'Search ID, title, or content…' },
  'history.delete_all': { id: 'Hapus semua', en: 'Delete all' },
  'history.date_all': { id: 'Semua tanggal', en: 'All dates' },
  'history.date_today': { id: 'Hari ini', en: 'Today' },
  'history.date_7d': { id: '7 hari terakhir', en: 'Last 7 days' },
  'history.date_30d': { id: '30 hari terakhir', en: 'Last 30 days' },
  'history.grade_all': { id: 'Semua grade', en: 'All grades' },
  'history.lang_all': { id: 'Semua bahasa', en: 'All languages' },
  'history.lang_id': { id: 'Indonesia', en: 'Indonesian' },
  'history.lang_en': { id: 'English', en: 'English' },
  'history.category_all': { id: 'Semua kategori temuan', en: 'All finding categories' },
  'history.sort_newest': { id: 'Terbaru', en: 'Newest' },
  'history.sort_oldest': { id: 'Terlama', en: 'Oldest' },
  'history.sort_score_desc': { id: 'Skor tertinggi', en: 'Highest score' },
  'history.sort_score_asc': { id: 'Skor terendah', en: 'Lowest score' },
  'history.reset': { id: 'Reset', en: 'Reset' },
  'history.empty_title': { id: 'Belum ada riwayat audit', en: 'No audit history yet' },
  'history.empty_desc': { id: 'Jalankan analisis dari editor, hasilnya akan tersimpan di sini.', en: 'Run analysis from the editor, results will be saved here.' },
  'history.open_editor': { id: 'Buka editor', en: 'Open editor' },
  'history.no_match': { id: 'Tidak ada audit yang cocok dengan pencarian atau filter ini.', en: 'No audits match this search or filter.' },
  'history.reset_filter': { id: 'Reset filter', en: 'Reset filter' },
  'history.findings': { id: 'temuan', en: 'findings' },
  'history.open': { id: 'Buka', en: 'Open' },
  'history.confirm_delete_all': { id: 'Hapus seluruh riwayat audit di browser ini? Tindakan ini tidak dapat dibatalkan.', en: 'Delete all audit history in this browser? This action cannot be undone.' },
  'history.deleted': { id: '{id} dihapus dari riwayat.', en: '{id} deleted from history.' },
  'history.all_deleted': { id: 'Seluruh riwayat dihapus.', en: 'All history deleted.' },

  // ─── Contact Page ───
  'contact.crumb': { id: 'Workspace / Kontak', en: 'Workspace / Contact' },
  'contact.title': { id: 'Hubungi Kami', en: 'Contact Us' },
  'contact.subtitle': { id: 'Punya pertanyaan, saran, atau melaporkan bug? Jangan ragu menghubungi tim ReqLint.', en: 'Have questions, suggestions, or bug reports? Feel free to contact the ReqLint team.' },
  'contact.form_title': { id: 'Kirim Pesan', en: 'Send a Message' },
  'contact.name': { id: 'Nama', en: 'Name' },
  'contact.name_placeholder': { id: 'Nama lengkap Anda', en: 'Your full name' },
  'contact.email': { id: 'Email', en: 'Email' },
  'contact.email_placeholder': { id: 'email@contoh.com', en: 'email@example.com' },
  'contact.subject': { id: 'Subjek', en: 'Subject' },
  'contact.subject_placeholder': { id: 'Topik pesan Anda', en: 'Topic of your message' },
  'contact.message': { id: 'Pesan', en: 'Message' },
  'contact.message_placeholder': { id: 'Jelaskan pertanyaan atau masukan Anda...', en: 'Describe your question or feedback...' },
  'contact.submit': { id: 'Kirim Pesan', en: 'Send Message' },
  'contact.sending': { id: 'Mengirim...', en: 'Sending...' },
  'contact.success': { id: 'Pesan berhasil dikirim! Kami akan segera membalas.', en: 'Message sent successfully! We will reply shortly.' },
  'contact.info_title': { id: 'Informasi Kontak', en: 'Contact Information' },
  'contact.info_email': { id: 'Email', en: 'Email' },
  'contact.info_github': { id: 'GitHub', en: 'GitHub' },
  'contact.info_team': { id: 'Tim Pengembang', en: 'Development Team' },
  'contact.info_team_desc': { id: 'PPL Praktikum I4 Kelompok 3', en: 'PPL Praktikum I4 Group 3' },
  'contact.info_univ': { id: 'Universitas', en: 'University' },

  // ─── Help Page ───
  'help.crumb': { id: 'Workspace / Panduan', en: 'Workspace / Help' },
  'help.title': { id: 'Panduan Pengguna', en: 'User Guide' },
  'help.subtitle': { id: 'Pelajari cara menggunakan ReqLint untuk audit kualitas User Story Anda.', en: 'Learn how to use ReqLint to audit the quality of your User Stories.' },
  'help.getting_started': { id: 'Memulai', en: 'Getting Started' },
  'help.step1_title': { id: '1. Daftar & Masuk', en: '1. Register & Sign In' },
  'help.step1_desc': { id: 'Buat akun baru di halaman Daftar, lalu masuk dengan kredensial Anda. Anda juga bisa menggunakan akun demo untuk mencoba langsung.', en: 'Create a new account on the Register page, then sign in with your credentials. You can also use a demo account to try it out right away.' },
  'help.step2_title': { id: '2. Input User Story', en: '2. Input User Story' },
  'help.step2_desc': { id: 'Di halaman Editor, ketikkan atau tempelkan teks User Story Anda. Pilih bahasa analisis (Indonesia/English). Anda juga bisa mengunggah dokumen PDF.', en: 'On the Editor page, type or paste your User Story text. Choose the analysis language (Indonesian/English). You can also upload a PDF document.' },
  'help.step3_title': { id: '3. Jalankan Analisis', en: '3. Run Analysis' },
  'help.step3_desc': { id: 'Klik tombol "Jalankan Analisis" untuk memulai proses audit. Mesin NLP akan menganalisis teks Anda berdasarkan standar ISO 29148 dan kerangka INVEST.', en: 'Click the "Run Analysis" button to start the audit. The NLP engine will analyze your text based on ISO 29148 standard and INVEST framework.' },
  'help.step4_title': { id: '4. Lihat Hasil', en: '4. View Results' },
  'help.step4_desc': { id: 'Halaman hasil menampilkan scorecard kualitas, daftar temuan cacat, serta rekomendasi perbaikan dari AI.', en: 'The results page displays a quality scorecard, defect findings list, and AI-powered improvement recommendations.' },
  'help.step5_title': { id: '5. Ekspor & Kelola', en: '5. Export & Manage' },
  'help.step5_desc': { id: 'Ekspor hasil audit ke format PDF, Markdown, atau JSON. Lihat seluruh riwayat audit di halaman History.', en: 'Export audit results to PDF, Markdown, or JSON format. View all audit history on the History page.' },
  'help.scores_title': { id: 'Memahami Skor & Grade', en: 'Understanding Scores & Grades' },
  'help.scores_desc': { id: 'Skor dimulai dari 100 dan dikurangi berdasarkan temuan cacat. Setiap kategori memiliki bobot berbeda.', en: 'Score starts at 100 and is reduced based on defect findings. Each category has a different weight.' },
  'help.grade_a': { id: 'Excellent — User Story berkualitas tinggi', en: 'Excellent — High quality User Story' },
  'help.grade_b': { id: 'Good — Kualitas baik, sedikit perbaikan', en: 'Good — Good quality, minor improvements' },
  'help.grade_c': { id: 'Acceptable — Perlu beberapa perbaikan', en: 'Acceptable — Some improvements needed' },
  'help.grade_d': { id: 'Needs Improvement — Banyak masalah ditemukan', en: 'Needs Improvement — Many issues found' },
  'help.grade_e': { id: 'Poor — Perlu ditulis ulang', en: 'Poor — Needs to be rewritten' },
  'help.categories_title': { id: 'Kategori Temuan', en: 'Finding Categories' },
  'help.cat_ambiguity': { id: 'Ambiguity — Istilah atau kalimat yang ambigu/tidak jelas', en: 'Ambiguity — Ambiguous or unclear terms or sentences' },
  'help.cat_incomplete': { id: 'Tidak Lengkap — Elemen yang hilang (role, action, benefit)', en: 'Incomplete — Missing elements (role, action, benefit)' },
  'help.cat_weak': { id: 'Weak Directive — Kata kerja yang lemah atau tidak tegas', en: 'Weak Directive — Weak or non-assertive verbs' },
  'help.cat_passive': { id: 'Passive Voice — Penggunaan kalimat pasif', en: 'Passive Voice — Use of passive voice' },
  'help.tips_title': { id: 'Tips Menulis User Story', en: 'Tips for Writing User Stories' },
  'help.tip1': { id: 'Gunakan format standar: "Sebagai [peran], saya ingin [aksi], sehingga [manfaat]"', en: 'Use the standard format: "As a [role], I want [action], so that [benefit]"' },
  'help.tip2': { id: 'Hindari istilah ambigu seperti "cepat", "mudah", "baik", "sesuai"', en: 'Avoid ambiguous terms like "fast", "easy", "good", "appropriate"' },
  'help.tip3': { id: 'Gunakan kata kerja aktif dan spesifik', en: 'Use active and specific verbs' },
  'help.tip4': { id: 'Pastikan setiap story independen dan dapat di-estimasi', en: 'Ensure each story is independent and estimable' },
  'help.tip5': { id: 'Sertakan kriteria penerimaan (acceptance criteria) yang terukur', en: 'Include measurable acceptance criteria' },

  // ─── Forgot / Reset Password ───
  'forgot.title': { id: 'Lupa Kata Sandi', en: 'Forgot Password' },
  'forgot.subtitle': { id: 'Masukkan email Anda untuk menerima tautan reset kata sandi.', en: 'Enter your email to receive a password reset link.' },
  'forgot.email': { id: 'Email', en: 'Email' },
  'forgot.email_placeholder': { id: 'Masukkan email terdaftar', en: 'Enter your registered email' },
  'forgot.submit': { id: 'Kirim Tautan Reset', en: 'Send Reset Link' },
  'forgot.sending': { id: 'Mengirim...', en: 'Sending...' },
  'forgot.success': { id: 'Jika email terdaftar, tautan reset telah dikirim. Silakan cek email Anda.', en: 'If the email is registered, a reset link has been sent. Please check your email.' },
  'forgot.back_login': { id: 'Kembali ke halaman masuk', en: 'Back to sign in page' },
  'reset.title': { id: 'Reset Kata Sandi', en: 'Reset Password' },
  'reset.subtitle': { id: 'Masukkan kata sandi baru untuk akun Anda.', en: 'Enter a new password for your account.' },
  'reset.password': { id: 'Kata Sandi Baru', en: 'New Password' },
  'reset.password_placeholder': { id: 'Minimal 8 karakter (huruf dan angka)', en: 'Minimum 8 characters (letters and numbers)' },
  'reset.confirm': { id: 'Konfirmasi Kata Sandi', en: 'Confirm Password' },
  'reset.confirm_placeholder': { id: 'Ulangi kata sandi baru', en: 'Repeat new password' },
  'reset.submit': { id: 'Reset Kata Sandi', en: 'Reset Password' },
  'reset.processing': { id: 'Memproses...', en: 'Processing...' },
  'reset.success': { id: 'Kata sandi berhasil diperbarui. Silakan masuk.', en: 'Password updated successfully. Please sign in.' },
  'reset.invalid_token': { id: 'Token reset tidak valid atau sudah kedaluwarsa.', en: 'Reset token is invalid or expired.' },

  // ─── General & Categories ───
  'general.language': { id: 'Bahasa', en: 'Language' },
  'general.indonesian': { id: 'Bahasa Indonesia', en: 'Indonesian' },
  'general.english': { id: 'English', en: 'English' },
  'category.ambiguity': { id: 'Ambiguity', en: 'Ambiguity' },
  'category.non_testable': { id: 'Tidak Bisa Diuji', en: 'Non-Testable' },
  'category.incomplete': { id: 'Tidak Lengkap', en: 'Incomplete' },
  'category.weak_directive': { id: 'Weak Directive', en: 'Weak Directive' },
  'category.passive_voice': { id: 'Passive Voice', en: 'Passive Voice' },
};

/**
 * Mengambil terjemahan berdasarkan key dan locale aktif.
 * Mendukung placeholder {key} yang bisa di-replace via params.
 */
export function t(key: string, params?: Record<string, string | number>): string {
  const locale = localeStore.get();
  let text = translations[key]?.[locale] ?? translations[key]?.['id'] ?? key;
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      text = text.replace(`{${k}}`, String(v));
    });
  }
  return text;
}

/** Hook version — reactive terhadap perubahan locale */
export function useT() {
  const locale = useUILocale();
  return (key: string, params?: Record<string, string | number>): string => {
    let text = translations[key]?.[locale] ?? translations[key]?.['id'] ?? key;
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        text = text.replace(`{${k}}`, String(v));
      });
    }
    return text;
  };
}
