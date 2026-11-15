'use client';

import Link from 'next/link';
import { Logo } from '@/components/logo';
import { useT } from '@/lib/i18n';

export function LandingFooter() {
  const t = useT();

  return (
    <footer className="border-t border-line/[0.07]">
      <div className="mx-auto flex max-w-[1200px] flex-col gap-8 px-5 py-10 md:flex-row md:items-start md:justify-between">
        <div className="max-w-[320px]">
          <Logo small />
          <p className="mt-3 text-[13.5px] leading-relaxed text-muted">
            {t('landing.footer_desc')}
          </p>
        </div>
        <nav className="flex gap-16 text-[14px]" aria-label={t('landing.footer_nav_aria')}>
          <ul className="space-y-2.5">
            <li className="eyebrow mb-3">{t('landing.footer_product')}</li>
            <li><a href="#fitur" className="text-muted hover:text-ink">{t('landing.footer_features')}</a></li>
            <li><a href="#cara-kerja" className="text-muted hover:text-ink">{t('landing.footer_how')}</a></li>
            <li><a href="#standar" className="text-muted hover:text-ink">{t('landing.footer_standards')}</a></li>
          </ul>
          <ul className="space-y-2.5">
            <li className="eyebrow mb-3">{t('landing.footer_account')}</li>
            <li><Link href="/login" className="text-muted hover:text-ink">{t('landing.footer_signin')}</Link></li>
            <li><Link href="/register" className="text-muted hover:text-ink">{t('landing.footer_register')}</Link></li>
            <li><Link href="/editor" className="text-muted hover:text-ink">{t('landing.footer_editor')}</Link></li>
          </ul>
        </nav>
      </div>
      <div className="mx-auto max-w-[1200px] px-5 pb-8 text-[12.5px] text-muted">
        © {new Date().getFullYear()} ReqLint · {t('landing.footer_preview')}
      </div>
    </footer>
  );
}
