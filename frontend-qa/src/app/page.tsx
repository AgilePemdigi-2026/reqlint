'use client';

import { ShieldCheck } from 'lucide-react';
import { Hero } from '@/components/landing/hero';
import { LandingFooter } from '@/components/landing/footer';
import { LandingNav } from '@/components/landing/landing-nav';
import { Faq, Features, FinalCta, HowItWorks, Privacy, Standards } from '@/components/landing/sections';
import { useUILocale } from '@/lib/i18n';

/** Landing page publik (tanpa login). */
export default function LandingPage() {
  const locale = useUILocale();

  return (
    <div className="min-h-screen bg-[#f7f5f1] dark:bg-[#141416]">
      <LandingNav />

      <div className="bg-[#e6f0fa] text-center text-[15px] text-[#0b5c8a] dark:bg-[#12263a] dark:text-[#7fc0f0]">
        <a href="#privasi" className="inline-flex flex-wrap items-center justify-center gap-2.5 px-5 py-3.5">
          <ShieldCheck size={20} strokeWidth={1.6} aria-hidden />
          <span>
            {locale === 'id'
              ? 'Analisis berjalan secara instan dan aman — mendukung Connextra & kriteria INVEST dwibahasa.'
              : 'Instant and secure requirement analysis — supporting bilingual Connextra & INVEST criteria.'}
          </span>
          <span className="font-medium underline underline-offset-2">
            {locale === 'id' ? 'Pelajari lebih lanjut →' : 'Learn more →'}
          </span>
        </a>
      </div>

      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Standards />
        <Privacy />
        <Faq />
        <FinalCta />
      </main>
      <LandingFooter />
    </div>
  );
}
