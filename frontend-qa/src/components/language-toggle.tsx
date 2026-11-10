'use client';

import { Globe } from 'lucide-react';
import { useUILocale, setUILocale, type UILocale } from '@/lib/i18n';

export function LanguageToggle() {
  const locale = useUILocale();
  const next: UILocale = locale === 'id' ? 'en' : 'id';
  const label = locale === 'id' ? 'EN' : 'ID';

  return (
    <button
      type="button"
      onClick={() => setUILocale(next)}
      aria-label={locale === 'id' ? 'Switch to English' : 'Ganti ke Bahasa Indonesia'}
      className="inline-flex h-10 items-center gap-1.5 rounded-full px-3 text-[13px] font-medium text-muted transition hover:bg-line/[0.06] hover:text-ink"
    >
      <Globe size={16} strokeWidth={1.6} />
      {label}
    </button>
  );
}

