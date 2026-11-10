'use client';

import Link from 'next/link';
import { Logo } from '@/components/logo';
import { ThemeToggle } from '@/components/theme-toggle';
import { LanguageToggle } from '@/components/language-toggle';
import { BackendHealthBadge } from '@/components/backend-badge';
import { useCurrentUser } from '@/lib/auth';
import { useT } from '@/lib/i18n';

export function LandingNav() {
  const user = useCurrentUser();
  const t = useT();

  const links = [
    { href: '#fitur', label: t('landing.features') },
    { href: '#cara-kerja', label: t('landing.how_it_works') },
    { href: '#standar', label: t('landing.standards') },
    { href: '#faq', label: t('landing.faq') },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-black/[0.07] bg-[#f7f5f1]/90 backdrop-blur-md dark:border-white/10 dark:bg-[#141416]/90">
      <nav className="mx-auto flex h-[76px] max-w-[1280px] items-center justify-between gap-4 px-6" aria-label="Navigasi utama">
        <div className="flex items-center gap-12">
          <Logo />
          <ul className="hidden items-center gap-9 lg:flex">
            {links.map((l) => (
              <li key={l.href}>
                <a href={l.href} className="text-[16px] text-ink/80 transition hover:text-ink">
                  {l.label}
                </a>
              </li>
            ))}
          </ul>
        </div>

        <div className="flex items-center gap-2 sm:gap-4">
          <BackendHealthBadge />
          <LanguageToggle />
          <ThemeToggle />
          {user ? (
            <Link href="/editor" className="btn-primary h-11 rounded-full px-6 text-[15px]">
              {t('landing.open_workspace')}
            </Link>
          ) : (
            <>
              <Link href="/login" className="hidden px-2 text-[15px] text-ink/80 transition hover:text-ink sm:inline">
                {t('landing.login')}
              </Link>
              <Link
                href="/editor"
                className="hidden h-11 items-center rounded-full border border-emerald-800/35 px-5 text-[15px] font-medium text-emerald-900 transition hover:bg-emerald-800/[0.06] dark:border-emerald-400/40 dark:text-emerald-300 md:inline-flex"
              >
                {t('landing.open_editor')}
              </Link>
              <Link href="/register" className="btn-primary h-11 rounded-full px-6 text-[15px]">
                {t('landing.start_free')}
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
