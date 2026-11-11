import { describe, expect, it } from 'vitest';
import { buildHistoryRows, rowGrade, rowScore } from './history';
import type { Audit } from './audits';

/** P0.1/R3-1 regression: PROCESSING/FAILED history states must never show the
 * placeholder skor 0.0 as a real evaluation; COMPLETED/PARTIAL keep real scores. */
function audit(overrides: Partial<Audit>): Audit {
  return {
    id: '1',
    seq: 1,
    createdAt: '2026-11-12T00:00:00Z',
    title: 'Login cepat',
    text: 'Login cepat',
    language: 'id',
    ...overrides,
  } as Audit;
}

describe('buildHistoryRows — P0.1/R3-1', () => {
  it('PROCESSING is a pending state, never "0 · Poor"', () => {
    const [row] = buildHistoryRows([audit({ backendStatus: 'PROCESSING', backendScore: 0 })]);
    expect(row.pendingStatus).toBe('PROCESSING');
    expect(row.backend).toBeNull();
    expect(row.result).toBeNull();
    expect(rowGrade(row)).toBeNull(); // tidak ikut filter grade
    expect(rowScore(row)).toBe(0); // hanya untuk sorting (mengumpul di bawah)
  });

  it('FAILED is a pending/failed state, not a score', () => {
    const [row] = buildHistoryRows([audit({ backendStatus: 'FAILED', backendScore: 0 })]);
    expect(row.pendingStatus).toBe('FAILED');
    expect(row.backend).toBeNull();
    expect(rowGrade(row)).toBeNull();
  });

  it('COMPLETED preserves the real persisted backend score', () => {
    const [row] = buildHistoryRows([audit({ backendStatus: 'COMPLETED', backendScore: 82.4 })]);
    expect(row.pendingStatus).toBeNull();
    expect(row.backend?.score).toBe(82);
    expect(row.backend?.status).toBe('COMPLETED');
    expect(row.result).toBeNull();
  });

  it('PARTIAL keeps its real Stage-1 score', () => {
    const [row] = buildHistoryRows([audit({ backendStatus: 'PARTIAL', backendScore: 65 })]);
    expect(row.pendingStatus).toBeNull();
    expect(row.backend?.score).toBe(65);
  });

  it('local offline audits are evaluated by the local engine', () => {
    const [row] = buildHistoryRows([audit({ text: 'Sebagai user, saya ingin data aman agar tenang.' })]);
    expect(row.pendingStatus).toBeNull();
    expect(row.backend).toBeNull();
    expect(row.result).not.toBeNull();
    expect(rowScore(row)).toBeGreaterThanOrEqual(0);
  });

  it('legacy cached backend items without status still show their score', () => {
    const [row] = buildHistoryRows([audit({ backendScore: 90 })]);
    expect(row.pendingStatus).toBeNull();
    expect(row.backend?.score).toBe(90);
  });
});
