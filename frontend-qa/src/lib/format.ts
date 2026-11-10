import type { Category, Grade } from './analyzer';

export const CATEGORY_LABEL: Record<Category, string> = {
  ambiguity: 'Ambiguity',
  'non-testable': 'Non-Testable',
  incomplete: 'Tidak Lengkap',
  'weak-directive': 'Weak Directive',
  'passive-voice': 'Passive Voice',
};

/** Kelas warna pill per kategori (light + dark). */
export const CATEGORY_STYLE: Record<Category, string> = {
  ambiguity: 'bg-amber-100 text-amber-800 dark:bg-amber-400/15 dark:text-amber-300',
  'non-testable': 'bg-orange-100 text-orange-800 dark:bg-orange-400/15 dark:text-orange-300',
  incomplete: 'bg-rose-100 text-rose-800 dark:bg-rose-400/15 dark:text-rose-300',
  'weak-directive': 'bg-violet-100 text-violet-800 dark:bg-violet-400/15 dark:text-violet-300',
  'passive-voice': 'bg-line/[0.06] text-muted',
};

export const GRADE_LABEL: Record<Grade, string> = {
  excellent: 'Excellent',
  good: 'Good',
  'needs-improvement': 'Needs Improvement',
  poor: 'Poor',
};

export const GRADE_TAGLINE: Record<Grade, string> = {
  excellent: 'Kebutuhan sudah jelas dan terukur.',
  good: 'Hampir siap — poles beberapa istilah.',
  'needs-improvement': 'Kejelasan dimulai dari kebutuhan yang baik.',
  poor: 'Perjelas istilah utama sebelum masuk pengembangan.',
};

export const GRADE_COLOR: Record<Grade, string> = {
  excellent: '#22a559',
  good: '#22a559',
  'needs-improvement': '#f59e0b',
  poor: '#ef4444',
};

export const GRADE_BADGE: Record<Grade, string> = {
  excellent: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-400/15 dark:text-emerald-300',
  good: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-400/15 dark:text-emerald-300',
  'needs-improvement': 'bg-amber-100 text-amber-800 dark:bg-amber-400/15 dark:text-amber-300',
  poor: 'bg-rose-100 text-rose-800 dark:bg-rose-400/15 dark:text-rose-300',
};

export function formatDate(iso: string, locale: 'id' | 'en' = 'id'): string {
  const loc = locale === 'en' ? 'en-US' : 'id-ID';
  return new Date(iso).toLocaleDateString(loc, { day: '2-digit', month: 'short', year: 'numeric' });
}
