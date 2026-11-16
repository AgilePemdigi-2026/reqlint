'use client';

import { CheckCircle2, XCircle, MinusCircle } from 'lucide-react';
import { useT } from '@/lib/i18n';

type DimensionEntry = {
  label?: string;
  confidence?: number | null;
  rationale?: string | null;
};

/**
 * Task 10 Phase 3: renders the dimension-level evaluation produced by the
 * ACTUAL evaluator (Traditional ML / LLM/SLM). Previously this data existed
 * in the API response but was never displayed, which made ML/LLM audits look
 * like empty Rule-Based results. The evaluator attribution is explicit —
 * these verdicts belong to the evaluation contract, never to a fallback.
 */
export function DimensionResults({
  dimensions,
  evaluatorLabel,
  verdict,
}: {
  dimensions: Record<string, DimensionEntry>;
  evaluatorLabel: string;
  verdict?: string | null;
}) {
  const t = useT();
  const entries = ['independent', 'negotiable', 'valuable', 'estimable', 'small', 'testable']
    .map((key) => ({ key, dim: dimensions[key] }))
    .filter(({ dim }) => Boolean(dim));

  if (entries.length === 0) return null;

  const badgeFor = (label: string | undefined) => {
    switch ((label ?? '').toUpperCase()) {
      case 'PASS':
        return {
          icon: <CheckCircle2 size={14} aria-hidden />,
          text: t('dims.pass'),
          cls: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25',
        };
      case 'FAIL':
        return {
          icon: <XCircle size={14} aria-hidden />,
          text: t('dims.fail'),
          cls: 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/25',
        };
      default:
        return {
          icon: <MinusCircle size={14} aria-hidden />,
          text: t('dims.ie'),
          cls: 'bg-line/[0.06] text-muted border border-line/25',
        };
    }
  };

  return (
    <section
      className="card p-6"
      aria-label={t('dims.title')}
      data-testid="dimension-results"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-[16px] font-semibold">{t('dims.title')}</h2>
        <span className="pill bg-line/[0.06] px-2 py-0.5 text-[10.5px] text-muted">
          {t('dims.by_evaluator', { evaluator: evaluatorLabel })}
        </span>
      </div>

      <ul className="mt-4 grid gap-3 sm:grid-cols-2">
        {entries.map(({ key, dim }) => {
          const badge = badgeFor(dim?.label);
          const conf =
            typeof dim?.confidence === 'number' ? t('dims.confidence', { n: Math.round(dim.confidence * 100) }) : null;
          const rationale = (dim?.rationale ?? '').trim();
          const unsupported = rationale.startsWith('EVALUATOR_UNSUPPORTED');
          return (
            <li key={key} className="rounded-2xl border border-line/[0.07] bg-card/60 p-4">
              <div className="flex items-center justify-between gap-2">
                <span className="text-[13.5px] font-semibold capitalize">{key}</span>
                <span className={`pill px-2 py-0.5 text-[10.5px] font-medium ${badge.cls}`}>
                  {badge.icon} {badge.text}
                </span>
              </div>
              {conf && <p className="mt-1 text-[11.5px] text-muted">{conf}</p>}
              <p className="mt-1.5 text-[12.5px] leading-snug text-muted">
                {rationale && !unsupported ? rationale : t('dims.no_rationale')}
              </p>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
