import { z } from 'zod';

export const MAX_CHARS = 20_000;

export const loginSchema = z.object({
  email: z.string().trim().min(1, 'Email wajib diisi.').email('Format email tidak valid.'),
  password: z.string().min(1, 'Kata sandi wajib diisi.'),
});

export const registerSchema = z
  .object({
    name: z.string().trim().min(2, 'Nama minimal 2 karakter.').max(60, 'Nama terlalu panjang.'),
    email: z.string().trim().min(1, 'Email wajib diisi.').email('Format email tidak valid.'),
    password: z
      .string()
      .min(8, 'Kata sandi minimal 8 karakter.')
      .regex(/[A-Za-z]/, 'Kata sandi harus memuat minimal 1 huruf.')
      .regex(/\d/, 'Kata sandi harus memuat minimal 1 angka.'),
    confirm: z.string().min(1, 'Konfirmasi kata sandi wajib diisi.'),
    terms: z.literal(true, { message: 'Anda harus menyetujui ketentuan layanan.' }),
  })
  .refine((v) => v.password === v.confirm, { path: ['confirm'], message: 'Konfirmasi kata sandi tidak cocok.' });

export const CONTACT_MAX = 2000;

export const contactSchema = z.object({
  name: z.string().trim().min(2, 'Nama minimal 2 karakter.').max(60, 'Nama terlalu panjang.'),
  email: z.string().trim().min(1, 'Email wajib diisi.').email('Format email tidak valid.'),
  subject: z.string().trim().min(3, 'Subjek minimal 3 karakter.').max(100, 'Subjek terlalu panjang.'),
  message: z
    .string()
    .trim()
    .min(10, 'Pesan minimal 10 karakter.')
    .max(CONTACT_MAX, `Pesan maksimal ${CONTACT_MAX} karakter.`),
});

export const analyzeRequestSchema = z.object({
  text: z.string().min(1, 'Teks tidak boleh kosong.').max(50_000, 'Teks terlalu panjang (maks. 50.000 karakter).'),
  language: z.enum(['id', 'en']).default('id'),
});

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
