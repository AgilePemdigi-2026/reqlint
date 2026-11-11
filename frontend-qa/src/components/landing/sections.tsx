import {
  ArrowRight,
  Columns2,
  Gauge,
  ListChecks,
  Lock,
  PenLine,
  ScanSearch,
  Wand2,
  type LucideIcon,
} from 'lucide-react';
import Link from 'next/link';
import { CATEGORY_LABEL, CATEGORY_STYLE } from '@/lib/format';
import type { Category } from '@/lib/analyzer';

function SectionHead({ eyebrow, title, subtitle }: { eyebrow: string; title: string; subtitle?: string }) {
  return (
    <div className="mx-auto max-w-[680px] text-center">
      <p className="eyebrow">{eyebrow}</p>
      <h2 className="mt-3 text-[32px] font-semibold leading-tight tracking-tight sm:text-[40px]">{title}</h2>
      {subtitle && <p className="mt-4 text-[16.5px] leading-relaxed text-muted">{subtitle}</p>}
    </div>
  );
}

// ───────────── Fitur ─────────────
const FEATURES: Array<{ icon: LucideIcon; title: string; text: string }> = [
  {
    icon: PenLine,
    title: 'Editor real-time',
    text: 'Istilah yang tidak terukur digarisbawahi saat Anda mengetik, lengkap dengan nomor baris dan hitungan klausul.',
  },
  {
    icon: Gauge,
    title: 'Quality Scorecard',
    text: 'Skor 0–100 plus kepatuhan terhadap ISO 29148 dan INVEST, dengan rincian I-N-V-E-S-T.',
  },
  {
    icon: ScanSearch,
    title: 'Temuan cacat yang jelas',
    text: 'Setiap temuan menunjuk kalimat, istilah, kategori, dan rekomendasi perbaikan yang spesifik.',
  },
  {
    icon: Wand2,
    title: 'Saran revisi otomatis',
    text: 'Ubah istilah tidak terukur dan kalimat pasif menjadi versi yang lebih tegas. Anda yang memutuskan menerapkannya.',
  },
  {
    icon: ListChecks,
    title: 'Acceptance Criteria (BDD)',
    text: 'Draf skenario Given/When/Then dibuat langsung dari user story Anda sebagai titik awal.',
  },
  {
    icon: Columns2,
    title: 'Diff Before / After',
    text: 'Bandingkan draf asli dan revisi per kata, lihat kenaikan skornya, lalu simpan di riwayat atau ekspor.',
  },
];

