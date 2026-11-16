import type { Audit } from './audits';
import { categoryLabel, formatDate, gradeLabel } from './format';
import type { AnalysisResult, Revision } from './analyzer';

export type ExportFormat = 'md' | 'csv' | 'json';

// Task 07: evaluator identity/provenance ikut diekspor (metadata opsional).
// AI advisory notes dipisahkan eksplisit dari findings evaluator.
export interface ExportMeta {
  evaluator?: string;
  modelVersion?: string | null;
  aiInvestNotes?: Record<string, boolean> | null;
  locale?: 'id' | 'en';
}

type ExportLabels = {
  title: (id: string) => string;
  judul: string;
  tanggal: string;
  skor: string;
  praktik: string;
  invest: string;
  draf: string;
  temuan: (n: number) => string;
  none: string;
  lokasi: string;
  kategori: string;
  istilah: string;
  rekom: string;
  kalimat: string;
  saranRevisi: (skor: number) => string;
  catatan: string;
  flagged: string;
  lolos: string;
  unknown: string;
  nochange: string;
  evaluator: string;
  model: string;
};

const LABELS: Record<'id' | 'en', ExportLabels> = {
  id: {
    title: (id: string) => `Hasil Audit ${id}`,
    judul: 'Judul',
    tanggal: 'Tanggal',
    skor: 'Skor kualitas',
    praktik: 'Praktik dokumen (heuristik)',
    invest: 'dimensi INVEST',
    draf: 'Draf Orisinal',
    temuan: (n: number) => `Temuan Cacat (${n})`,
    none: 'Tidak ada temuan.',
    lokasi: 'Lokasi',
    kategori: 'Kategori',
    istilah: 'Istilah Terdeteksi',
    rekom: 'Rekomendasi',
    kalimat: 'Kalimat',
    saranRevisi: (skor: number) => `Saran Revisi (skor ${skor})`,
    catatan: 'Catatan AI (advisory — bukan findings evaluator)',
    flagged: 'LLM menandai perlu perhatian (dinilai gagal oleh LLM)',
    lolos: 'lolos menurut LLM',
    unknown: 'nilai tidak diketahui',
    nochange: '(tidak mengubah skor/verdict)',
    evaluator: 'Evaluator',
    model: '(model: {mv})',
  },
  en: {
    title: (id: string) => `Audit Result ${id}`,
    judul: 'Title',
    tanggal: 'Date',
    skor: 'Quality score',
    praktik: 'Document practice (heuristic)',
    invest: 'INVEST dimensions',
    draf: 'Original Draft',
    temuan: (n: number) => `Defect Findings (${n})`,
    none: 'No defects found.',
    lokasi: 'Location',
    kategori: 'Category',
    istilah: 'Detected Term',
    rekom: 'Recommendation',
    kalimat: 'Clause',
    saranRevisi: (skor: number) => `Suggested Revision (score ${skor})`,
    catatan: 'AI notes (advisory — not evaluator findings)',
    flagged: 'flagged by the LLM as failing',
    lolos: 'passing per the LLM',
    unknown: 'unknown value',
    nochange: '(does not change score/verdict)',
    evaluator: 'Evaluator',
    model: '(model: {mv})',
  },
};

const evaluatorLine = (meta?: ExportMeta): string => {
  if (!meta?.evaluator) return '';
  const model = meta.modelVersion ? ` (model: ${meta.modelVersion})` : '';
  const label = meta.locale === 'en' ? 'Evaluator' : 'Evaluator';
  return `- ${label}: **${meta.evaluator}${model}**`;
};

const advisoryLines = (meta: ExportMeta | undefined, L: (typeof LABELS)['id']): string[] => {
  if (!meta?.aiInvestNotes || Object.keys(meta.aiInvestNotes).length === 0) return [];
  return [
    '',
    `## ${L.catatan}`,
    '',
    // Semantik historis: `true` = kriteria lolos menurut LLM, `false` = LLM
    // menandai kriteria bermasalah. Nilai ini TIDAK mengubah skor/verdict.
    ...Object.entries(meta.aiInvestNotes).map(([crit, flagged]) =>
      `- ${crit}: ${
        flagged === false
          ? L.flagged
          : flagged === true
            ? L.lolos
            : L.unknown
      } ${L.nochange}`
    ),
  ];
};

