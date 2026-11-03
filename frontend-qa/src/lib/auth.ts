'use client';

import { createLocalStore, useHydrated } from './store';

/**
 * AUTH DEMO — hanya untuk pratinjau.
 * Akun dan sesi disimpan di localStorage browser ini, BUKAN autentikasi sungguhan.
 * Untuk produksi, ganti isi berkas ini dengan Auth.js / provider lain (antarmuka fungsi dipertahankan).
 */
export interface User {
  name: string;
  email: string;
  passwordHash: string;
}

const usersStore = createLocalStore<User[]>('reqlint.users', []);
const sessionStore = createLocalStore<string | null>('reqlint.session', null);

export const DEMO_ACCOUNT = { name: 'Fajar Akbar', email: 'demo@reqlint.app', password: 'demo12345' };

async function hashPassword(email: string, password: string): Promise<string> {
  const input = `${email.toLowerCase()}:${password}`;
  if (typeof crypto !== 'undefined' && crypto.subtle) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(input));
    return Array.from(new Uint8Array(buf), (b) => b.toString(16).padStart(2, '0')).join('');
  }
  return `plain:${input}`; // konteks non-HTTPS: tidak ada crypto.subtle
}

type Result = { ok: true } | { ok: false; error: string };

export async function register(input: { name: string; email: string; password: string }): Promise<Result> {
  const email = input.email.trim().toLowerCase();
  if (usersStore.get().some((u) => u.email === email)) {
    return { ok: false, error: 'Email ini sudah terdaftar. Silakan masuk.' };
  }
  const user: User = { name: input.name.trim(), email, passwordHash: await hashPassword(email, input.password) };
  usersStore.set([...usersStore.get(), user]);
  return { ok: true };
}

export async function login(emailInput: string, password: string): Promise<Result> {
  const email = emailInput.trim().toLowerCase();
  const user = usersStore.get().find((u) => u.email === email);
  if (!user || user.passwordHash !== (await hashPassword(email, password))) {
    return { ok: false, error: 'Email atau kata sandi salah.' };
  }
  sessionStore.set(email);
  return { ok: true };
}

export async function loginDemo(): Promise<void> {
  const email = DEMO_ACCOUNT.email;
  if (!usersStore.get().some((u) => u.email === email)) {
    usersStore.set([
      ...usersStore.get(),
      { name: DEMO_ACCOUNT.name, email, passwordHash: await hashPassword(email, DEMO_ACCOUNT.password) },
    ]);
  }
  sessionStore.set(email);
}

export function logout() {
  sessionStore.set(null);
}

/** undefined = belum hidrasi, null = belum login. */
export function useCurrentUser(): User | null | undefined {
  const hydrated = useHydrated();
  const users = usersStore.useValue();
  const session = sessionStore.useValue();
  if (!hydrated) return undefined;
  return users.find((u) => u.email === session) ?? null;
}

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  return ((parts[0]?.[0] ?? '') + (parts.length > 1 ? parts[parts.length - 1][0] : '')).toUpperCase() || '?';
}
