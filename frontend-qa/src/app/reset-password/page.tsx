'use client';

import { ArrowRight, Loader2, CheckCircle2, ShieldAlert } from 'lucide-react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense, useState } from 'react';
import { AuthShell } from '@/components/auth/auth-shell';
import { PasswordField } from '@/components/auth/fields';
import { useT } from '@/lib/i18n';
import { apiResetPassword } from '@/lib/api';

function ResetPasswordForm() {
  const t = useT();
  const searchParams = useSearchParams();
  const token = searchParams.get('token') ?? '';
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  if (!token) {
    return (
      <AuthShell>
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-rose-100 dark:bg-rose-900/30">
            <ShieldAlert size={28} className="text-rose-600 dark:text-rose-400" />
          </div>
          <h1 className="text-[24px] font-bold">{t('reset.title')}</h1>
          <p className="max-w-[360px] text-[14px] text-muted">{t('reset.invalid_token')}</p>
          <Link href="/forgot-password" className="btn-primary mt-3 h-11 px-6 text-[14px]">
            {t('forgot.title')}
          </Link>
        </div>
      </AuthShell>
    );
  }

  if (done) {
    return (
      <AuthShell>
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900/30">
            <CheckCircle2 size={28} className="text-emerald-600 dark:text-emerald-400" />
          </div>
          <h1 className="text-[24px] font-bold">{t('reset.title')}</h1>
          <p className="max-w-[360px] text-[14px] text-muted">{t('reset.success')}</p>
          <Link href="/login" className="btn-primary mt-3 h-11 px-6 text-[14px]">
            {t('login.submit')} <ArrowRight size={15} aria-hidden />
          </Link>
        </div>
      </AuthShell>
    );
  }

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const password = form.get('password') as string;
    const confirm = form.get('confirm') as string;

    if (password.length < 8) {
      return setErrors({ password: 'Minimal 8 karakter' });
    }
    if (password !== confirm) {
      return setErrors({ confirm: 'Konfirmasi sandi tidak cocok' });
    }

    setBusy(true);
    setErrors({});

    try {
      await apiResetPassword({
        token,
        password,
        password_confirmation: confirm,
      });
      setDone(true);
    } catch (err: any) {
      const msg = err?.response?.data?.message || t('reset.invalid_token');
      setErrors({ form: msg });
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell>
      <h1 className="text-[30px] font-bold leading-tight tracking-tight">{t('reset.title')}</h1>
      <p className="mt-2.5 text-[15px] text-muted">{t('reset.subtitle')}</p>

      <form onSubmit={onSubmit} noValidate className="mt-8 space-y-5">
        <PasswordField
          label={t('reset.password')}
          name="password"
          autoComplete="new-password"
          placeholder={t('reset.password_placeholder')}
          error={errors.password}
        />
        <PasswordField
          label={t('reset.confirm')}
          name="confirm"
          autoComplete="new-password"
          placeholder={t('reset.confirm_placeholder')}
          error={errors.confirm}
        />

        {errors.form && (
          <p role="alert" className="rounded-2xl bg-rose-50 px-4 py-3 text-[13.5px] text-rose-700 dark:bg-rose-400/10 dark:text-rose-300">
            {errors.form}
          </p>
        )}

        <button type="submit" disabled={busy} className="btn-primary relative h-[52px] w-full text-[16px] disabled:opacity-60">
          {busy ? (
            <span className="inline-flex items-center gap-2">
              <Loader2 size={18} className="animate-spin" aria-hidden /> {t('reset.processing')}
            </span>
          ) : (
            t('reset.submit')
          )}
        </button>
      </form>
    </AuthShell>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<AuthShell><div className="min-h-[200px]" aria-busy="true" /></AuthShell>}>
      <ResetPasswordForm />
    </Suspense>
  );
}

