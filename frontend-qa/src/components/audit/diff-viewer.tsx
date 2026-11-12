import { ArrowRight, Columns2, MapPin } from 'lucide-react';
import { useMemo } from 'react';
import { diffLines, diffWords, type DiffOp } from '@/lib/analyzer';

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
  before,
  after,
  beforeScore,
  afterScore,
  localEstimate = false,
  onApply,
  canApply,
}: {
  before: string;
  after: string;
  beforeScore: number;
  afterScore: number;
  /** P0.1/R2-1: true bila kedua skor adalah estimasi mesin lokal (evaluator
   * yang sama untuk kedua sisi) — bukan skor audit resmi dari backend. */
  localEstimate?: boolean;
  onApply: () => void;
  canApply: boolean;
}) {
  const { left, right } = useMemo(() => {
    const ops = diffWords(before, after);
    return { left: diffLines(ops, 'before'), right: diffLines(ops, 'after') };
  }, [before, after]);

  return (
    <section className="card p-6" aria-label="Diff viewer">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="flex items-center gap-2.5 text-[16px] font-semibold">
          <Columns2 size={16} strokeWidth={1.6} className="text-muted" aria-hidden />
          Diff Viewer <span className="font-normal text-muted">— Before / After</span>
        </h2>
        {canApply && (
          <button type="button" onClick={onApply} className="btn-primary h-9 rounded-full px-4 text-[12.5px]">
            Apply Revision <ArrowRight size={14} aria-hidden />
          </button>
        )}
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <Pane
          title="Draf Orisinal"
          badge={localEstimate ? `Estimasi lokal ${beforeScore}` : `Skor ${beforeScore}`}
          badgeClass="bg-line/[0.06] text-muted"
          lines={left}
        />
        <Pane
          title="Revised Requirement"
          badge={localEstimate ? `Estimasi lokal ${afterScore}` : `Skor ${afterScore}`}
          badgeClass="bg-emerald-100 text-emerald-800 dark:bg-emerald-400/15 dark:text-emerald-300"
          lines={right}
          highlight
        />
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-[11px] text-muted">
        <span className="flex items-center gap-4">
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-sm bg-rose-500/40" aria-hidden /> Dihapus
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-sm bg-emerald-500/40" aria-hidden /> Ditambahkan
          </span>
        </span>
        <span className="inline-flex items-center gap-1.5">
          <MapPin size={12} aria-hidden /> Anda selalu memegang kendali atas revisi.
        </span>
      </div>

      {localEstimate && (
        <p className="mt-2 text-[11px] leading-snug text-muted">
          Kedua skor di atas adalah <strong>estimasi mesin lokal yang sama</strong> (deterministik) agar
          before/after dapat dibandingkan — skor audit resmi dari backend tetap tertera pada kartu Ringkasan.
        </p>
      )}
    </section>
  );
}
