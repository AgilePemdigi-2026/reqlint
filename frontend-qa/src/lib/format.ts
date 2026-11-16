import type { Category, Grade } from './analyzer';
import { translations, type UILocale } from './i18n';

/** Terjemahan langsung dari kamus i18n (fallback id → key). */
function tr(locale: UILocale, key: string): string {
  return translations[key]?.[locale] ?? translations[key]?.['id'] ?? key;
}

/** Task 09: label kategori temuan mengikuti locale UI (dulu ID statis). */
export function categoryLabel(cat: Category, locale: UILocale = 'id'): string {
  return tr(locale, `category.${cat}`);
}

/** Task 09: label kategori sebagai fungsi t() — untuk pemakaian di komponen. */
export function categoryLabelT(cat: Category, t: (key: string) => string): string {
  return t(`category.${cat}`);
}

/** Task 09: label grade & tagline mengikuti locale UI. */
export function gradeLabel(grade: Grade, locale: UILocale = 'id'): string {
  return tr(locale, `grade.${grade}`);
}

export function gradeTagline(grade: Grade, locale: UILocale = 'id'): string {
  return tr(locale, `tagline.${grade}`);
}

/** Kelas warna pill per kategori (light + dark). */
export const CATEGORY_STYLE: Record<Category, string> = {
  ambiguity: 'bg-amber-100 text-amber-800 dark:bg-amber-400/15 dark:text-amber-300',
  'non-testable': 'bg-orange-100 text-orange-800 dark:bg-orange-400/15 dark:text-orange-300',
  incomplete: 'bg-rose-100 text-rose-800 dark:bg-rose-400/15 dark:text-rose-300',
  'weak-directive': 'bg-violet-100 text-violet-800 dark:bg-violet-400/15 dark:text-violet-300',
  'passive-voice': 'bg-line/[0.06] text-muted',
};

/** Label warna grade (light + dark). */
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

/** Tanggal mengikuti locale UI (dulu selalu id-ID). */
export function formatDate(iso: string, locale: UILocale = 'id'): string {
  return new Date(iso).toLocaleDateString(locale === 'en' ? 'en-GB' : 'id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}
