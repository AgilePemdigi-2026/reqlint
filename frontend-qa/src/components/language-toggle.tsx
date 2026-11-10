'use client';

import { Globe } from 'lucide-react';
import { useUILocale, setUILocale, type UILocale } from '@/lib/i18n';

export function LanguageToggle() {
  const locale = useUILocale();
  const next: UILocale = locale === 'id' ? 'en' : 'id';

  return (
    <button
      type="button"
      onClick={() => setUILocale(next)}
      aria-label={locale === 'id' ? 'Switch to English' : 'Ganti ke Bahasa Indonesia'}
      className="inline-flex h-10 items-center gap-1.5 rounded-full border border-line/[0.08] px-3 text-[13px] font-medium text-muted transition hover:bg-line/[0.06] hover:text-ink"
      title={locale === 'id' ? 'Ganti bahasa ke English' : 'Switch language to Indonesian'}
    >
      <Globe size={15} strokeWidth={1.6} />
      <span className={locale === 'id' ? 'font-bold text-accent' : 'opacity-60'}>ID</span>
      <span className="opacity-30">/</span>
      <span className={locale === 'en' ? 'font-bold text-accent' : 'opacity-60'}>EN</span>
    </button>
  );
}