export function Features() {
  return (
    <section id="fitur" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <SectionHead
        eyebrow="Fitur"
        title="Semua yang dibutuhkan untuk menulis kebutuhan yang jelas"
        subtitle="Dari mengetik draf sampai menyerahkannya ke tim pengembang."
      />
      <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, text }) => (
          <article key={title} className="card rounded-[22px] p-6">
            <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-line/[0.07] bg-card">
              <Icon size={19} strokeWidth={1.6} aria-hidden />
            </span>
            <h3 className="mt-5 text-[17px] font-semibold">{title}</h3>
            <p className="mt-2 text-[14.5px] leading-relaxed text-muted">{text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

// ───────────── Cara kerja ─────────────
const STEPS = [
  { n: '01', title: 'Tempel atau unggah', text: 'Tulis user story, tempel dari alat lain, atau unggah PDF/TXT. Pilih bahasa Indonesia atau English.' },
  { n: '02', title: 'Jalankan analisis', text: 'ReqLint memeriksa tiap klausul terhadap aturan ambiguitas, testabilitas, kelengkapan, direktif, dan kalimat aktif.' },
  { n: '03', title: 'Perbaiki dan ekspor', text: 'Terapkan saran revisi atau edit manual, lihat skor naik di diff, lalu ekspor ke Markdown, CSV, atau JSON.' },
];

export function HowItWorks() {
  return (
    <section id="cara-kerja" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <SectionHead eyebrow="Cara kerja" title="Tiga langkah dari draf ke kebutuhan yang siap diuji" />
      <ol className="mt-12 grid gap-5 md:grid-cols-3">
        {STEPS.map((s) => (
          <li key={s.n} className="card rounded-[22px] p-7">
            <span className="font-mono text-[13px] font-medium text-accent">{s.n}</span>
            <h3 className="mt-4 text-[19px] font-semibold">{s.title}</h3>
            <p className="mt-2 text-[14.5px] leading-relaxed text-muted">{s.text}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

// ───────────── Standar ─────────────
const ISO_CRITERIA = [
  ['Tidak ambigu', 'Tidak memuat kata relatif seperti "cepat", "banyak", atau "yang sesuai".'],
  ['Dapat diverifikasi', 'Tidak memakai kata subjektif seperti "user-friendly" atau "menarik".'],
  ['Lengkap', 'Punya peran, tujuan, dan manfaat; tidak berakhir dengan "dll" atau "TBD".'],
  ['Direktif tegas', 'Memakai "harus"/"wajib", bukan "sebaiknya" atau "mungkin".'],
  ['Kalimat aktif', 'Jelas siapa melakukan apa, bukan "harus disimpan".'],
];

const INVEST = [
  ['I', 'Independent', 'Tidak bergantung pada item lain'],
  ['N', 'Negotiable', 'Tidak mengunci solusi teknis'],
  ['V', 'Valuable', 'Manfaatnya dinyatakan'],
  ['E', 'Estimable', 'Cukup jelas untuk diestimasi'],
  ['S', 'Small', 'Cukup kecil untuk satu iterasi'],
  ['T', 'Testable', 'Dapat diuji dengan kriteria jelas'],
];

const FINDING_EXAMPLES: Array<[Category, string]> = [
  ['ambiguity', 'sangat cepat'],
  ['non-testable', 'user-friendly'],
  ['incomplete', 'tanpa "agar …"'],
  ['weak-directive', 'sebaiknya'],
  ['passive-voice', 'harus disimpan'],
];

export function Standards() {
  return (
    <section id="standar" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <SectionHead
        eyebrow="Standar"
        title="Dibangun di atas ISO 29148 dan INVEST"
        subtitle="Dua acuan yang umum dipakai untuk menilai kualitas kebutuhan dan user story."
      />

      <div className="mt-12 grid gap-5 lg:grid-cols-2">
        <div className="card rounded-[22px] p-7">
          <h3 className="text-[18px] font-semibold">ISO/IEC/IEEE 29148</h3>
          <p className="mt-1 text-[14px] text-muted">Lima kriteria yang kami periksa pada setiap klausul:</p>
          <ul className="mt-5 divide-y divide-line/[0.07]">
            {ISO_CRITERIA.map(([t, d]) => (
              <li key={t} className="py-3">
                <p className="text-[14.5px] font-medium">{t}</p>
                <p className="text-[13.5px] text-muted">{d}</p>
              </li>
            ))}
          </ul>
        </div>

        <div className="card rounded-[22px] p-7">
          <h3 className="text-[18px] font-semibold">INVEST</h3>
          <p className="mt-1 text-[14px] text-muted">Enam sifat user story yang baik:</p>
          <ul className="mt-5 grid gap-3 sm:grid-cols-2">
            {INVEST.map(([k, t, d]) => (
              <li key={k} className="flex gap-3 rounded-2xl bg-line/[0.04] p-4">
                <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-card text-[15px] font-bold shadow-soft">
                  {k}
                </span>
                <span>
                  <span className="block text-[14px] font-semibold">{t}</span>
                  <span className="block text-[12.5px] leading-snug text-muted">{d}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card mt-5 rounded-[22px] p-7">
        <h3 className="text-[18px] font-semibold">Lima kategori temuan</h3>
        <ul className="mt-4 flex flex-wrap gap-x-8 gap-y-4">
          {FINDING_EXAMPLES.map(([cat, ex]) => (
            <li key={cat} className="flex items-center gap-2.5">
              <span className={`pill ${CATEGORY_STYLE[cat]}`}>{CATEGORY_LABEL[cat]}</span>
              <code className="rounded-md bg-line/[0.06] px-2 py-1 font-mono text-[12px]">{ex}</code>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

// ───────────── Privasi ─────────────
export function Privacy() {
  return (
    <section id="privasi" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <div className="card flex flex-col items-start gap-8 rounded-[28px] p-8 sm:p-12 md:flex-row md:items-center">
        <span className="inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-line/[0.07] bg-card">
          <Lock size={24} strokeWidth={1.5} aria-hidden />
        </span>
        <div className="flex-1">
          <h2 className="text-[26px] font-semibold tracking-tight">Transparansi data: apa yang terjadi dengan draf Anda</h2>
          <p className="mt-2 max-w-[640px] text-[15.5px] leading-relaxed text-muted">
            Ada dua mode analisis. <strong>Demo di halaman ini</strong> berjalan sepenuhnya di browser — teks demo tidak
            dikirim ke server. <strong>Saat Anda memakai aplikasi (editor &amp; audit)</strong>, teks dan berkas PDF
            diunggah ke server ReqLint untuk dianalisis dan disimpan pada riwayat akun Anda. Bila tahap rekomendasi AI
            aktif, teks juga dikirim ke penyedia model bahasa eksternal (mis. Groq) untuk diproses.
          </p>
          <p className="mt-2 max-w-[640px] text-[15.5px] leading-relaxed text-muted">
            Hasil analisis aturan tetap deterministik: teks yang sama selalu menghasilkan skor yang sama.
          </p>
        </div>
      </div>
    </section>
  );
}

// ───────────── FAQ ─────────────
const FAQ = [
  [
    'Apakah ReqLint memakai AI?',
    'Demo di halaman ini tidak. Aplikasi lengkap memakai dua lapis: analisis aturan deterministik (kamus & regex) di backend, dan — bila dikonfigurasi — model bahasa eksternal (mis. Groq) untuk saran revisi dan acceptance criteria. Tanpa provider AI yang aktif, saran revisi berupa contoh generik bawaan, bukan hasil model AI.',
  ],
  [
    'Apakah teks saya dikirim ke server?',
    'Di demo halaman ini tidak — analisis berjalan di browser. Di aplikasi (editor & audit), teks dan berkas PDF diunggah ke server ReqLint untuk dianalisis dan disimpan pada riwayat akun Anda. Bila rekomendasi AI aktif, teks juga diteruskan ke penyedia model bahasa eksternal yang dikonfigurasi (mis. Groq).',
  ],
  [
    'Bahasa apa yang didukung?',
    'Bahasa Indonesia dan English. Pilih bahasa analisis di editor.',
  ],
  [
    'Format berkas apa yang bisa diunggah?',
    'PDF, TXT, dan Markdown (maks. 8 MB). PDF berbasis gambar hasil pindai belum dapat dibaca karena tidak memuat teks.',
  ],
  [
    'Bagaimana skor dihitung?',
    'Skor dimulai dari 100 lalu dikurangi bobot tiap temuan (ambiguity 14, non-testable 16, tidak lengkap 18, weak directive 10, pasif 12), diredam untuk teks yang panjang.',
  ],
  [
    'Bisakah hasilnya diekspor?',
    'Bisa. Ekspor ke Markdown, CSV, atau JSON dari halaman hasil audit, atau salin ringkasannya.',
  ],
];

export function Faq() {
  return (
    <section id="faq" className="mx-auto max-w-[820px] scroll-mt-24 px-5 py-20">
      <SectionHead eyebrow="FAQ" title="Pertanyaan yang sering diajukan" />
      <div className="mt-10 space-y-3">
        {FAQ.map(([q, a]) => (
          <details key={q} className="group card rounded-2xl px-6 py-4 open:pb-5">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-[16px] font-medium [&::-webkit-details-marker]:hidden">
              {q}
              <span
                className="text-[22px] font-light leading-none text-muted transition group-open:rotate-45"
                aria-hidden
              >
                +
              </span>
            </summary>
            <p className="mt-3 text-[14.5px] leading-relaxed text-muted">{a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}

// ───────────── CTA penutup ─────────────
export function FinalCta() {
  return (
    <section className="mx-auto max-w-[1200px] px-5 pb-24 pt-8">
      <div className="rounded-[32px] bg-btn px-8 py-14 text-center text-btnink sm:px-16">
        <h2 className="mx-auto max-w-[620px] text-[30px] font-semibold leading-tight tracking-tight sm:text-[38px]">
          Tulis kebutuhan yang bisa diukur, bukan ditebak.
        </h2>
        <p className="mx-auto mt-4 max-w-[520px] text-[16px] opacity-70">
          Coba audit pertama Anda sekarang — gratis, tanpa instalasi.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/register"
            className="inline-flex h-12 items-center gap-2 rounded-full bg-btnink px-7 text-[15px] font-semibold text-btn transition hover:opacity-90"
          >
            Daftar gratis <ArrowRight size={16} aria-hidden />
          </Link>
          <Link
            href="/login"
            className="inline-flex h-12 items-center rounded-full border border-btnink/25 px-7 text-[15px] font-medium transition hover:bg-btnink/10"
          >
            Masuk
          </Link>
        </div>
      </div>
    </section>
  );
}
