import { describe, expect, it } from 'vitest';
import { adaptBackendAuditToAnalysisResult } from './adapter';
import { analyze } from './analyze';
import type { BackendAuditDetail } from '../api';

/**
 * P0 regression tests (FUNC-05, UI-47, UI-48, FUNC-12):
 * - the "after revision" result must be a REAL evaluation, never fabricated;
 * - missing INVEST breakdown values must be "not evaluated", never passing.
 */
function makeDetail(overrides: Record<string, unknown> = {}): BackendAuditDetail {
  return {
    id_audit: 1,
    id_draf: 1,
    judul_klausul: 'Login cepat',
    tipe_masukan: 'manual',
    status_audit: 'COMPLETED',
    stage2_status: 'DONE',
    status_revisi: 'BELUM_DIREVISI',
    tanggal_audit: '2026-11-12T00:00:00Z',
    scorecard: {
      skor_awal: 80,
      skor_kualitas: 80,
      breakdown: { iso_29148: {}, invest: {} },
    },
    ringkasan: { ambiguity: 0, tidak_lengkap: 0, weak_directive: 0, passive_voice: 0, total: 0 },
    temuan: [],
    rekomendasi_ai: null,
    diff: {
      original: { teks: 'Sebagai admin, saya ingin dapat menghapus data dengan mudah agar cepat.' },
      revised: { teks: 'Sebagai admin, saya ingin dapat menghapus data dengan mudah agar cepat.' },
    },
    ...overrides,
  } as unknown as BackendAuditDetail & Record<string, unknown> as BackendAuditDetail;
}

describe('adaptBackendAuditToAnalysisResult — P0 result integrity', () => {
  it('FUNC-05/UI-47: revision result is a real evaluation, not clamped to >= 90', () => {
    const worseRevised = 'Harus disimpan oleh sistem dengan cepat.'; // pasif + ambigu -> skor rendah
    const detail = makeDetail({
      diff: { original: { teks: 'Sebagai admin, saya ingin dapat menghapus data dengan mudah agar cepat.' }, revised: { teks: worseRevised } },
    });
    const { revision } = adaptBackendAuditToAnalysisResult(detail);
    const expected = analyze(worseRevised, 'id');
    expect(revision.changed).toBe(true);
    expect(revision.result.score).toBe(expected.score); // hasil nyata, bukan fabrikasi
    expect(revision.result.score).toBeLessThan(90); // tidak ada lagi patokan bawah 90
    expect(revision.result.findings.length).toBeGreaterThan(0); // findings nyata, bukan [] buatan
  });

  it('FUNC-05: unchanged revision reuses the audit result (no artificial uplift)', () => {
    const { result, revision } = adaptBackendAuditToAnalysisResult(makeDetail());
    expect(revision.changed).toBe(false);
    expect(revision.result).toBe(result);
  });

  it('UI-48: missing INVEST breakdown values are "not evaluated", never passing', () => {
    const detail = makeDetail({
      scorecard: {
        skor_awal: 80,
        skor_kualitas: 80,
        breakdown: {
          iso_29148: {},
          invest: { independent: null, negotiable: null, valuable: null, estimable: null, small: null, testable: null },
        },
      },
    });
    const { result } = adaptBackendAuditToAnalysisResult(detail);
    expect(result.invest).toHaveLength(6); // keenam kriteria INVEST tetap ada
    expect(result.invest.every((c) => c.notEvaluated)).toBe(true);
    expect(result.invest.every((c) => !c.passed)).toBe(true);
    expect(result.compliance.invest).toBeNull(); // bukan 100%, bukan 0%
  });

  it('FUNC-12: explicit INVEST failures are represented as failures', () => {
    const detail = makeDetail({
      scorecard: {
        skor_awal: 80,
        skor_kualitas: 80,
        breakdown: {
          iso_29148: {},
          invest: { independent: 40, negotiable: 80, valuable: 35, estimable: 85, small: 85, testable: 20 },
        },
      },
    });
    const { result } = adaptBackendAuditToAnalysisResult(detail);
    const byKey = Object.fromEntries(result.invest.map((c) => [c.key, c]));
    expect(byKey.I.passed).toBe(false);
    expect(byKey.I.notEvaluated).toBeFalsy();
    expect(byKey.V.passed).toBe(false);
    expect(byKey.E.passed).toBe(true);
    expect(byKey.T.passed).toBe(false);
    expect(result.compliance.invest).toBe(50); // 3 lulus dari 6 ter-evaluasi
  });
});
