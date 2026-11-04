'use client';

import axios from 'axios';
import {
  apiGetMe,
  apiLogin,
  apiRegister,
  extractApiError,
  type AuthUserData,
} from './api';
import { createLocalStore, useHydrated } from './store';

export interface User {
  id_user?: number;
  name: string;
  email: string;
  tanggal_registrasi?: string | null;
}

export interface AuthSession {
  token: string;
  user: User;
}

const sessionStore = createLocalStore<AuthSession | null>('reqlint.auth_session', null);

export const DEMO_ACCOUNT = {
  name: 'Fajar Akbar',
  email: 'demo@reqlint.app',
  password: 'demo12345',
};

export type Result = { ok: true; user?: User } | { ok: false; error: string; field?: string };

/** Mendaftarkan akun baru ke backend FastAPI lalu langsung melakukan autentikasi login. */
export async function register(input: {
  name: string;
  email: string;
  password: string;
  confirm?: string;
}): Promise<Result> {
  const name = input.name.trim();
  const email = input.email.trim().toLowerCase();
  const password = input.password;
  const password_confirmation = input.confirm ?? password;

  try {
    // 1. Panggil registrasi ke backend
    await apiRegister({
      name,
      email,
      password,
      password_confirmation,
    });

    // 2. Otomatis login untuk mendapatkan JWT Token
    return await login(email, password);
  } catch (err) {
    const error = extractApiError(err);
    return {
      ok: false,
      error: error.message,
      field: error.field === 'password_confirmation' ? 'confirm' : error.field,
    };
  }
}

/** Melakukan login kredensial ke backend FastAPI dan menyimpan sesi JWT. */
export async function login(emailInput: string, passwordInput: string): Promise<Result> {
  const email = emailInput.trim().toLowerCase();
  const password = passwordInput;

  try {
    const res = await apiLogin({ email, password });
    if (!res.data || !res.data.access_token) {
      return { ok: false, error: 'Respons login tidak memuat token akses.' };
    }

    const session: AuthSession = {
      token: res.data.access_token,
      user: {
        id_user: res.data.user.id_user,
        name: res.data.user.name,
        email: res.data.user.email,
        tanggal_registrasi: res.data.user.tanggal_registrasi,
      },
    };

    sessionStore.set(session);
    return { ok: true, user: session.user };
  } catch (err) {
    const error = extractApiError(err);
    return { ok: false, error: error.message, field: error.field };
  }
}

/** Masuk dengan akun demo, otomatis membuat akun di backend bila belum ada. */
export async function loginDemo(): Promise<Result> {
  // Coba login terlebih dahulu
  const loginRes = await login(DEMO_ACCOUNT.email, DEMO_ACCOUNT.password);
  if (loginRes.ok) return loginRes;

  // Jika akun demo belum terdaftar di database server, daftarkan otomatis
  const regRes = await register({
    name: DEMO_ACCOUNT.name,
    email: DEMO_ACCOUNT.email,
    password: DEMO_ACCOUNT.password,
    confirm: DEMO_ACCOUNT.password,
  });

  return regRes;
}

/** Mengakhiri sesi pengguna aktif dan menghapus token dari storage. */
export function logout() {
  sessionStore.set(null);
}

/** Mendapatkan token akses JWT saat ini (atau null bila belum login). */
export function getAuthToken(): string | null {
  return sessionStore.get()?.token ?? null;
}

/** Memverifikasi keabsahan sesi JWT ke endpoint GET /api/v1/auth/me di backend. */
export async function verifySession(): Promise<User | null> {
  const session = sessionStore.get();
  if (!session?.token) return null;

  try {
    const res = await apiGetMe();
    if (res.data) {
      const updatedUser: User = {
        id_user: res.data.id_user,
        name: res.data.name,
        email: res.data.email,
        tanggal_registrasi: res.data.tanggal_registrasi,
      };
      sessionStore.set({ token: session.token, user: updatedUser });
      return updatedUser;
    }
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 401) {
      // Sesi telah kedaluwarsa atau tidak valid di backend
      sessionStore.set(null);
      return null;
    }
  }
  return session.user;
}

/** Hook reaktif untuk mendapatkan data profil pengguna yang sedang login. */
export function useCurrentUser(): User | null | undefined {
  const hydrated = useHydrated();
  const session = sessionStore.useValue();
  if (!hydrated) return undefined;
  return session?.user ?? null;
}

/** Inisial 1–2 huruf untuk avatar akun. */
export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  return ((parts[0]?.[0] ?? '') + (parts.length > 1 ? parts[parts.length - 1][0] : '')).toUpperCase() || '?';
}