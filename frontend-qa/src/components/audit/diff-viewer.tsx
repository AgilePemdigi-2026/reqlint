'use client';

import { ArrowRight, Columns2, MapPin } from 'lucide-react';
import { useMemo } from 'react';
import { diffWords, type DiffOp } from '@/lib/analyzer';
import { useT } from '@/lib/i18n';

function Pane({
  title,
  badge,
  badgeClass,
  lines,
  highlight,
  className = '',
}: {
  title: string;
  badge: string;
  badgeClass: string;
  lines: DiffOp[][];
  highlight?: boolean;
  className?: string;
}) {
  return (
    <div
      className={`overflow-hidden rounded-2xl border bg-card/70 ${
        highlight ? 'border-accent/35 shadow-[0_0_0_3px_rgb(var(--accent)/0.07)]' : 'border-line/[0.08]'
      } ${className}`}
    >
      <div className="flex items-center justify-between border-b border-line/[0.07] px-4 py-2.5">
        <span className="flex items-center gap-2 text-[11.5px] text-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-faint" aria-hidden /> {title}
        </span>
        <span className={`pill px-2 py-0.5 text-[10.5px] ${badgeClass}`}>{badge}</span>
      </div>
      <ol className="space-y-1 px-4 py-4 font-mono text-[12px] leading-[1.9]">
        {lines.map((line, i) => (
          <li key={i} className="grid grid-cols-[20px_1fr] gap-2">
            <span className="select-none text-faint">{i + 1}</span>
            <span className="whitespace-pre-wrap break-words">
              {line.map((op, j) =>
                op.type === 'equal' ? (
                  <span key={j}>{op.text}</span>
                ) : (
                  <span
                    key={j}
                    className={
                      op.type === 'del'
                        ? 'rounded bg-rose-500/15 px-0.5 text-rose-700 line-through decoration-rose-500/60 dark:text-rose-300'
                        : 'rounded bg-emerald-500/15 px-0.5 text-emerald-800 dark:text-emerald-300'
                    }
                  >
                    {op.text}
                  </span>
                ),
              )}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}

export function DiffViewer({
  original,
  revised,
  originalScore,
  revisedScore,
}: {
  original: string;
  revised: string;
  originalScore?: number;
  revisedScore?: number;
}) {
  const t = useT();

  const { leftLines, rightLines } = useMemo(() => {
    const origLines = original.split('\n');
    const revLines = revised.split('\n');
    const max = Math.max(origLines.length, revLines.length);
    const left: DiffOp[][] = [];
    const right: DiffOp[][] = [];

    for (let i = 0; i < max; i++) {
      const a = origLines[i] ?? '';
      const b = revLines[i] ?? '';
      if (a === b) {
        left.push([{ type: 'equal', text: a }]);
        right.push([{ type: 'equal', text: b }]);
      } else {
        const ops = diffWords(a, b);
        left.push(ops.filter((op) => op.type !== 'add'));
        right.push(ops.filter((op) => op.type !== 'del'));
      }
    }
    return { leftLines: left, rightLines: right };
  }, [original, revised]);

  const delta = originalScore !== undefined && revisedScore !== undefined ? revisedScore - originalScore : null;

  return (
    <section className="card p-6" aria-label="Perbandingan sebelum dan sesudah revisi">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="flex items-center gap-2.5 text-[16px] font-semibold">
          <Columns2 size={16} strokeWidth={1.6} className="text-muted" aria-hidden />
          {t('audit.diff_title')}
        </h2>
        {delta !== null && (
          <span className="pill bg-emerald-500/10 text-emerald-700 dark:text-emerald-300">
            Skor: {originalScore} → {revisedScore} ({delta >= 0 ? `+${delta}` : delta})
          </span>
        )}
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <Pane
          title={t('audit.diff_before')}
          badge={originalScore !== undefined ? `Skor ${originalScore}` : t('audit.original_badge')}
          badgeClass="bg-line/[0.06] text-muted"
          lines={leftLines}
        />
        <Pane
          title={t('audit.diff_after')}
          badge={revisedScore !== undefined ? `Skor ${revisedScore}` : t('audit.revised_badge')}
          badgeClass="bg-emerald-500/15 text-emerald-700 dark:text-emerald-400"
          lines={rightLines}
          highlight
        />
      </div>
    </section>
  );
}
