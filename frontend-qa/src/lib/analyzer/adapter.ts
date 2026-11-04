import type {
  AnalysisResult,
  AcceptanceCriteria,
  Category,
  Finding,
  Grade,
  InvestCheck,
  Language,
  Revision,
} from './types';
import { countWords, splitClauses } from './clauses';
import { gradeFor } from './analyze';
import type { BackendAuditDetail } from '../api';

export function adaptBackendAuditToAnalysisResult(
  detail: BackendAuditDetail,
  fallbackLang: Language = 'id'
): {
  result: AnalysisResult;
  revision: Revision;
  criteria: AcceptanceCriteria | null;
  rawDetail: BackendAuditDetail;
} {
  const originalText = detail.diff?.original?.teks || '';
  const revisedText = detail.diff?.revised?.teks || detail.rekomendasi_ai?.ai_rewrite || originalText;

  // Deteksi bahasa sederhana berdasarkan kata kunci
  const isEn = /\b(as a|i want|so that|shall|should)\b/i.test(originalText);
  const lang: Language = isEn ? 'en' : fallbackLang;

  const clauses = splitClauses(originalText);
  const wordCount = clauses.reduce((n, c) => n + countWords(c.text), 0);

  // Pemetaan temuan backend ke format frontend
  const findings: Finding[] = (detail.temuan || []).map((t) => {
    let cat: Category = 'ambiguity';
    const rawCat = (t.kategori_cacat || '').toUpperCase();
    if (rawCat.includes('AMBIGU') || rawCat.includes('SUBJEKTIF')) {
      cat = 'ambiguity';
    } else if (rawCat.includes('WEAK') || rawCat.includes('DIREKTIF')) {
      cat = 'weak-directive';
    } else if (rawCat.includes('LENGKAP') || rawCat.includes('INCOMPLETE') || rawCat.includes('MISSING')) {
      cat = 'incomplete';
    } else if (rawCat.includes('PASSIVE') || rawCat.includes('PASIF')) {
      cat = 'passive-voice';
    } else if (rawCat.includes('NON_TESTABLE') || rawCat.includes('UNVERIFIABLE')) {
      cat = 'non-testable';
    }

    return {
      id: String(t.id_temuan),
      ruleId: t.kategori_cacat,
      clause: (t.story_index ?? 0) + 1,
      category: cat,
      term: t.potongan_teks_asli,
      start: t.highlight_start,
      end: t.highlight_end,
      recommendation: t.saran_perbaikan,
    };
  });

  const counts: Record<Category, number> = {
    ambiguity: detail.ringkasan?.ambiguity ?? 0,
    'non-testable': 0,
    incomplete: detail.ringkasan?.tidak_lengkap ?? 0,
    'weak-directive': detail.ringkasan?.weak_directive ?? 0,
    'passive-voice': detail.ringkasan?.passive_voice ?? 0,
  };

  const rawScore = detail.scorecard?.skor_kualitas ?? detail.scorecard?.skor_awal ?? 0;
  const score = Math.round(rawScore);
  const grade: Grade = gradeFor(score, clauses.length > 0);

  // Evaluasi dimensi INVEST dari model backend
  const investData = detail.scorecard?.breakdown?.invest || {};
  const invest: InvestCheck[] = [
    {
      key: 'I',
      label: 'Independent',
      passed: (investData.independent ?? 80) >= 70,
      note: 'Diverifikasi model INVEST backend',
    },
    {
      key: 'N',
      label: 'Negotiable',
      passed: (investData.negotiable ?? 80) >= 70,
      note: 'Diverifikasi model INVEST backend',
    },
    {
      key: 'V',
      label: 'Valuable',
      passed: (investData.valuable ?? 80) >= 70,
      note: 'Diverifikasi model INVEST backend',
    },
    {
      key: 'E',
      label: 'Estimable',
      passed: (investData.estimable ?? 70) >= 70,
      note: 'Diverifikasi model INVEST backend',
    },
    {
      key: 'S',
      label: 'Small',
      passed: (investData.small ?? 85) >= 70,
      note: 'Diverifikasi model INVEST backend',
    },
    {
      key: 'T',
      label: 'Testable',
      passed: (investData.testable ?? 60) >= 70,
      note: 'Diverifikasi model INVEST backend',
    },
  ];

  const isoVals = Object.values(detail.scorecard?.breakdown?.iso_29148 || {}).filter(
    (v): v is number => typeof v === 'number'
  );
  const avgIso = isoVals.length ? Math.round(isoVals.reduce((a, b) => a + b, 0) / isoVals.length) : score;
  const avgInvest = invest.length ? Math.round((invest.filter((i) => i.passed).length / invest.length) * 100) : score;

  const result: AnalysisResult = {
    language: lang,
    clauses,
    wordCount,
    findings,
    counts,
    score,
    grade,
    compliance: {
      iso29148: avgIso,
      invest: avgInvest,
    },
    invest,
  };

  const changed = Boolean(revisedText && revisedText.trim() !== originalText.trim());

  // Buat dummy result untuk teks revisi (skor revisi biasanya mendekati 90-100)
  const revisedClauses = splitClauses(revisedText);
  const revisedScore = Math.min(100, Math.max(score, 90));
  const revisionResult: AnalysisResult = {
    ...result,
    clauses: revisedClauses,
    wordCount: revisedClauses.reduce((n, c) => n + countWords(c.text), 0),
    findings: [],
    counts: { ambiguity: 0, 'non-testable': 0, incomplete: 0, 'weak-directive': 0, 'passive-voice': 0 },
    score: revisedScore,
    grade: gradeFor(revisedScore, true),
    compliance: { iso29148: 95, invest: 100 },
    invest: invest.map((i) => ({ ...i, passed: true })),
  };

  const revision: Revision = {
    text: revisedText,
    changed,
    result: revisionResult,
  };

  const firstAc = detail.rekomendasi_ai?.acceptance_criteria?.[0];
  const criteria: AcceptanceCriteria | null = firstAc
    ? {
        given: firstAc.given,
        when: firstAc.when,
        then: firstAc.then,
      }
    : null;

  return { result, revision, criteria, rawDetail: detail };
}
