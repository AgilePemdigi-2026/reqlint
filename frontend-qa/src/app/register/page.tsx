'use client';

import { ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { AuthShell } from '@/components/auth/auth-shell';
import { PasswordField, TextField } from '@/components/auth/fields';
import { useToast } from '@/components/providers';
import { register } from '@/lib/auth';
import { fieldErrors, passwordStrength, registerSchema } from '@/lib/validation';

const STRENGTH_COLOR = ['', 'bg-rose-500', 'bg-amber-500', 'bg-lime-500', 'bg-emerald-500'];

export default function RegisterPage() {
  const router = useRouter();
  const toast = useToast();
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const strength = passwordStrength(password);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const parsed = registerSchema.safeParse({
      name: form.get('name') ?? '',
      email: form.get('email') ?? '',
      password: form.get('password') ?? '',
      confirm: form.get('confirm') ?? '',
      terms: form.get('terms') === 'on',
    });
    if (!parsed.success) return setErrors(fieldErrors(parsed.error));

    setBusy(true);
    const result = await register(parsed.data);
    setBusy(false);
    if (!result.ok) return setErrors({ email: result.error });
    router.replace('/login');
  }

  const soon = (e: React.MouseEvent) => {
    e.preventDefault();
    toast('Halaman ini belum tersedia di pratinjau.');
  };

  return (
    <AuthShell>
      <h1 className=" text-[30px] font-bold leading-tight tracking-tight">Buat akun baru</h1>
      <p className="mt-2.5 text-[15px] text-muted">
        Mulai audit kualitas User Story Anda dengan standar ISO 29148 dan INVEST.
      </p>

      <form onSubmit={onSubmit} noValidate className="mt-7 space-y-4">
        <TextField label="Nama" name="name" autoComplete="name" placeholder="Nama lengkap Anda" error={errors.name} />
        <TextField
          label="Email"
          name="email"
          type="email"
          autoComplete="email"
          placeholder="nama@perusahaan.com"
          error={errors.email}
        />
        <PasswordField
          label="Kata Sandi"
          name="password"
          autoComplete="new-password"
          placeholder="Minimal 8 karakter"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={errors.password}
        >
          <div className="mt-3 grid grid-cols-4 gap-1.5" aria-hidden>
            {[1, 2, 3, 4].map((i) => (
              <span
                key={i}
                className={`h-1 rounded-full transition-colors ${i <= strength ? STRENGTH_COLOR[strength] : 'bg-line/[0.08]'}`}
              />
            ))}
          </div>
          <p className="mt-2 text-[12px] text-muted">Gunakan huruf, angka, dan simbol</p>
        </PasswordField>
        <PasswordField
          label="Konfirmasi Kata Sandi"
          name="confirm"
          autoComplete="new-password"
          placeholder="Ulangi kata sandi Anda"
          error={errors.confirm}
        />

        <div>
          <label className="flex cursor-pointer items-center gap-3 text-[13.5px] text-muted">
            <input
              type="checkbox"
              name="terms"
              className="h-5 w-5 shrink-0 cursor-pointer rounded-md border border-line/20 accent-[rgb(var(--btn))]"
            />
            <span>
              Saya menyetujui{' '}
              <a href="#" onClick={soon} className="text-accent hover:underline">
                Ketentuan Layanan
              </a>{' '}
              dan{' '}
              <a href="#" onClick={soon} className="text-accent hover:underline">
                Kebijakan Privasi
              </a>
            </span>
          </label>
          {errors.terms && <p className="mt-1.5 text-[12.5px] text-rose-600 dark:text-rose-400">{errors.terms}</p>}
        </div>

        <button type="submit" disabled={busy} className="btn-primary relative h-[52px] w-full text-[16px]">
          Daftar
          <ArrowRight size={18} className="absolute right-5" aria-hidden />
        </button>
      </form>

      <p className="mt-6 text-center text-[14px] text-muted">
        Sudah punya akun?{' '}
        <Link href="/login" className="font-semibold text-accent hover:underline">
          Masuk
        </Link>
      </p>
    </AuthShell>
  );
}
