'use client';

import { Mail, Github, Users, GraduationCap, Send, Loader2, CheckCircle2 } from 'lucide-react';
import { useState } from 'react';
import { PageHeader } from '@/components/app-shell';
import { useToast } from '@/components/providers';
import { useT } from '@/lib/i18n';

const TEAM_MEMBERS = [
  'Fajar Akbar Putra',
  'Bimantara Jati Purnama',
  'Anggota Tim 3',
  'Anggota Tim 4',
  'Anggota Tim 5',
];

export default function ContactPage() {
  const toast = useToast();
  const t = useT();
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);

    // Simulasi pengiriman (karena belum ada backend endpoint contact)
    await new Promise((r) => setTimeout(r, 1200));

    setBusy(false);
    setSent(true);
    toast(t('contact.success'));

    // Reset form
    (e.target as HTMLFormElement).reset();
    setTimeout(() => setSent(false), 4000);
  }

  return (
    <>
      <PageHeader
        crumb={t('contact.crumb')}
        title={t('contact.title')}
        subtitle={t('contact.subtitle')}
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* ── Form Kontak ── */}
        <div className="card p-6 lg:col-span-2">
          <h2 className="text-[18px] font-semibold">{t('contact.form_title')}</h2>

          {sent && (
            <div className="mt-4 flex items-center gap-2 rounded-2xl bg-emerald-50 px-4 py-3 text-[13.5px] text-emerald-700 dark:bg-emerald-400/10 dark:text-emerald-300">
              <CheckCircle2 size={16} />
              {t('contact.success')}
            </div>
          )}

          <form onSubmit={onSubmit} className="mt-5 space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-[13px] font-medium">{t('contact.name')}</label>
                <input
                  name="name"
                  required
                  placeholder={t('contact.name_placeholder')}
                  className="field h-11 w-full rounded-xl px-4 text-[14px]"
                />
              </div>
              <div>
                <label className="mb-1.5 block text-[13px] font-medium">{t('contact.email')}</label>
                <input
                  name="email"
                  type="email"
                  required
                  placeholder={t('contact.email_placeholder')}
                  className="field h-11 w-full rounded-xl px-4 text-[14px]"
                />
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-[13px] font-medium">{t('contact.subject')}</label>
              <input
                name="subject"
                required
                placeholder={t('contact.subject_placeholder')}
                className="field h-11 w-full rounded-xl px-4 text-[14px]"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-[13px] font-medium">{t('contact.message')}</label>
              <textarea
                name="message"
                required
                rows={5}
                placeholder={t('contact.message_placeholder')}
                className="field w-full resize-none rounded-xl px-4 py-3 text-[14px]"
              />
            </div>

            <button
              type="submit"
              disabled={busy}
              className="btn-primary h-11 px-6 text-[14px] disabled:opacity-60"
            >
              {busy ? (
                <span className="inline-flex items-center gap-2">
                  <Loader2 size={16} className="animate-spin" aria-hidden /> {t('contact.sending')}
                </span>
              ) : (
                <span className="inline-flex items-center gap-2">
                  <Send size={15} aria-hidden /> {t('contact.submit')}
                </span>
              )}
            </button>
          </form>
        </div>

        {/* ── Sidebar Info ── */}
        <div className="space-y-5">
          <div className="card p-6">
            <h3 className="text-[16px] font-semibold">{t('contact.info_title')}</h3>

            <div className="mt-4 space-y-4 text-[14px]">
              <div className="flex items-start gap-3">
                <Mail size={18} className="mt-0.5 shrink-0 text-accent" />
                <div>
                  <p className="font-medium">{t('contact.info_email')}</p>
                  <a href="mailto:support@reqlint.app" className="text-muted hover:text-accent hover:underline">
                    support@reqlint.app
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Github size={18} className="mt-0.5 shrink-0 text-accent" />
                <div>
                  <p className="font-medium">{t('contact.info_github')}</p>
                  <a
                    href="https://github.com/reqlint"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-muted hover:text-accent hover:underline"
                  >
                    github.com/reqlint
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <GraduationCap size={18} className="mt-0.5 shrink-0 text-accent" />
                <div>
                  <p className="font-medium">{t('contact.info_univ')}</p>
                  <p className="text-muted">{t('contact.info_team_desc')}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="flex items-center gap-2 text-[16px] font-semibold">
              <Users size={18} className="text-accent" />
              {t('contact.info_team')}
            </h3>
            <ul className="mt-3 space-y-2">
              {TEAM_MEMBERS.map((name) => (
                <li key={name} className="flex items-center gap-2.5 text-[14px]">
                  <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-line/[0.07] text-[11px] font-semibold">
                    {name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase()}
                  </span>
                  {name}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}

