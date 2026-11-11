'use client';

import { AudioLines, Check, FlaskConical, Flag, ListChecks, Minus, ScanLine, ShieldCheck, ArrowUpRight, X } from 'lucide-react';
import { useState } from 'react';
import { CATEGORIES, type AnalysisResult, type Category } from '@/lib/analyzer';
import { CATEGORY_LABEL } from '@/lib/format';

const ICONS: Record<Category, typeof ScanLine> = {
  ambiguity: ScanLine,
  'non-testable': FlaskConical,
  incomplete: ListChecks,
  'weak-directive': Flag,
  'passive-voice': AudioLines,
};

function Meter({ label, value }: { label: string; value: number | null }) {
  return (
    <span className="inline-flex items-center gap-2 text-[12px] text-muted">
      {label}
      <span className="h-1 w-10 overflow-hidden rounded-full bg-line/[0.1]" aria-hidden>
        <span className="block h-full rounded-full bg-muted/70" style={{ width: `${value ?? 0}%` }} />
      </span>
      {/* P0/UI-48: null = belum dievaluasi — tampilkan "–", bukan angka buatan. */}
      <span className="font-medium text-ink">{value ?? '–'}</span>
    </span>
  );
}

export function SummaryCard({ result }: { result: AnalysisResult }) {
  const [open, setOpen] = useState(false);
  const total = result.findings.length;

  return (
    <section className="card flex flex-col p-6" aria-label="Ringkasan hasil analisis">
      <div className="flex items-center justify-between gap-3">
        <h2 className="flex items-center gap-2.5 text-[16px] font-semibold">
          Ringkasan Hasil Analisis
          <span className="pill bg-line/[0.06] px-2 py-0.5 text-[11px] text-muted">{total} temuan</span>
        </h2>
        <span className="inline-flex items-center gap-1.5 text-[12px] text-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" aria-hidden /> Analisis selesai
        </span>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {CATEGORIES.map((cat) => {
          const Icon = ICONS[cat];
          const n = result.counts[cat];
          return (
            <div key={cat} className="relative rounded-2xl border border-line/[0.06] bg-card/70 p-4">
              <Icon size={16} strokeWidth={1.6} className="text-muted" aria-hidden />
              {n === 0 && <Check size={13} className="absolute right-3.5 top-4 text-faint" aria-label="Tidak ada temuan" />}
              <p className="mt-3 text-[28px] font-semibold leading-none tracking-tight">{n}</p>
              <p className="mt-1.5 text-[12px] text-muted">{CATEGORY_LABEL[cat]}</p>
            </div>
          );
        })}
      </div>

      <div className="mt-auto pt-5">
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line/[0.07] pt-4">
          <span className="inline-flex items-center gap-2 text-[12px] text-muted">
            <ShieldCheck size={14} aria-hidden /> Kepatuhan standar
          </span>
          <span className="inline-flex items-center gap-5">
            <Meter label="ISO 29148" value={result.compliance.iso29148} />
            <Meter label="INVEST" value={result.compliance.invest} />
            <button
              type="button"
              onClick={() => setOpen((o) => !o)}
              aria-expanded={open}
              aria-label="Lihat detail INVEST"
              className="text-muted transition hover:text-ink"
            >
              <ArrowUpRight size={14} className={open ? 'rotate-90 transition' : 'transition'} />
            </button>
          </span>
        </div>

        {open && (
          <ul className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3">
            {result.invest.map((c) => (
              <li key={c.key} className="flex items-start gap-2.5 rounded-xl bg-line/[0.04] p-3">
                <span
                  className={`mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full ${
                    c.notEvaluated
                      ? 'bg-line/[0.1] text-muted'
                      : c.passed
                        ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                        : 'bg-rose-500/15 text-rose-600 dark:text-rose-400'
                  }`}
                >
                  {c.notEvaluated ? (
                    <Minus size={12} aria-label="Belum dievaluasi" />
                  ) : c.passed ? (
                    <Check size={12} aria-label="Lulus" />
                  ) : (
                    <X size={12} aria-label="Belum lulus" />
                  )}
                </span>
                <span>
                  <span className="block text-[12.5px] font-semibold">
                    {c.key} · {c.label}
                  </span>
                  <span className="block text-[11.5px] leading-snug text-muted">{c.note}</span>
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
