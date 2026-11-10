'use client';

import { ArrowRight, ShieldCheck, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { AuthShell } from '@/components/auth/auth-shell';
import { PasswordField, TextField } from '@/components/auth/fields';
import { useToast } from '@/components/providers';
import { login, loginDemo } from '@/lib/auth';
import { fieldErrors, loginSchema } from '@/lib/validation';
import { useT } from '@/lib/i18n';

export default function LoginPage() {
  const router = useRouter();
  const toast = useToast();
  const t = useT();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget)) as Record<string, string>;
    const parsed = loginSchema.safeParse(data);
    if (!parsed.success) return setErrors(fieldErrors(parsed.error));

    setBusy(true);
    setErrors({});
    const result = await login(parsed.data.email, parsed.data.password);
    setBusy(false);
    if (!result.ok) return setErrors({ form: result.error });
    
    toast(t('login.success'));
    router.replace('/editor');
  }

  async function onDemo() {
    setBusy(true);
    setErrors({});
    const result = await loginDemo();
    setBusy(false);
    if (!result.ok) return setErrors({ form: result.error });
    
    toast(t('login.demo_success'));
    router.replace('/editor');
  }

  return (
    <AuthShell
      footer={
        <div className="mt-6 flex flex-col items-center gap-3 text-center">
          <button
            type="button"
            onClick={onDemo}
            disabled={busy}
            className="inline-flex items-center gap-2 text-[14px] font-medium text-muted transition hover:text-ink disabled:opacity-50"
          >
            {busy ? (
              <>
                <Loader2 size={15} className="animate-spin" aria-hidden /> {t('login.demo_connecting')}
              </>
            ) : (
              <>
                {t('login.demo')} <ArrowRight size={15} aria-hidden />
              </>
            )}
          </button>
          <p className="flex items-center gap-1.5 text-[12px] text-muted">
            <ShieldCheck size={14} aria-hidden /> {t('login.jwt_info')}
          </p>
        </div>
      }
    >
      <h1 className="text-[30px] font-bold leading-tight tracking-tight">{t('login.title')}</h1>
      <p className="mt-2.5 text-[15px] text-muted">{t('login.subtitle')}</p>

      <form onSubmit={onSubmit} noValidate className="mt-8 space-y-5">
        <TextField
          label={t('login.email')}
          name="email"
          type="email"
          autoComplete="email"
          placeholder="nama@perusahaan.com"
          error={errors.email}
        />
        <PasswordField
          label={t('login.password')}
          name="password"
          autoComplete="current-password"
          placeholder={t('login.password_placeholder')}
          error={errors.password}
        />
        <div className="flex justify-end">
          <Link
            href="/forgot-password"
            className="text-[13.5px] font-medium text-accent hover:underline"
          >
            {t('login.forgot')}
          </Link>
        </div>

        {errors.form && (
          <p role="alert" className="rounded-2xl bg-rose-50 px-4 py-3 text-[13.5px] text-rose-700 dark:bg-rose-400/10 dark:text-rose-300">
            {errors.form}
          </p>
        )}

        <button type="submit" disabled={busy} className="btn-primary relative h-[52px] w-full text-[16px] disabled:opacity-60">
          {busy ? t('login.processing') : t('login.submit')}
          {!busy && <ArrowRight size={18} className="absolute right-5" aria-hidden />}
        </button>
      </form>

      <p className="mt-6 text-center text-[14px] text-muted">
        {t('login.no_account')}{' '}
        <Link href="/register" className="font-semibold text-accent hover:underline">
          {t('login.register')}
        </Link>
      </p>
    </AuthShell>
  );
}
