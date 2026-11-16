'use client';

import { useEffect } from 'react';
import { useUILocale } from '@/lib/i18n';

/**
 * Task 09: sinkronkan atribut `lang` dokumen dengan locale UI yang dipilih,
 * sehingga screen reader memakai pelafalan yang benar. SSR tetap merender
 * lang="id" (default store) tanpa hydration mismatch — efek ini hanya
 * berjalan setelah mount.
 */
export function LocaleHtmlSync() {
  const locale = useUILocale();

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  return null;
}
