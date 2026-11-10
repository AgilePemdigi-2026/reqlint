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
   Kamus terjemahan UI
   ──────────────────────────────────────────── */

const translations: Record<string, Record<UILocale, string>> = {
  // ─── Navbar & Shell ───
  'nav.editor': { id: 'Editor', en: 'Editor' },
  'nav.history': { id: 'History Audit', en: 'Audit History' },
  'nav.workspace': { id: 'Personal workspace', en: 'Personal workspace' },
  'nav.notifications': { id: 'Notifikasi', en: 'Notifications' },
  'nav.notif_welcome': { id: 'Selamat datang di ReqLint. Belum ada notifikasi lain.', en: 'Welcome to ReqLint. No other notifications.' },
  'nav.account_menu': { id: 'Menu akun', en: 'Account menu' },
  'nav.theme_light': { id: 'Tema terang', en: 'Light theme' },
  'nav.theme_dark': { id: 'Tema gelap', en: 'Dark theme' },
  'nav.logout': { id: 'Keluar', en: 'Sign out' },
  'nav.footer_jwt': { id: 'Sesi autentikasi diamankan dengan token JWT FastAPI.', en: 'Authentication session secured with FastAPI JWT token.' },

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

  // ─── General ───
  'general.language': { id: 'Bahasa', en: 'Language' },
  'general.indonesian': { id: 'Bahasa Indonesia', en: 'Indonesian' },
  'general.english': { id: 'English', en: 'English' },
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

