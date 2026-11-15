import { z } from 'zod';
import { getUILocale, type UILocale } from './i18n';

export const MAX_CHARS = 20_000;

const messages: Record<string, { id: string; en: string }> = {
  email_required: { id: 'Email wajib diisi.', en: 'Email is required.' },
  email_invalid: { id: 'Format email tidak valid.', en: 'Email format is invalid.' },
  password_required: { id: 'Kata sandi wajib diisi.', en: 'Password is required.' },
  name_min: { id: 'Nama minimal 2 karakter.', en: 'Name must be at least 2 characters.' },
  name_max: { id: 'Nama terlalu panjang.', en: 'Name is too long.' },
  password_min: { id: 'Kata sandi minimal 8 karakter.', en: 'Password must be at least 8 characters.' },
  password_letter: { id: 'Kata sandi harus memuat minimal 1 huruf.', en: 'Password must contain at least 1 letter.' },
  password_digit: { id: 'Kata sandi harus memuat minimal 1 angka.', en: 'Password must contain at least 1 digit.' },
  confirm_required: { id: 'Konfirmasi kata sandi wajib diisi.', en: 'Password confirmation is required.' },
  terms_required: { id: 'Anda harus menyetujui ketentuan layanan.', en: 'You must agree to the terms of service.' },
  confirm_mismatch: { id: 'Konfirmasi kata sandi tidak cocok.', en: 'Password confirmation does not match.' },
  text_required: { id: 'Teks tidak boleh kosong.', en: 'Text cannot be empty.' },
  text_too_long: { id: 'Teks terlalu panjang (maks. 50.000 karakter).', en: 'Text is too long (max 50,000 characters).' },
};

function msg(key: string, locale: UILocale): string {
  return messages[key]?.[locale] ?? messages[key]?.id ?? key;
}

export function loginSchema(locale: UILocale = getUILocale()) {
  return z.object({
    email: z.string().trim().min(1, msg('email_required', locale)).email(msg('email_invalid', locale)),
    password: z.string().min(1, msg('password_required', locale)),
  });
}

export function registerSchema(locale: UILocale = getUILocale()) {
  return z
    .object({
      name: z.string().trim().min(2, msg('name_min', locale)).max(60, msg('name_max', locale)),
      email: z.string().trim().min(1, msg('email_required', locale)).email(msg('email_invalid', locale)),
      password: z
        .string()
        .min(8, msg('password_min', locale))
        .regex(/[A-Za-z]/, msg('password_letter', locale))
        .regex(/\d/, msg('password_digit', locale)),
      confirm: z.string().min(1, msg('confirm_required', locale)),
      terms: z.literal(true, { message: msg('terms_required', locale) }),
    })
    .refine((v) => v.password === v.confirm, { path: ['confirm'], message: msg('confirm_mismatch', locale) });
}

export function analyzeRequestSchema(locale: UILocale = getUILocale()) {
  return z.object({
    text: z.string().min(1, msg('text_required', locale)).max(50_000, msg('text_too_long', locale)),
    language: z.enum(['id', 'en']).default('id'),
  });
}

/** Ambil pesan error pertama per field dari ZodError. */
export function fieldErrors(error: z.ZodError): Record<string, string> {
  const out: Record<string, string> = {};
  for (const issue of error.issues) {
    const key = String(issue.path[0] ?? '_');
    if (!out[key]) out[key] = issue.message;
  }
  return out;
}

/** Skor kekuatan kata sandi 0–4 (panjang, huruf besar+kecil, angka, simbol). */
export function passwordStrength(password: string): number {
  if (!password) return 0;
  let s = 0;
  if (password.length >= 8) s++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) s++;
  if (/\d/.test(password)) s++;
  if (/[^A-Za-z0-9]/.test(password)) s++;
  return s;
}
