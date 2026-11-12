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
import { analyze, gradeFor } from './analyze';
import type { BackendAuditDetail } from '../api';

export function adaptBackendAuditToAnalysisResult(
  detail: BackendAuditDetail,
  fallbackLang: Language = 'id'
): {
  result: AnalysisResult;
  revision: Revision;
  originalLocal: AnalysisResult;
  criteria: AcceptanceCriteria | null;
  rawDetail: BackendAuditDetail;
} {
  const originalText = detail.diff?.original?.teks || '';
  const revisedText = detail.diff?.revised?.teks || detail.rekomendasi_ai?.ai_rewrite || originalText;

  // P0.1/R2-2: bahasa dideteksi per teks — teks revisi bisa berbeda bahasa
  // dari teks asli, dan masing-masing dievaluasi dengan bahasanya sendiri.
  const langFor = (t: string): Language =>
    /\b(as a|i want|so that|shall|should)\b/i.test(t) ? 'en' : fallbackLang;
  const lang = langFor(originalText);

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

  // P0/UI-48: pemetaan INVEST null-safe. Nilai breakdown yang hilang (null)
  // berarti kriteria BELUM dievaluasi — bukan lulus.
  const investData = detail.scorecard?.breakdown?.invest || {};
  const stateOf = (v: number | null | undefined): 'pass' | 'fail' | 'unknown' =>
    v == null ? 'unknown' : v >= 70 ? 'pass' : 'fail';
  const investCheck = (
    key: InvestCheck['key'],
    label: string,
    raw: number | null | undefined,
  ): InvestCheck => {
    const state = stateOf(raw);
    return {
      key,
      label,
      passed: state === 'pass',
      notEvaluated: state === 'unknown',
      note:
        state === 'unknown'
          ? 'Belum dievaluasi — data INVEST tidak tersedia dari backend'
          : 'Diverifikasi model INVEST backend',
    };
  };
  const invest: InvestCheck[] = [
    investCheck('I', 'Independent', investData.independent),
    investCheck('N', 'Negotiable', investData.negotiable),
    investCheck('V', 'Valuable', investData.valuable),
    investCheck('E', 'Estimable', investData.estimable),
    investCheck('S', 'Small', investData.small),
    investCheck('T', 'Testable', investData.testable),
  ];

  const isoVals = Object.values(detail.scorecard?.breakdown?.iso_29148 || {}).filter(
    (v): v is number => typeof v === 'number'
  );
  const avgIso = isoVals.length ? Math.round(isoVals.reduce((a, b) => a + b, 0) / isoVals.length) : score;
  // P0/UI-48: compliance INVEST hanya dihitung dari kriteria yang benar-benar
  // dievaluasi; null bila tidak ada sama sekali (bukan 0%, bukan 100%).
  const evaluatedInvest = invest.filter((i) => !i.notEvaluated);
  const avgInvest = evaluatedInvest.length
    ? Math.round((evaluatedInvest.filter((i) => i.passed).length / evaluatedInvest.length) * 100)
    : null;

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

  // P0.1/R2-1: DiffViewer membandingkan dua sisi dengan EVALUATOR YANG SAMA —
  // analyzer lokal pada teks asli (`originalLocal`) vs teks revisi
  // (`revisionResult` saat changed). Skor audit resmi dari backend tetap ada
  // di `result` dan tidak pernah ditimpa nilai-nilai lokal ini.
  const originalLocal = analyze(originalText, lang);
  const revisionResult = changed ? analyze(revisedText, langFor(revisedText)) : result;

  const revision: Revision = {
    text: revisedText,
    changed,
    result: revisionResult,
    originalLocal,
  };

  const firstAc = detail.rekomendasi_ai?.acceptance_criteria?.[0];
  const criteria: AcceptanceCriteria | null = firstAc
    ? {
        given: firstAc.given,
        when: firstAc.when,
        then: firstAc.then,
      }
    : null;

  return { result, revision, originalLocal, criteria, rawDetail: detail };
}
