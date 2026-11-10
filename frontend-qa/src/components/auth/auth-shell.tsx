'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Logo } from '@/components/logo';
import { ThemeToggle } from '@/components/theme-toggle';
import { LanguageToggle } from '@/components/language-toggle';
import { useT } from '@/lib/i18n';

export function AuthShell({ children, footer }: { children: React.ReactNode; footer?: React.ReactNode }) {
  const t = useT();

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between px-6 py-6 sm:px-12">
        <Logo />
        <div className="flex items-center gap-2 sm:gap-3">
          <Link
            href="/editor"
            className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-[14px] font-medium text-muted transition hover:text-ink"
          >
            <ArrowLeft size={16} aria-hidden /> {t('landing.open_workspace')}
          </Link>
          <LanguageToggle />
          <ThemeToggle />
        </div>
      </header>
      <main className="flex flex-1 flex-col items-center px-4 pb-10 pt-2 sm:pt-6">
        <div className="card w-full max-w-[430px] rounded-[30px] p-8 sm:p-10">{children}</div>
        {footer}
      </main>
    </div>
  );
}
