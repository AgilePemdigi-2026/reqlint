'use client';

import { suggestTitle, type Language } from './analyzer';
import { createLocalStore, useHydrated } from './store';

/**
 * Hanya teks sumber yang disimpan. Hasil audit selalu dihitung ulang dari teks
 * (analisis murah & deterministik), sehingga tidak ada data turunan yang basi.
 */
export interface Audit {
  id: string; // AUD-101, AUD-102, ... atau ID numerik backend (1, 2, ...)
  seq: number;
  createdAt: string; // ISO
  title: string;
  text: string;
  language: Language;
  /** P0/FUNC-06: skor tersimpan dari backend untuk item riwayat backend
   * (null selama audit masih PROCESSING). Item lokal tidak memiliki ini. */
  backendScore?: number | null;
  backendStatus?: string | null;
}

export interface Draft {
  text: string;
  language: Language;
}

export const SAMPLE_DRAFT: Draft = {
  language: 'id',
  text: 'Sebagai user, saya ingin proses login sistem berjalan dengan sangat cepat dan user-friendly agar tidak membuang waktu.\nData sesi pengguna harus disimpan oleh sistem.',
};

const auditsStore = createLocalStore<Audit[]>('reqlint.audits', []);
const draftStore = createLocalStore<Draft>('reqlint.draft', SAMPLE_DRAFT);
const tipStore = createLocalStore<boolean>('reqlint.tip-dismissed', false);

export const FIRST_SEQ = 101;

/** Buat audit baru, atau pakai ulang audit terbaru bila teks & bahasa identik. */
export function createAudit(text: string, language: Language, customId?: string): Audit {
  const all = auditsStore.get();
  const latest = all[0];
  if (latest && latest.text === text && latest.language === language && (!customId || latest.id === customId)) return latest;
  const seq = all.reduce((max, a) => Math.max(max, a.seq), FIRST_SEQ - 1) + 1;
  const audit: Audit = {
    id: customId || `AUD-${seq}`,
    seq,
    createdAt: new Date().toISOString(),
    title: suggestTitle(text, language),
    text,
    language,
  };
  // Hindari duplikasi ID
  auditsStore.set([audit, ...all.filter((a) => a.id !== audit.id)]);
  return audit;
}

export function syncAudits(items: Audit[]) {
  const current = auditsStore.get();
  const existingIds = new Set(current.map((a) => a.id));
  const newItems = items.filter((item) => !existingIds.has(item.id));
  if (newItems.length > 0) {
    auditsStore.set([...newItems, ...current]);
  }
}

export function touchAudit(id: string) {
  auditsStore.set(auditsStore.get().map((a) => (a.id === id ? { ...a, createdAt: new Date().toISOString() } : a)));
}

export function deleteAudit(id: string) {
  auditsStore.set(auditsStore.get().filter((a) => a.id !== id));
}

export function clearAudits() {
  auditsStore.set([]);
}

export function useAudits(): Audit[] {
  return auditsStore.useValue();
}

/** undefined = belum hidrasi, null = tidak ditemukan. */
export function useAudit(id: string): Audit | null | undefined {
  const hydrated = useHydrated();
  const audits = auditsStore.useValue();
  if (!hydrated) return undefined;
  return audits.find((a) => a.id === id) ?? null;
}

export const useDraft = () => draftStore.useValue();
export const setDraft = (draft: Draft) => draftStore.set(draft);
export const useTipDismissed = () => tipStore.useValue();
export const dismissTip = () => tipStore.set(true);