export function toMarkdown(audit: Audit, result: AnalysisResult, revision: Revision, meta?: ExportMeta): string {
  const locale = meta?.locale ?? 'id';
  const L = LABELS[locale];
  const lines: string[] = [
    L.title(audit.id),
    '',
    evaluatorLine(meta),
    `- ${L.judul}: ${audit.title}`,
    `- ${L.tanggal}: ${formatDate(audit.createdAt, locale)}`,
    `- ${L.skor}: **${result.score}/100** (${gradeLabel(result.grade, locale)})`,
    `- ${L.praktik}: ${result.compliance.iso29148}% · ${L.invest} ${result.compliance.invest}%`,
    '',
    `## ${L.draf}`,
    '',
    ...audit.text.split('\n').map((l) => `> ${l}`),
    '',
    `## ${L.temuan(result.findings.length)}`,
    '',
  ];
  if (result.findings.length) {
    lines.push(`| ${L.lokasi} | ${L.kategori} | ${L.istilah} | ${L.rekom} |`, '| --- | --- | --- | --- |');
    for (const f of result.findings) {
      lines.push(`| ${L.kalimat} ${f.clause} | ${categoryLabel(f.category, locale)} | \`${f.term}\` | ${f.recommendation} |`);
    }
  } else {
    lines.push(L.none);
  }
  if (revision.changed) {
    lines.push('', `## ${L.saranRevisi(revision.result.score)}`, '', ...revision.text.split('\n').map((l) => `> ${l}`));
  }
  lines.push(...advisoryLines(meta, L));
  return lines.join('\n') + '\n';
}

const csvCell = (v: string | number) => `"${String(v).replace(/"/g, '""')}"`;

export function toCsv(audit: Audit, result: AnalysisResult, locale: 'id' | 'en' = 'id'): string {
  // Task 09: header CSV mengikuti locale UI (dulu ID statis).
  const L = LABELS[locale];
  const rows = [['audit_id', L.kalimat.toLowerCase(), L.kategori.toLowerCase(), L.istilah.toLowerCase(), L.rekom.toLowerCase()]];
  for (const f of result.findings) {
    rows.push([audit.id, String(f.clause), categoryLabel(f.category, locale), f.term, f.recommendation]);
  }
  return rows.map((r) => r.map(csvCell).join(',')).join('\n') + '\n';
}

export function toJson(audit: Audit, result: AnalysisResult, revision: Revision, meta?: ExportMeta): string {
  return JSON.stringify(
    {
      evaluator: meta?.evaluator ?? null,
      model_version: meta?.modelVersion ?? null,
      audit,
      result,
      revision: { changed: revision.changed, text: revision.text, score: revision.result.score },
      ai_advisory_notes: meta?.aiInvestNotes ?? null,
    },
    null,
    2,
  );
}

const MIME: Record<ExportFormat, string> = {
  md: 'text/markdown;charset=utf-8',
  csv: 'text/csv;charset=utf-8',
  json: 'application/json;charset=utf-8',
};

export function buildExport(format: ExportFormat, audit: Audit, result: AnalysisResult, revision: Revision, meta?: ExportMeta) {
  const content =
    format === 'md'
      ? toMarkdown(audit, result, revision, meta)
      : format === 'csv'
        ? toCsv(audit, result, meta?.locale ?? 'id')
        : toJson(audit, result, revision, meta);
  return { filename: `${audit.id}.${format}`, mime: MIME[format], content };
}

export function download(filename: string, mime: string, content: string) {
  // BOM agar Excel membaca CSV UTF-8 dengan benar.
  const blob = new Blob([mime.startsWith('text/csv') ? '﻿' + content : content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    ta.remove();
    return ok;
  }
}
