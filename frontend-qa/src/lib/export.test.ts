import { describe, expect, it } from 'vitest';
import { buildExport, toMarkdown, toJson } from './export';
import { analyze } from './analyzer';

const story = 'Sebagai admin, saya ingin menghapus data dengan cepat agar hemat waktu.';
const result = analyze(story, 'id');
const revision = { text: story, changed: false, result, originalLocal: result };
const audit = {
  id: '1',
  seq: 1,
  title: 'Login cepat',
  text: story,
  createdAt: '2026-11-15T00:00:00Z',
  language: 'id' as const,
};

const meta = {
  evaluator: 'traditional_ml',
  modelVersion: '2.1.0-srs-hybrid',
  aiInvestNotes: { negotiable: false, testable: true },
};

describe('export integrity — Task 07 (evaluator identity & advisory separation)', () => {
  it('markdown export includes evaluator identity + model version', () => {
    const md = toMarkdown(audit, result, revision, meta);
    expect(md).toContain('Evaluator: **traditional_ml (model: 2.1.0-srs-hybrid)**');
  });

  it('markdown export uses honest heuristic label, not an ISO compliance claim', () => {
    const md = toMarkdown(audit, result, revision, meta);
    expect(md).toContain('Praktik dokumen (heuristik)');
    expect(md).not.toContain('Kepatuhan: ISO 29148');
  });

  it('markdown export separates AI advisory notes from evaluator findings', () => {
    const md = toMarkdown(audit, result, revision, meta);
    expect(md).toContain('## Catatan AI (advisory — bukan findings evaluator)');
    expect(md).toContain('negotiable: LLM menandai perlu perhatian');
    expect(md).toContain('testable: lolos menurut LLM');
  });

  it('json export carries evaluator, model_version and ai_advisory_notes as separate keys', () => {
    const parsed = JSON.parse(toJson(audit, result, revision, meta));
    expect(parsed.evaluator).toBe('traditional_ml');
    expect(parsed.model_version).toBe('2.1.0-srs-hybrid');
    expect(parsed.ai_advisory_notes).toEqual({ negotiable: false, testable: true });
    expect(parsed.result.findings).toBeDefined();
  });

  it('without meta, exports make no evaluator claims', () => {
    const md = toMarkdown(audit, result, revision);
    expect(md).not.toContain('Evaluator:');
    const parsed = JSON.parse(toJson(audit, result, revision));
    expect(parsed.evaluator).toBeNull();
    expect(parsed.ai_advisory_notes).toBeNull();
  });

  it('buildExport passes meta through for md and json', () => {
    const md = buildExport('md', audit, result, revision, meta);
    expect(md.content).toContain('Evaluator: **traditional_ml');
    const js = buildExport('json', audit, result, revision, meta);
    expect(JSON.parse(js.content).evaluator).toBe('traditional_ml');
    expect(js.filename).toBe('1.json');
  });

  it('result findings remain the evaluator findings (advisory never merged in)', () => {
    const md = toMarkdown(audit, result, revision, meta);
    const findingsSection = md.split('## Catatan AI')[0];
    expect(findingsSection).toContain('## Temuan Cacat');
    // advisory lines must appear only after the findings section
    expect(md.indexOf('Catatan AI')).toBeGreaterThan(md.indexOf('## Temuan Cacat'));
  });
});
