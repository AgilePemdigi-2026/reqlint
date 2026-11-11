'use client';

import { ArrowRight, CheckCircle2, Mail } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';
import { TextField } from '@/components/auth/fields';
import { LandingFooter } from '@/components/landing/footer';
import { LandingNav } from '@/components/landing/landing-nav';
import { CONTACT_MAX, contactSchema, fieldErrors } from '@/lib/validation';

export default function ContactPage() {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const parsed = contactSchema.safeParse({
      name: form.get('name') ?? '',
      email: form.get('email') ?? '',
      subject: form.get('subject') ?? '',
      message: form.get('message') ?? '',
    });
    if (!parsed.success) return setErrors(fieldErrors(parsed.error));
    setErrors({});

    setBusy(true);
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsed.data),
      });
      if (res.status === 422) {
        const data = (await res.json()) as { errors?: Record<string, string> };
        return setErrors(data.errors ?? { form: 'Data tidak valid.' });
      }
      if (!res.ok) throw new Error('request failed');
      setSent(true);
    } catch {
      setErrors({ form: 'Pesan gagal dikirim. Periksa koneksi Anda lalu coba lagi.' });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#f7f5f1] dark:bg-[#141416]">
      <LandingNav />
      <main className="mx-auto grid max-w-[1100px] gap-10 px-5 pb-24 pt-14 lg:grid-cols-[1fr_520px] lg:gap-16 lg:pt-20">
        <div>
          <p className="eyebrow">Hubungi Kami</p>
          <h1 className="mt-3 text-[38px] font-medium leading-[1.08] tracking-[-0.03em] sm:text-[48px]">
            Ada pertanyaan atau masukan?
          </h1>
          <p className="mt-5 max-w-[460px] text-[17px] leading-[1.7] text-ink/60">
            Ceritakan kendala, saran fitur, atau pertanyaan Anda tentang ReqLint. Kami akan membalas melalui email yang Anda
            isi.
          </p>
          <p className="mt-8 inline-flex items-center gap-2.5 text-[15px] text-ink/70">
            <Mail size={18} aria-hidden /> support@reqlint.app
          </p>
        </div>

        <div className="card p-7 sm:p-9">
          {sent ? (
            <div className="py-6 text-center" role="status">
              <CheckCircle2 size={40} strokeWidth={1.5} className="mx-auto text-emerald-600" aria-hidden />
              <h2 className="mt-4 text-[22px] font-medium">Pesan terkirim</h2>
              <p className="mt-2 text-[14.5px] text-muted">Terima kasih. Kami akan membalas secepatnya melalui email Anda.</p>
              <Link href="/" className="btn-ghost mt-7 h-11 px-6 text-[14px]">
                Kembali ke beranda
              </Link>
            </div>
          ) : (
            <form onSubmit={onSubmit} noValidate className="space-y-5">
              <TextField label="Nama" name="name" autoComplete="name" placeholder="Nama lengkap Anda" error={errors.name} />
              <TextField
                label="Email"
                name="email"
                type="email"
                autoComplete="email"
                placeholder="nama@perusahaan.com"
                error={errors.email}
              />
              <TextField label="Subjek" name="subject" placeholder="Topik pesan Anda" error={errors.subject} />
              <div>
                <label htmlFor="contact-message" className="label">
                  Pesan
                </label>
                <textarea
                  id="contact-message"
                  name="message"
                  rows={6}
                  maxLength={CONTACT_MAX}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  aria-invalid={!!errors.message}
                  placeholder="Tulis pesan Anda di sini…"
                  className={`field h-auto resize-y py-3 leading-relaxed ${
                    errors.message ? 'border-rose-400/70 focus:border-rose-400 focus:ring-rose-400/15' : ''
                  }`}
                />
                <div className="mt-1.5 flex justify-between text-[12.5px]">
                  <span className="text-rose-600 dark:text-rose-400">{errors.message}</span>
                  <span className="text-muted">
                    {message.length}/{CONTACT_MAX}
                  </span>
                </div>
              </div>

              {errors.form && (
                <p role="alert" className="rounded-2xl bg-rose-50 px-4 py-3 text-[13.5px] text-rose-700 dark:bg-rose-400/10 dark:text-rose-300">
                  {errors.form}
                </p>
              )}

              <button type="submit" disabled={busy} className="btn-primary relative h-[52px] w-full text-[16px]">
                {busy ? 'Mengirim…' : 'Kirim pesan'}
                <ArrowRight size={18} className="absolute right-5" aria-hidden />
              </button>
            </form>
          )}
        </div>
      </main>
      <LandingFooter />
    </div>
  );
}