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
import { CATEGORY_STYLE, categoryLabelT } from '@/lib/format';
import type { Category } from '@/lib/analyzer';
import { useT } from '@/lib/i18n';

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
const FEATURES: Array<{ icon: LucideIcon; titleKey: string; descKey: string }> = [
  { icon: PenLine, titleKey: 'landing.feat1_title', descKey: 'landing.feat1_desc' },
  { icon: Gauge, titleKey: 'landing.feat2_title', descKey: 'landing.feat2_desc' },
  { icon: ScanSearch, titleKey: 'landing.feat3_title', descKey: 'landing.feat3_desc' },
  { icon: Wand2, titleKey: 'landing.feat4_title', descKey: 'landing.feat4_desc' },
  { icon: ListChecks, titleKey: 'landing.feat5_title', descKey: 'landing.feat5_desc' },
  { icon: Columns2, titleKey: 'landing.feat6_title', descKey: 'landing.feat6_desc' },
];

export function Features() {
  const t = useT();
  return (
    <section id="fitur" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <SectionHead
        eyebrow={t('landing.features_eyebrow')}
        title={t('landing.features_title')}
        subtitle={t('landing.features_subtitle')}
      />
      <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map(({ icon: Icon, titleKey, descKey }) => (
          <article key={titleKey} className="card rounded-[22px] p-6">
            <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-line/[0.07] bg-card">
              <Icon size={19} strokeWidth={1.6} aria-hidden />
            </span>
            <h3 className="mt-5 text-[17px] font-semibold">{t(titleKey)}</h3>
            <p className="mt-2 text-[14.5px] leading-relaxed text-muted">{t(descKey)}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

// ───────────── Cara kerja ─────────────
const STEPS = [
  { n: '01', titleKey: 'landing.step1_title', descKey: 'landing.step1_desc' },
  { n: '02', titleKey: 'landing.step2_title', descKey: 'landing.step2_desc' },
  { n: '03', titleKey: 'landing.step3_title', descKey: 'landing.step3_desc' },
];

export function HowItWorks() {
  const t = useT();
  return (
    <section id="cara-kerja" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <SectionHead eyebrow={t('landing.how_eyebrow')} title={t('landing.how_title')} />
      <ol className="mt-12 grid gap-5 md:grid-cols-3">
        {STEPS.map((s) => (
          <li key={s.n} className="card rounded-[22px] p-7">
            <span className="font-mono text-[13px] font-medium text-accent">{s.n}</span>
            <h3 className="mt-4 text-[19px] font-semibold">{t(s.titleKey)}</h3>
            <p className="mt-2 text-[14.5px] leading-relaxed text-muted">{t(s.descKey)}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

// ───────────── Standar ─────────────
const ISO_CRITERIA = [
  ['landing.iso1_title', 'landing.iso1_desc'],
  ['landing.iso2_title', 'landing.iso2_desc'],
  ['landing.iso3_title', 'landing.iso3_desc'],
  ['landing.iso4_title', 'landing.iso4_desc'],
  ['landing.iso5_title', 'landing.iso5_desc'],
];

const INVEST: Array<[string, string, string]> = [
  ['I', 'Independent', 'landing.invest_i'],
  ['N', 'Negotiable', 'landing.invest_n'],
  ['V', 'Valuable', 'landing.invest_v'],
  ['E', 'Estimable', 'landing.invest_e'],
  ['S', 'Small', 'landing.invest_s'],
  ['T', 'Testable', 'landing.invest_t'],
];

const FINDING_EXAMPLES: Array<[Category, string]> = [
  ['ambiguity', 'landing.example_ambiguity'],
  ['non-testable', 'landing.example_non-testable'],
  ['incomplete', 'landing.example_incomplete'],
  ['weak-directive', 'landing.example_weak-directive'],
  ['passive-voice', 'landing.example_passive-voice'],
];

export function Standards() {
  const t = useT();
  return (
    <section id="standar" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <SectionHead
        eyebrow={t('landing.standards_eyebrow')}
        title={t('landing.standards_title')}
        subtitle={t('landing.standards_subtitle')}
      />

      <div className="mt-12 grid gap-5 lg:grid-cols-2">
        <div className="card rounded-[22px] p-7">
          <h3 className="text-[18px] font-semibold">{t('landing.doc_check_title')}</h3>
          <p className="mt-1 text-[14px] text-muted">{t('landing.doc_check_desc')}</p>
          <ul className="mt-5 divide-y divide-line/[0.07]">
            {ISO_CRITERIA.map(([tk, dk]) => (
              <li key={tk} className="py-3">
                <p className="text-[14.5px] font-medium">{t(tk)}</p>
                <p className="text-[13.5px] text-muted">{t(dk)}</p>
              </li>
            ))}
          </ul>
        </div>

        <div className="card rounded-[22px] p-7">
          <h3 className="text-[18px] font-semibold">{t('landing.invest_title')}</h3>
          <p className="mt-1 text-[14px] text-muted">{t('landing.invest_desc')}</p>
          <ul className="mt-5 grid gap-3 sm:grid-cols-2">
            {INVEST.map(([k, name, dk]) => (
              <li key={k} className="flex gap-3 rounded-2xl bg-line/[0.04] p-4">
                <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-card text-[15px] font-bold shadow-soft">
                  {k}
                </span>
                <span>
                  <span className="block text-[14px] font-semibold">{name}</span>
                  <span className="block text-[12.5px] leading-snug text-muted">{t(dk)}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card mt-5 rounded-[22px] p-7">
        <h3 className="text-[18px] font-semibold">{t('landing.finding_examples_title')}</h3>
        <ul className="mt-4 flex flex-wrap gap-x-8 gap-y-4">
          {FINDING_EXAMPLES.map(([cat, ex]) => (
            <li key={cat} className="flex items-center gap-2.5">
              <span className={`pill ${CATEGORY_STYLE[cat]}`}>{categoryLabelT(cat, t)}</span>
              <code className="rounded-md bg-line/[0.06] px-2 py-1 font-mono text-[12px]">{t(ex)}</code>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

// ───────────── Privasi ─────────────
export function Privacy() {
  const t = useT();
  return (
    <section id="privasi" className="mx-auto max-w-[1200px] scroll-mt-24 px-5 py-20">
      <div className="card flex flex-col items-start gap-8 rounded-[28px] p-8 sm:p-12 md:flex-row md:items-center">
        <span className="inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-line/[0.07] bg-card">
          <Lock size={24} strokeWidth={1.5} aria-hidden />
        </span>
        <div className="flex-1">
          <h2 className="text-[26px] font-semibold tracking-tight">{t('landing.privacy_title')}</h2>
          <p className="mt-2 max-w-[640px] text-[15.5px] leading-relaxed text-muted">
            {t('landing.privacy_p1')}
          </p>
          <p className="mt-2 max-w-[640px] text-[15.5px] leading-relaxed text-muted">
            {t('landing.privacy_p2')}
          </p>
        </div>
      </div>
    </section>
  );
}

// ───────────── FAQ ─────────────
const FAQ: Array<[string, string]> = [
  ['landing.faq1_q', 'landing.faq1_a'],
  ['landing.faq2_q', 'landing.faq2_a'],
  ['landing.faq3_q', 'landing.faq3_a'],
  ['landing.faq4_q', 'landing.faq4_a'],
  ['landing.faq5_q', 'landing.faq5_a'],
  ['landing.faq6_q', 'landing.faq6_a'],
];

export function Faq() {
  const t = useT();
  return (
    <section id="faq" className="mx-auto max-w-[820px] scroll-mt-24 px-5 py-20">
      <SectionHead eyebrow="FAQ" title={t('landing.faq_title')} />
      <div className="mt-10 space-y-3">
        {FAQ.map(([qk, ak]) => (
          <details key={qk} className="group card rounded-2xl px-6 py-4 open:pb-5">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-[16px] font-medium [&::-webkit-details-marker]:hidden">
              {t(qk)}
              <span
                className="text-[22px] font-light leading-none text-muted transition group-open:rotate-45"
                aria-hidden
              >
                +
              </span>
            </summary>
            <p className="mt-3 text-[14.5px] leading-relaxed text-muted">{t(ak)}</p>
          </details>
        ))}
      </div>
    </section>
  );
}

// ───────────── CTA penutup ─────────────
export function FinalCta() {
  const t = useT();
  return (
    <section className="mx-auto max-w-[1200px] px-5 pb-24 pt-8">
      <div className="rounded-[32px] bg-btn px-8 py-14 text-center text-btnink sm:px-16">
        <h2 className="mx-auto max-w-[620px] text-[30px] font-semibold leading-tight tracking-tight sm:text-[38px]">
          {t('landing.cta_title')}
        </h2>
        <p className="mx-auto mt-4 max-w-[520px] text-[16px] opacity-70">
          {t('landing.cta_desc')}
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/register"
            className="inline-flex h-12 items-center gap-2 rounded-full bg-btnink px-7 text-[15px] font-semibold text-btn transition hover:opacity-90"
          >
            {t('landing.cta_register')} <ArrowRight size={16} aria-hidden />
          </Link>
          <Link
            href="/login"
            className="inline-flex h-12 items-center rounded-full border border-btnink/25 px-7 text-[15px] font-medium transition hover:bg-btnink/10"
          >
            {t('landing.cta_signin')}
          </Link>
        </div>
      </div>
    </section>
  );
}
