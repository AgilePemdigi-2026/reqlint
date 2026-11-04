export * from './types';
export { analyze, liveMarks, PENALTY } from './analyze';
export { splitClauses, countWords } from './clauses';
export { revise, acceptanceCriteria } from './revise';
export { diffWords, diffLines, type DiffOp } from './diff';
export { STORY } from './rules';
export { adaptBackendAuditToAnalysisResult } from './adapter';

import { splitClauses } from './clauses';
import { STORY } from './rules';
import type { Language } from './types';

/** Judul ringkas audit, diambil dari tujuan user story (atau klausul pertama). */
export function suggestTitle(text: string, lang: Language): string {
  const first = splitClauses(text)[0]?.text ?? '';
  const goal = STORY[lang].parse.exec(first)?.groups?.goal ?? first;
  const words = goal.replace(/[.!?]+$/, '').split(/\s+/).filter(Boolean).slice(0, 4).join(' ');
  if (!words) return lang === 'id' ? 'Tanpa judul' : 'Untitled';
  return words.charAt(0).toUpperCase() + words.slice(1);
}
