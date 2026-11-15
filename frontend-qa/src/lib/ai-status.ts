import type { BackendAuditDetail } from './api';
import { translations, type UILocale } from './i18n';

/**
 * P0.1/R3-2: status transparan untuk saran tahap AI (Stage-2).
 * Membedakan: hasil provider nyata / contoh mock / gagal-tidak-tersedia /
 * belum tersedia — tanpa mengekspos detail error internal ke pengguna.
 * Task 09: label & penjelasan mengikuti locale UI.
 */
export type AiSuggestionKind = 'mock' | 'provider' | 'unavailable' | 'none';

export interface AiSuggestionStatus {
  kind: AiSuggestionKind;
  /** Label pendek untuk pill/status di UI. */
  shortLabel: string;
  /** Penjelasan satu kalimat untuk pengguna (tanpa detail internal). */
  explanation: string;
}

function tr(locale: UILocale, key: string): string {
  return translations[key]?.[locale] ?? translations[key]?.['id'] ?? key;
}

export function resolveAiSuggestionStatus(
  detail: Pick<BackendAuditDetail, 'ai_suggestion_source' | 'status_audit' | 'stage2_status'>,
  locale: UILocale = 'id',
): AiSuggestionStatus {
  if (detail.ai_suggestion_source === 'mock') {
    return {
      kind: 'mock',
      shortLabel: tr(locale, 'ai_status.mock_label'),
      explanation: tr(locale, 'ai_status.mock_desc'),
    };
  }
  if (detail.ai_suggestion_source === 'provider') {
    return {
      kind: 'provider',
      shortLabel: tr(locale, 'ai_status.provider_label'),
      explanation: tr(locale, 'ai_status.provider_desc'),
    };
  }
  if (detail.status_audit === 'PARTIAL' || detail.status_audit === 'FAILED' || detail.stage2_status === 'FAILED') {
    return {
      kind: 'unavailable',
      shortLabel: tr(locale, 'ai_status.unavailable_label'),
      explanation: tr(locale, 'ai_status.unavailable_desc'),
    };
  }
  return {
    kind: 'none',
    shortLabel: tr(locale, 'ai_status.none_label'),
    explanation: tr(locale, 'ai_status.none_desc'),
  };
}
