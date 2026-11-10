'use client';

import { Bell, ChevronDown, Clock, LogOut, Moon, PenLine, Sun, HelpCircle, MessageSquare, Globe } from 'lucide-react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Lock } from 'lucide-react';
import { initials, logout, useCurrentUser, verifySession } from '@/lib/auth';
import { useT } from '@/lib/i18n';
import { LanguageToggle } from './language-toggle';
import { Logo } from './logo';
import { Popover } from './popover';
import { useTheme } from './providers';
import { BackendHealthBadge } from './backend-badge';

const TABS = [
  { href: '/editor', labelKey: 'nav.editor', icon: PenLine, match: (p: string) => p.startsWith('/editor') || p.startsWith('/audit') },
  { href: '/history', labelKey: 'nav.history', icon: Clock, match: (p: string) => p.startsWith('/history') },
  { href: '/help', labelKey: 'nav.help' as const, icon: HelpCircle, match: (p: string) => p.startsWith('/help') },
  { href: '/contact', labelKey: 'nav.contact' as const, icon: MessageSquare, match: (p: string) => p.startsWith('/contact') },
];

function Navbar({ name, email }: { name: string; email: string }) {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, toggle } = useTheme();
  const t = useT();

  return (
    <header className="sticky top-0 z-40 border-b border-black/[0.07] bg-[#f7f5f1]/90 backdrop-blur-md dark:border-white/10 dark:bg-[#141416]/90">
      <nav className="mx-auto flex h-[76px] max-w-[1280px] items-center justify-between gap-3 px-6" aria-label="Navigasi utama">
        <div className="flex items-center gap-2 sm:gap-4">
          <Logo />
          <span className="hidden h-7 w-px bg-line/10 sm:block" aria-hidden />
          <div className="flex items-center gap-1 rounded-full bg-black/[0.05] p-1 dark:bg-white/[0.07]">
            {TABS.map(({ href, labelKey, icon: Icon, match }) => {
              const active = match(pathname);
              const label = labelKey === 'nav.help' ? (t('help.title').startsWith('Panduan') ? 'Panduan' : 'Help')
                : labelKey === 'nav.contact' ? (t('contact.title').startsWith('Hubungi') ? 'Kontak' : 'Contact')
                : t(labelKey);
              return (
                <Link
                  key={href}
                  href={href}
                  aria-current={active ? 'page' : undefined}
                  className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-[14px] font-medium transition ${
                    active ? 'bg-card text-ink shadow-soft' : 'text-muted hover:text-ink'
                  }`}
                >
                  <Icon size={15} aria-hidden />
                  <span className="hidden sm:inline">{label}</span>
                </Link>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <BackendHealthBadge />

          <span className="hidden items-center gap-2 text-[12.5px] text-muted md:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-faint" aria-hidden /> {t('nav.workspace')}
          </span>

          <LanguageToggle />

          <Popover
            align="right"
            trigger={({ toggle: t }) => (
              <button
                type="button"
                onClick={t}
                aria-label="Notifikasi"
                className="relative inline-flex h-10 w-10 items-center justify-center rounded-full border border-line/[0.07] bg-card/70 text-ink transition hover:bg-card"
              >
                <Bell size={17} strokeWidth={1.6} />
                <span className="absolute right-2.5 top-2.5 h-1.5 w-1.5 rounded-full bg-accent" aria-hidden />
              </button>
            )}
          >
            {() => (
              <div className="w-[260px] px-3 py-2.5">
                <p className="text-[13.5px] font-semibold">{t('nav.notifications')}</p>
                <p className="mt-1 text-[12.5px] text-muted">{t('nav.notif_welcome')}</p>
              </div>
            )}
          </Popover>

          <Popover
            align="right"
            trigger={({ toggle: t }) => (
              <button
                type="button"
                onClick={t}
                aria-label={t('nav.account_menu')}
                className="inline-flex items-center gap-1.5 rounded-full p-1 pr-2 transition hover:bg-line/[0.05]"
              >
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-line/[0.07] text-[12.5px] font-semibold">
                  {initials(name)}
                </span>
                <ChevronDown size={14} className="text-muted" aria-hidden />
              </button>
            )}
          >
            {(close) => (
              <>
                <div className="border-b border-line/[0.07] px-3 pb-2.5 pt-2">
                  <p className="text-[13.5px] font-semibold">{name}</p>
                  <p className="text-[12.5px] text-muted">{email}</p>
                </div>
                <button
                  type="button"
                  className="menu-item mt-1.5"
                  onClick={() => {
                    toggle();
                    close();
                  }}
                >
                  {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                  {theme === 'dark' ? t('nav.theme_light') : t('nav.theme_dark')}
                </button>
                <button
                  type="button"
                  className="menu-item"
                  onClick={() => {
                    logout();
                    close();
                    router.replace('/login');
                  }}
                >
                  <LogOut size={16} /> {t('nav.logout')}
                </button>
              </>
            )}
          </Popover>
        </div>
      </nav>
    </header>
  );
}

/** Kerangka halaman terproteksi: wajib login, navbar, dan footer terintegrasi. */
export function AppShell({ children }: { children: React.ReactNode }) {
  const user = useCurrentUser();
  const router = useRouter();
  const t = useT();

  useEffect(() => {
    if (user === null) {
      router.replace('/login');
    } else if (user) {
      verifySession();
    }
  }, [user, router]);

  if (!user) return <div className="min-h-screen" aria-busy="true" />;

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar name={user.name} email={user.email} />
      <div className="mx-auto flex w-full max-w-[1080px] flex-1 flex-col px-4 pb-6">
        <main className="flex-1 pb-6 pt-10">{children}</main>
        <footer className="flex flex-wrap items-center justify-between gap-2 text-[12px] text-muted">
          <span className="inline-flex items-center gap-2">
            <Lock size={14} aria-hidden /> {t('nav.footer_jwt')}
          </span>
          <span>ReqLint v1.0 · Arsitektur Terintegrasi</span>
        </footer>
      </div>
    </div>
  );
}

export function PageHeader({
  crumb,
  title,
  subtitle,
  right,
}: {
  crumb: string;
  title: string;
  subtitle?: React.ReactNode;
  right?: React.ReactNode;
}) {
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div>
        <p className="eyebrow">{crumb}</p>
        <h1 className="mt-2 text-[34px] font-medium leading-tight tracking-[-0.02em] sm:text-[42px]">{title}</h1>
        {subtitle && <div className="mt-2 text-[15px] text-muted">{subtitle}</div>}
      </div>
      {right}
    </div>
  );
}
