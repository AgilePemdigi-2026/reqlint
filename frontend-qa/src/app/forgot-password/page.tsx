'use client';

import { ArrowLeft, Loader2, Mail, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';
import { AuthShell } from '@/components/auth/auth-shell';
import { TextField } from '@/components/auth/fields';
import { useT } from '@/lib/i18n';
import { apiForgotPassword } from '@/lib/api';

export default function ForgotPasswordPage() {
  const t = useT();
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const email = (form.get('email') as string)?.trim();
    if (!email) return;

    setBusy(true);
    setError('');

    try {
      await apiForgotPassword({ email });
      setSent(true);
    } catch (err: any) {
      // Tetap tampilkan pesan sukses untuk mencegah user enumeration
      setSent(true);
    } finally {
      setBusy(false);
    }
  }

  if (sent) {
    return (
      <AuthShell>
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900/30">
            <CheckCircle2 size={28} className="text-emerald-600 dark:text-emerald-400" />
          </div>
          <h1 className="text-[24px] font-bold">{t('forgot.title')}</h1>
          <p className="max-w-[360px] text-[14px] text-muted">{t('forgot.success')}</p>
          <Link href="/login" className="btn-primary mt-3 h-11 px-6 text-[14px]">
            <ArrowLeft size={15} aria-hidden /> {t('forgot.back_login')}
          </Link>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell>
      <h1 className="text-[30px] font-bold leading-tight tracking-tight">{t('forgot.title')}</h1>
      <p className="mt-2.5 text-[15px] text-muted">{t('forgot.subtitle')}</p>

      <form onSubmit={onSubmit} noValidate className="mt-8 space-y-5">
        <TextField
          label={t('forgot.email')}
          name="email"
          type="email"
          autoComplete="email"
          placeholder={t('forgot.email_placeholder')}
          error={error}
        />

        <button type="submit" disabled={busy} className="btn-primary relative h-[52px] w-full text-[16px] disabled:opacity-60">
          {busy ? (
            <span className="inline-flex items-center gap-2">
              <Loader2 size={18} className="animate-spin" aria-hidden /> {t('forgot.sending')}
            </span>
          ) : (
            <span className="inline-flex items-center gap-2">
              <Mail size={18} aria-hidden /> {t('forgot.submit')}
            </span>
          )}
        </button>
      </form>

      <p className="mt-6 text-center text-[14px] text-muted">
        <Link href="/login" className="font-semibold text-accent hover:underline">
          <ArrowLeft size={13} className="mr-1 inline" aria-hidden />
          {t('forgot.back_login')}
        </Link>
      </p>
    </AuthShell>
  );
}

