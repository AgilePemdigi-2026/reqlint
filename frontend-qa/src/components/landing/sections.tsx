'use client';

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
import { CATEGORY_LABEL } from '@/lib/format';
import type { Category } from '@/lib/analyzer';
import { useUILocale, type UILocale } from '@/lib/i18n';

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
const FEATURES: Array<{
  icon: LucideIcon;
  title: Record<UILocale, string>;
  text: Record<UILocale, string>;
}> = [
  {
    icon: PenLine,
    title: { id: 'Editor real-time', en: 'Real-time Editor' },
    text: {
      id: 'Istilah yang tidak terukur digarisbawahi saat Anda mengetik, lengkap dengan nomor baris dan hitungan klausul.',
      en: 'Non-measurable terms are underlined as you type, complete with line numbers and clause counting.',
    },
  },
  {
    icon: Gauge,
    title: { id: 'Quality Scorecard', en: 'Quality Scorecard' },
    text: {
      id: 'Skor 0–100 plus kepatuhan terhadap ISO 29148 dan INVEST, dengan rincian I-N-V-E-S-T.',
      en: '0–100 quality score plus compliance to ISO 29148 and INVEST criteria, with I-N-V-E-S-T breakdown.',
    },
  },
  {
    icon: ScanSearch,
    title: { id: 'Temuan cacat yang jelas', en: 'Precise Defect Findings' },
    text: {
      id: 'Setiap temuan menunjuk kalimat, istilah, kategori, dan rekomendasi perbaikan yang spesifik.',
      en: 'Each finding pinpoint sentence, term, category, and specific actionable improvement recommendations.',
    },
  },
  {
    icon: Wand2,
    title: { id: 'Saran revisi otomatis', en: 'Automated Revision' },
    text: {
      id: 'Ubah istilah tidak terukur dan kalimat pasif menjadi versi yang lebih tegas. Anda yang memutuskan menerapkannya.',
      en: 'Transform ambiguous terms and passive voice into active, definitive requirements with 1-click apply.',
    },
  },
  {
    icon: ListChecks,
    title: { id: 'Acceptance Criteria (BDD)', en: 'Acceptance Criteria (BDD)' },
    text: {
      id: 'Draf skenario Given/When/Then dibuat langsung dari user story Anda sebagai titik awal pengujian.',
      en: 'Given/When/Then scenario drafts are generated directly from your user story as a testing baseline.',
    },
  },
  {
    icon: Columns2,
    title: { id: 'Diff Before / After', en: 'Before & After Diff' },
    text: {
      id: 'Bandingkan draf asli dan revisi per kata, lihat kenaikan skornya, lalu simpan di riwayat atau ekspor.',
      en: 'Compare original and revised drafts word-by-word, inspect score improvements, and export reports.',
    },
  },
];

