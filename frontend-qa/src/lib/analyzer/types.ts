export type Language = 'id' | 'en';

export type Category =
  | 'ambiguity'
  | 'non-testable'
  | 'incomplete'
  | 'weak-directive'
  | 'passive-voice';

export const CATEGORIES: Category[] = [
  'ambiguity',
  'non-testable',
  'incomplete',
  'weak-directive',
  'passive-voice',
];

export interface Clause {
  /** Nomor urut klausul, mulai dari 1. */
  index: number;
  text: string;
  /** Offset karakter pada teks asli (end eksklusif). */
  start: number;
  end: number;
}

export interface Finding {
  id: string;
  ruleId: string;
  /** Nomor klausul (1-based). */
  clause: number;
  category: Category;
  /** Potongan teks yang terdeteksi. */
  term: string;
  start: number;
  end: number;
  recommendation: string;
}

export type InvestKey = 'I' | 'N' | 'V' | 'E' | 'S' | 'T';

export interface InvestCheck {
  key: InvestKey;
  label: string;
  passed: boolean;
  /** P0/UI-48: true bila backend tidak menyediakan evaluasi untuk kriteria ini. */
  notEvaluated?: boolean;
  note: string;
}

export type Grade = 'excellent' | 'good' | 'needs-improvement' | 'poor';

export interface AcceptanceCriteria {
  given: string;
  when: string;
  then: string;
}

export interface AnalysisResult {
  language: Language;
  clauses: Clause[];
  wordCount: number;
  findings: Finding[];
  counts: Record<Category, number>;
  score: number;
  grade: Grade;
  /** P0/UI-48: `invest` bernilai null bila tidak ada kriteria yang ter-evaluasi. */
  compliance: { iso29148: number; invest: number | null };
  invest: InvestCheck[];
}

export interface Revision {
  text: string;
  /** True bila ada perubahan dibanding teks asli. */
  changed: boolean;
  result: AnalysisResult;
  /** P0.1/R2-1: evaluasi lokal atas TEKS ASLI dengan analyzer yang sama —
   * dipakai DiffViewer agar before/after memakai satu metode konsisten.
   * Skor audit resmi dari backend tetap ada di `AnalysisResult` hasil adaptasi
   * backend dan tidak pernah ditimpa nilai ini. */
  originalLocal: AnalysisResult;
}
