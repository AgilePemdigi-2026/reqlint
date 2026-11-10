'use client';

import Link from 'next/link';
import { Logo } from '@/components/logo';
import { useUILocale } from '@/lib/i18n';

export function LandingFooter() {
  const locale = useUILocale();

  return (
    <footer className="border-t border-line/[0.07]">
      <div className="mx-auto flex max-w-[1200px] flex-col gap-8 px-5 py-10 md:flex-row md:items-start md:justify-between">
        <div className="max-w-[320px]">
          <Logo small />
          <p className="mt-3 text-[13.5px] leading-relaxed text-muted">
            {locale === 'id'
              ? 'Audit kualitas User Story dengan standar ISO 29148 dan INVEST.'
              : 'User Story quality assurance platform based on ISO 29148 and INVEST.'}
          </p>
        </div>
        <nav className="flex gap-16 text-[14px]" aria-label="Tautan footer">
          <ul className="space-y-2.5">
            <li className="eyebrow mb-3">{locale === 'id' ? 'Produk' : 'Product'}</li>
            <li><a href="#fitur" className="text-muted hover:text-ink">{locale === 'id' ? 'Fitur' : 'Features'}</a></li>
            <li><a href="#cara-kerja" className="text-muted hover:text-ink">{locale === 'id' ? 'Cara Kerja' : 'How It Works'}</a></li>
            <li><a href="#standar" className="text-muted hover:text-ink">{locale === 'id' ? 'Standar' : 'Standards'}</a></li>
          </ul>
          <ul className="space-y-2.5">
            <li className="eyebrow mb-3">{locale === 'id' ? 'Akun' : 'Account'}</li>
            <li><Link href="/login" className="text-muted hover:text-ink">{locale === 'id' ? 'Masuk' : 'Sign in'}</Link></li>
            <li><Link href="/register" className="text-muted hover:text-ink">{locale === 'id' ? 'Daftar' : 'Register'}</Link></li>
            <li><Link href="/editor" className="text-muted hover:text-ink">{locale === 'id' ? 'Editor' : 'Editor'}</Link></li>
          </ul>
        </nav>
      </div>
      <div className="mx-auto max-w-[1200px] px-5 pb-8 text-[12.5px] text-muted">
        © {new Date().getFullYear()} ReqLint · {locale === 'id' ? 'Pratinjau interaktif' : 'Interactive preview'}
      </div>
    </footer>
  );
}
