'use client';

import { ShieldCheck } from 'lucide-react';
import { Hero } from '@/components/landing/hero';
import { LandingFooter } from '@/components/landing/footer';
import { LandingNav } from '@/components/landing/landing-nav';
import { Faq, Features, FinalCta, HowItWorks, Privacy, Standards } from '@/components/landing/sections';
import { useT } from '@/lib/i18n';

/** Landing page publik (tanpa login). Task 09: sepenuhnya dwibahasa. */
export default function LandingPage() {
  const t = useT();

  return (
    <div className="min-h-screen bg-[#f7f5f1] dark:bg-[#141416]">
      <LandingNav />

      <div className="bg-[#e6f0fa] text-center text-[15px] text-[#0b5c8a] dark:bg-[#12263a] dark:text-[#7fc0f0]">
        <a href="#privasi" className="inline-flex flex-wrap items-center justify-center gap-2.5 px-5 py-3.5">
          <ShieldCheck size={20} strokeWidth={1.6} aria-hidden />
          <span>{t('landing.banner')}</span>
          <span className="font-medium underline underline-offset-2">{t('landing.banner_cta')}</span>
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
