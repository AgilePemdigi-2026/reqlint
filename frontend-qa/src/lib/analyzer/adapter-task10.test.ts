import { describe, expect, it } from 'vitest';
import { adaptBackendAuditToAnalysisResult } from './adapter';
import type { BackendAuditDetail } from '../api';

const STORY = 'As a registered customer, I want to view my order status so that I can track the delivery of my purchase.';

function mlDetail(overrides: Partial<BackendAuditDetail> = {}): BackendAuditDetail {
  return {
    id_audit: 27,
    id_draf: 27,
    judul_klausul: 'T10 traditional_ml',
    tipe_masukan: 'manual',
    evaluator: 'traditional_ml',
    requested_evaluator: 'traditional_ml',
    actual_evaluator: 'traditional_ml',
    model_version: '2.1.0-srs-hybrid',
    evaluator_error_code: null,
    evaluator_error: null,
    generation: { provider: 'openai_compatible', model: 'openai/gpt-oss-120b', status: 'FAILED', error: 'LLM_INVALID_RESPONSE: x' },
    ai_invest_notes: null,
    evaluation: {
      evaluator: 'traditional_ml',
      model_version: '2.1.0-srs-hybrid',
      verdict: 'FAIL',
      score: 66.7,
      dimensions: {
        independent: { label: 'PASS', confidence: 0.9, rationale: 'self-contained' },
        negotiable: { label: 'FAIL', confidence: 0.81, rationale: 'prescribes a specific UI layout' },
        valuable: { label: 'FAIL', confidence: 0.75, rationale: 'benefit not stated' },
        estimable: { label: 'PASS', confidence: 0.6, rationale: 'clear scope' },
        small: { label: 'PASS', confidence: 0.55, rationale: 'single capability' },
        testable: { label: 'PASS', confidence: 0.5, rationale: 'measurable' },
      },
      assessed_dimensions: CRIT,
      invest_framework_score: 66.7,
      metadata: {},
    },
    status_audit: 'PARTIAL',
    stage2_status: 'FAILED',
    status_revisi: 'BELUM_DIREVISI',
    tanggal_audit: '2026-11-16T00:00:00Z',
    scorecard: { skor_awal: 66.7, skor_kualitas: 66.7, breakdown: { evaluation: {} } },
    ringkasan: { ambiguity: 0, tidak_lengkap: 0, weak_directive: 0, passive_voice: 0, total: 0 },
    temuan: [],
    rekomendasi_ai: null,
    ai_suggestion_source: null,
    diff: { original: { teks: STORY, skor: 66.7 }, revised: { teks: STORY, skor: null } },
    notifikasi: null,
    ...overrides,
  } as BackendAuditDetail;
}

const CRIT = ['independent', 'negotiable', 'valuable', 'estimable', 'small', 'testable'];

describe('Task 10 — adapter provenance & result integrity', () => {
  it('exposes requested vs actual evaluator and the evaluation contract', () => {
    const adapted = adaptBackendAuditToAnalysisResult(mlDetail());
    expect(adapted.requestedEvaluator).toBe('traditional_ml');
    expect(adapted.actualEvaluator).toBe('traditional_ml');
    expect(adapted.evaluation?.dimensions?.negotiable?.label).toBe('FAIL');
    expect(adapted.evaluator).toBe('traditional_ml');
  });

  it('does NOT present the ML score as a document-practice (ISO) percentage', () => {
    // ML audits store their contract in breakdown; no iso_29148 map exists —
    // the adapter must report null (unknown), never substitute the score.
    const adapted = adaptBackendAuditToAnalysisResult(mlDetail());
    expect(adapted.result.compliance.iso29148).toBeNull();
    expect(adapted.result.compliance.invest).toBeNull();
    expect(adapted.result.score).toBe(67); // scorecard skor_kualitas 66.7 rounded
  });

  it('maps the six ML dimensions with labels and confidence', () => {
    const adapted = adaptBackendAuditToAnalysisResult(mlDetail());
    const invest = adapted.result.invest;
    expect(invest.map((i) => i.key)).toEqual(['I', 'N', 'V', 'E', 'S', 'T']);
    // INVEST checks from the (absent) numeric breakdown remain unevaluated —
    // the AUTHORITATIVE dimension display comes from adapted.evaluation.
    expect(invest.every((i) => i.notEvaluated)).toBe(true);
  });

  it('failed LLM audit: actual_evaluator null propagates (no fabricated provenance)', () => {
    const failed = mlDetail({
      evaluator: 'llm',
      requested_evaluator: 'llm',
      actual_evaluator: null,
      status_audit: 'FAILED',
      model_version: null,
      evaluation: null,
      scorecard: { skor_awal: null, skor_kualitas: 0.0, breakdown: { evaluator_error: {} } },
      evaluator_error_code: 'LLM_EVALUATOR_UNAVAILABLE',
      evaluator_error: { code: 'LLM_EVALUATOR_UNAVAILABLE', evaluator: 'llm', message: 'mock provider' },
      generation: null,
    });
    const adapted = adaptBackendAuditToAnalysisResult(failed);
    expect(adapted.requestedEvaluator).toBe('llm');
    expect(adapted.actualEvaluator).toBeNull();
    expect(adapted.evaluatorError?.code).toBe('LLM_EVALUATOR_UNAVAILABLE');
  });
});