export function Features() {
  const locale = useUILocale();

  return (
    <section id="fitur" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <SectionHead
        eyebrow={locale === 'id' ? 'Fitur' : 'Features'}
        title={
          locale === 'id'
            ? 'Semua yang dibutuhkan untuk menulis kebutuhan yang jelas'
            : 'Everything you need to write clear, measurable requirements'
        }
        subtitle={
          locale === 'id'
            ? 'Dari mengetik draf sampai menyerahkannya ke tim pengembang.'
            : 'From typing drafts to handing them over to development teams.'
        }
      />
      <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, text }) => (
          <article key={title.id} className="card rounded-[22px] p-6">
            <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-line/[0.07] bg-card">
              <Icon size={19} strokeWidth={1.6} aria-hidden />
            </span>
            <h3 className="mt-5 text-[17px] font-semibold">{title[locale]}</h3>
            <p className="mt-2 text-[14.5px] leading-relaxed text-muted">{text[locale]}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

// ───────────── Cara kerja ─────────────
const STEPS = [
  {
    n: '01',
    title: { id: 'Tempel atau unggah', en: 'Paste or Upload' },
    text: {
      id: 'Tulis user story, tempel dari alat lain, atau unggah PDF/TXT. Pilih bahasa Indonesia atau English.',
      en: 'Type user story, paste from Jira/Notion, or upload PDF/TXT. Choose Indonesian or English.',
    },
  },
  {
    n: '02',
    title: { id: 'Jalankan analisis', en: 'Run Analysis' },
    text: {
      id: 'ReqLint memeriksa tiap klausul terhadap aturan ambiguitas, testabilitas, kelengkapan, direktif, dan kalimat aktif.',
      en: 'ReqLint checks clauses against ambiguity, testability, completeness, directives, and active voice.',
    },
  },
  {
    n: '03',
    title: { id: 'Perbaiki dan ekspor', en: 'Improve & Export' },
    text: {
      id: 'Terapkan saran revisi atau edit manual, lihat skor naik di diff, lalu ekspor ke Markdown, CSV, atau JSON.',
      en: 'Apply revision suggestions or edit manually, view score increase in diff, then export to Markdown, CSV, or JSON.',
    },
  },
];

export function HowItWorks() {
  const locale = useUILocale();

  return (
    <section id="cara-kerja" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <SectionHead
        eyebrow={locale === 'id' ? 'Cara kerja' : 'How It Works'}
        title={
          locale === 'id'
            ? 'Tiga langkah dari draf ke kebutuhan yang siap diuji'
            : 'Three steps from draft to test-ready requirements'
        }
      />
      <ol className="mt-12 grid gap-5 md:grid-cols-3">
        {STEPS.map((s) => (
          <li key={s.n} className="card rounded-[22px] p-7">
            <span className="font-mono text-[13px] font-medium text-accent">{s.n}</span>
            <h3 className="mt-4 text-[19px] font-semibold">{s.title[locale]}</h3>
            <p className="mt-2 text-[14.5px] leading-relaxed text-muted">{s.text[locale]}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

// ───────────── Standar ─────────────
const ISO_CRITERIA: Array<[Record<UILocale, string>, Record<UILocale, string>]> = [
  [
    { id: 'Tidak ambigu', en: 'Unambiguous' },
    {
      id: 'Tidak memuat kata relatif seperti "cepat", "banyak", atau "yang sesuai".',
      en: 'Free of vague relative terms like "fast", "many", or "as appropriate".',
    },
  ],
  [
    { id: 'Dapat diverifikasi', en: 'Verifiable' },
    {
      id: 'Tidak memakai kata subjektif seperti "user-friendly" atau "menarik".',
      en: 'Free of subjective terms like "user-friendly" or "attractive".',
    },
  ],
  [
    { id: 'Lengkap', en: 'Complete' },
    {
      id: 'Punya peran, tujuan, dan manfaat; tidak berakhir dengan "dll" atau "TBD".',
      en: 'Has role, action, and benefit; does not end with "etc." or "TBD".',
    },
  ],
  [
    { id: 'Direktif tegas', en: 'Strong Directives' },
    {
      id: 'Memakai "harus"/"wajib", bukan "sebaiknya" atau "mungkin".',
      en: 'Uses assertive verbs like "must" / "shall", not "should" or "might".',
    },
  ],
  [
    { id: 'Kalimat aktif', en: 'Active Voice' },
    {
      id: 'Jelas siapa melakukan apa, bukan "harus disimpan".',
      en: 'Clear subject doing the action, not passive constructions.',
    },
  ],
];

const INVEST = [
  ['I', 'Independent', { id: 'Tidak bergantung pada item lain', en: 'Not dependent on other items' }],
  ['N', 'Negotiable', { id: 'Tidak mengunci solusi teknis', en: 'Leaves room for discussion' }],
  ['V', 'Valuable', { id: 'Manfaatnya dinyatakan secara gamblang', en: 'Delivers clear user value' }],
  ['E', 'Estimable', { id: 'Cukup jelas untuk diestimasi ukurannya', en: 'Clear enough to estimate' }],
  ['S', 'Small', { id: 'Cukup kecil untuk satu iterasi sprint', en: 'Small enough for a sprint' }],
  ['T', 'Testable', { id: 'Dapat diuji dengan kriteria penerimaan yang jelas', en: 'Can be verified with tests' }],
] as const;

export function Standards() {
  const locale = useUILocale();

  return (
    <section id="standar" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <SectionHead
        eyebrow={locale === 'id' ? 'Standar' : 'Standards'}
        title={
          locale === 'id'
            ? 'Dibangun di atas ISO 29148 dan INVEST'
            : 'Built on ISO 29148 and INVEST'
        }
        subtitle={
          locale === 'id'
            ? 'Dua acuan yang umum dipakai untuk menilai kualitas kebutuhan dan user story.'
            : 'Two industry benchmarks for assessing requirement and user story quality.'
        }
      />

      <div className="mt-12 grid gap-5 lg:grid-cols-2">
        <div className="card rounded-[22px] p-7">
          <h3 className="text-[18px] font-semibold">ISO/IEC/IEEE 29148</h3>
          <p className="mt-1 text-[14px] text-muted">
            {locale === 'id'
              ? 'Lima kriteria yang kami periksa pada setiap klausul:'
              : 'Five core criteria audited on every requirement clause:'}
          </p>
          <ul className="mt-5 divide-y divide-line/[0.07]">
            {ISO_CRITERIA.map(([t, d]) => (
              <li key={t.id} className="py-3">
                <p className="text-[14.5px] font-medium">{t[locale]}</p>
                <p className="text-[13.5px] text-muted">{d[locale]}</p>
              </li>
            ))}
          </ul>
        </div>

        <div className="card rounded-[22px] p-7">
          <h3 className="text-[18px] font-semibold">INVEST</h3>
          <p className="mt-1 text-[14px] text-muted">
            {locale === 'id' ? 'Enam sifat user story yang baik:' : 'Six characteristics of quality user stories:'}
          </p>
          <ul className="mt-5 grid gap-3 sm:grid-cols-2">
            {INVEST.map(([k, t, d]) => (
              <li key={k} className="rounded-xl border border-line/[0.06] bg-card/70 p-3.5">
                <span className="font-mono text-[13px] font-bold text-accent">{k}</span>
                <p className="mt-1 text-[14px] font-semibold">{t}</p>
                <p className="mt-0.5 text-[12px] text-muted">{d[locale]}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

// ───────────── Privasi ─────────────
export function Privacy() {
  const locale = useUILocale();

  return (
    <section id="privasi" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <div className="card flex flex-col items-start gap-8 rounded-[28px] p-8 sm:p-12 md:flex-row md:items-center">
        <span className="inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-line/[0.07] bg-card">
          <Lock size={24} strokeWidth={1.5} aria-hidden />
        </span>
        <div className="flex-1">
          <h2 className="text-[26px] font-semibold tracking-tight">
            {locale === 'id' ? 'Draf Anda aman dan terisolasi' : 'Your drafts remain secure and private'}
          </h2>
          <p className="mt-2 max-w-[640px] text-[15.5px] leading-relaxed text-muted">
            {locale === 'id'
              ? 'Mesin analisis berjalan secara aman. Sesi autentikasi diamankan dengan token JWT FastAPI, dan riwayat audit diisolasi khusus untuk akun Anda dengan opsi ekspor fleksibel.'
              : 'The analysis engine runs securely. Authentication sessions are protected by FastAPI JWT tokens, and your audit history is isolated to your account with flexible export options.'}
          </p>
        </div>
      </div>
    </section>
  );
}

// ───────────── FAQ ─────────────
const FAQ_DATA: Array<{ q: Record<UILocale, string>; a: Record<UILocale, string> }> = [
  {
    q: { id: 'Apakah ReqLint memakai AI?', en: 'Does ReqLint use AI?' },
    a: {
      id: 'ReqLint menggabungkan rule-based linting deterministik (Tahap 1) dengan model klasifikasi NLP machine learning & spaCy (Tahap 2) untuk akurasi optimal.',
      en: 'ReqLint combines deterministic rule-based linting (Stage 1) with spaCy & machine learning NLP classification models (Stage 2) for optimal accuracy.',
    },
  },
  {
    q: { id: 'Apakah teks saya aman?', en: 'Is my text safe and private?' },
    a: {
      id: 'Sesi dilindungi otentikasi JWT FastAPI. Data draf Anda dienkripsi dan diisolasi khusus untuk akun Anda.',
      en: 'Sessions are protected with FastAPI JWT authentication. Your draft data is isolated strictly to your account.',
    },
  },
  {
    q: { id: 'Bahasa apa yang didukung?', en: 'What languages are supported?' },
    a: {
      id: 'Bahasa Indonesia dan English. Pilih bahasa analisis di toolbar editor.',
      en: 'Bahasa Indonesia and English. Choose the analysis language in the editor toolbar.',
    },
  },
  {
    q: { id: 'Format berkas apa yang bisa diunggah?', en: 'What file formats can be uploaded?' },
    a: {
      id: 'PDF, TXT, dan Markdown (maks. 10 MB). Teks dari dokumen PDF akan diekstrak secara otomatis.',
      en: 'PDF, TXT, and Markdown (max 10 MB). Text from PDF documents is extracted automatically.',
    },
  },
  {
    q: { id: 'Bagaimana skor dihitung?', en: 'How is the quality score calculated?' },
    a: {
      id: 'Skor dimulai dari 100 lalu dikurangi bobot cacat temuan (ambiguitas, non-testable, tidak lengkap, weak directive, kalimat pasif), diredam untuk teks panjang.',
      en: 'Score starts at 100 and deducts points based on defect severity (ambiguity, non-testable, incomplete, weak directives, passive voice), scaled for text length.',
    },
  },
  {
    q: { id: 'Bisakah hasilnya diekspor?', en: 'Can audit results be exported?' },
    a: {
      id: 'Bisa. Ekspor tersedia ke PDF resmi, Excel (.xlsx), Markdown (.md), atau JSON dari halaman hasil audit.',
      en: 'Yes. Export is available to official PDF, Excel (.xlsx), Markdown (.md), or JSON from the audit detail page.',
    },
  },
];

export function Faq() {
  const locale = useUILocale();

  return (
    <section id="faq" className="mx-auto max-w-[820px] scroll-mt-24 px-5 py-20">
      <SectionHead
        eyebrow="FAQ"
        title={locale === 'id' ? 'Pertanyaan yang sering diajukan' : 'Frequently Asked Questions'}
      />
      <div className="mt-10 space-y-3">
        {FAQ_DATA.map(({ q, a }, i) => (
          <details key={i} className="group card rounded-2xl px-6 py-4 open:pb-5">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-[16px] font-medium [&::-webkit-details-marker]:hidden">
              {q[locale]}
              <span
                className="text-[22px] font-light leading-none text-muted transition group-open:rotate-45"
                aria-hidden
              >
                +
              </span>
            </summary>
            <p className="mt-3 text-[14.5px] leading-relaxed text-muted">{a[locale]}</p>
          </details>
        ))}
      </div>
    </section>
  );
}

// ───────────── CTA penutup ─────────────
export function FinalCta() {
  const locale = useUILocale();

  return (
    <section className="mx-auto max-w-[1200px] px-5 pb-24 pt-8">
      <div className="rounded-[32px] bg-btn px-8 py-14 text-center text-btnink sm:px-16">
        <h2 className="mx-auto max-w-[620px] text-[30px] font-semibold leading-tight tracking-tight sm:text-[38px]">
          {locale === 'id'
            ? 'Tulis kebutuhan yang bisa diukur, bukan ditebak.'
            : 'Write requirements that can be measured, not guessed.'}
        </h2>
        <p className="mx-auto mt-4 max-w-[520px] text-[16px] opacity-70">
          {locale === 'id'
            ? 'Coba audit pertama Anda sekarang — gratis, tanpa instalasi.'
            : 'Run your first audit right now — free, no installation required.'}
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/register"
            className="inline-flex h-12 items-center gap-2 rounded-full bg-btnink px-7 text-[15px] font-semibold text-btn transition hover:opacity-90"
          >
            {locale === 'id' ? 'Daftar gratis' : 'Get started free'} <ArrowRight size={16} aria-hidden />
          </Link>
          <Link
            href="/login"
            className="inline-flex h-12 items-center rounded-full border border-btnink/25 px-7 text-[15px] font-medium transition hover:bg-btnink/10"
          >
            {locale === 'id' ? 'Masuk' : 'Sign in'}
          </Link>
        </div>
      </div>
    </section>
  );
}
