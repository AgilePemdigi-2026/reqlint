import { describe, expect, it } from 'vitest';
import { resolveAiSuggestionStatus } from './ai-status';

/** P0.1/R3-2 regression: mock, provider, failure dan belum-tersedia harus
 * terbedakan dengan jelas; tidak ada detail error internal yang bocor. */
describe('resolveAiSuggestionStatus', () => {
  it('mock suggestions are labeled as demo, never as real AI output', () => {
    const s = resolveAiSuggestionStatus({ ai_suggestion_source: 'mock', status_audit: 'COMPLETED', stage2_status: 'DONE' });
    expect(s.kind).toBe('mock');
    expect(s.shortLabel).toMatch(/mock|demo/i);
    expect(s.explanation).toMatch(/bukan hasil model AI/i);
  });

  it('provider output is labeled as AI-generated', () => {
    const s = resolveAiSuggestionStatus({ ai_suggestion_source: 'provider', status_audit: 'COMPLETED', stage2_status: 'DONE' });
    expect(s.kind).toBe('provider');
    expect(s.explanation).toMatch(/model bahasa/i);
  });

  it('failed Stage-2 becomes unavailable with generic messaging (no internal error details)', () => {
    const cases = [
      { ai_suggestion_source: null, status_audit: 'PARTIAL', stage2_status: 'FAILED' },
      { ai_suggestion_source: null, status_audit: 'FAILED', stage2_status: 'FAILED' },
      { ai_suggestion_source: null, status_audit: 'COMPLETED', stage2_status: 'FAILED' },
    ] as const;
    for (const c of cases) {
      const s = resolveAiSuggestionStatus(c);
      expect(s.kind).toBe('unavailable');
      expect(s.explanation).toMatch(/Analisis Ulang/i);
      // Tidak ada cuplikan error internal/stack dalam penjelasan.
      expect(s.explanation.length).toBeLessThan(200);
    }
  });

  it('pending audits report that suggestions are not yet available', () => {
    const s = resolveAiSuggestionStatus({ ai_suggestion_source: null, status_audit: 'PROCESSING', stage2_status: 'PENDING' });
    expect(s.kind).toBe('none');
    expect(s.explanation).toMatch(/belum tersedia/i);
  });
});
