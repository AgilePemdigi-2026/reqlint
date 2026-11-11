import type { BackendAuditDetail } from './api';

/**
 * P0.1/R3-2: status transparan untuk saran tahap AI (Stage-2).
 * Membedakan: hasil provider nyata / contoh mock / gagal-tidak-tersedia /
 * belum tersedia — tanpa mengekspos detail error internal ke pengguna.
 */
export type AiSuggestionKind = 'mock' | 'provider' | 'unavailable' | 'none';

export interface AiSuggestionStatus {
  kind: AiSuggestionKind;
  /** Label pendek untuk pill/status di UI. */
  shortLabel: string;
  /** Penjelasan satu kalimat untuk pengguna (tanpa detail internal). */
  explanation: string;
}

export function resolveAiSuggestionStatus(
  detail: Pick<BackendAuditDetail, 'ai_suggestion_source' | 'status_audit' | 'stage2_status'>
): AiSuggestionStatus {
  if (detail.ai_suggestion_source === 'mock') {
    return {
      kind: 'mock',
      shortLabel: 'Contoh demo (mock)',
      explanation:
        'Saran revisi & acceptance criteria berupa contoh generik bawaan (mode demo) — bukan hasil model AI. Konfigurasikan provider AI untuk mendapatkan saran nyata.',
    };
  }
  if (detail.ai_suggestion_source === 'provider') {
    return {
      kind: 'provider',
      shortLabel: 'Dihasilkan model AI',
      explanation:
        'Saran revisi & acceptance criteria dihasilkan model bahasa yang dikonfigurasi di server ReqLint (bisa berupa provider eksternal).',
    };
  }
  if (detail.status_audit === 'PARTIAL' || detail.status_audit === 'FAILED' || detail.stage2_status === 'FAILED') {
    return {
      kind: 'unavailable',
      shortLabel: 'Saran AI tidak tersedia',
      explanation: 'Tahap AI gagal dijalankan untuk audit ini. Gunakan tombol Analisis Ulang untuk mencoba kembali.',
    };
  }
  return {
    kind: 'none',
    shortLabel: 'Saran AI belum tersedia',
    explanation: 'Saran AI belum tersedia untuk audit ini.',
  };
}
