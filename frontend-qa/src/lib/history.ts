import { analyze, type AnalysisResult, type Grade } from '@/lib/analyzer';
// gradeFor tidak di-re-export oleh index analyzer — import langsung dari modulnya.
import { gradeFor } from '@/lib/analyzer/analyze';
import type { Audit } from './audits';

/**
 * P0.1/R3-1: baris riwayat yang membedakan tiga sumber kebenaran:
 * - `backend`   : audit backend dengan skor TERSIMPAN (COMPLETED/PARTIAL).
 * - `pendingStatus`: audit backend yang belum punya hasil evaluasi
 *   (PROCESSING / FAILED) — skor kolomnya 0.0 adalah placeholder, BUKAN hasil.
 * - `result`    : audit offline lokal yang dievaluasi mesin lokal.
 */
export type HistoryRow = {
  audit: Audit;
  backend: { score: number; grade: Grade; status: string } | null;
  pendingStatus: string | null;
  result: AnalysisResult | null;
};

const BACKEND_STATUSES_WITH_SCORE = new Set(['COMPLETED', 'PARTIAL']);

export function buildHistoryRows(audits: Audit[]): HistoryRow[] {
  return audits.map((a) => {
    // Item backend ditandai metadata sync dari backend
    // (backendStatus/backendScore). Audit lokal tidak punya keduanya.
    if (a.backendStatus != null || a.backendScore != null) {
      const status = a.backendStatus ?? null;

      // R3-1: PROCESSING/FAILED belum memiliki evaluasi — jangan tampilkan
      // skor placeholder 0.0 sebagai hasil nyata.
      if ((status != null && !BACKEND_STATUSES_WITH_SCORE.has(status)) || a.backendScore == null) {
        return { audit: a, backend: null, pendingStatus: status ?? 'PROCESSING', result: null };
      }

      const score = Math.round(a.backendScore);
      return {
        audit: a,
        backend: { score, grade: gradeFor(score, true), status: status ?? 'COMPLETED' },
        pendingStatus: null,
        result: null,
      };
    }

    // Audit offline lokal: dievaluasi mesin lokal (sumber skor yang sah).
    return {
      audit: a,
      backend: null,
      pendingStatus: null,
      result: analyze(a.text || a.title || 'User Story', a.language || 'id'),
    };
  });
}

/** Skor efektif untuk sorting. Baris pending bernilai 0 (mengumpul di bawah). */
export function rowScore(row: HistoryRow): number {
  if (row.backend) return row.backend.score;
  if (row.result) return row.result.score;
  return 0;
}

/** Grade efektif; null untuk baris pending (tidak ikut filter grade). */
export function rowGrade(row: HistoryRow): Grade | null {
  if (row.backend) return row.backend.grade;
  if (row.result) return row.result.grade;
  return null;
}
