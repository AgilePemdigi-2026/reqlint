'use client';

import { HelpCircle } from 'lucide-react';
import type { AnalysisResult } from '@/lib/analyzer';
import { GRADE_BADGE, GRADE_COLOR, gradeLabel, gradeTagline } from '@/lib/format';
import { useT, useUILocale } from '@/lib/i18n';

export function ScoreRing({ score, color, size = 108 }: { score: number; color: string; size?: number }) {
  const stroke = 9;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90" aria-hidden>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeOpacity={0.16} strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - score / 100)}
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-[38px] font-semibold leading-none tracking-tight">{score}</span>
        <span className="mt-1 text-[11px] text-muted">/ 100</span>
      </div>
    </div>
  );
}

export function ScoreCard({ result, provenance }: { result: AnalysisResult; provenance?: string }) {
  const t = useT();
  const uiLocale = useUILocale();
  return (
    <section className="card flex flex-col p-6" aria-label={t('scorecard.aria')}>
      <div className="flex items-center justify-between">
        <h2 className="text-[16px] font-semibold">{t('scorecard.aria')}</h2>
        <span
          className="text-muted"
          title={t('scorecard.tooltip')}
        >
          <HelpCircle size={16} aria-label={t('scorecard.how_aria')} />
        </span>
      </div>
      <div className="flex flex-1 flex-col items-center justify-center py-5" role="img" aria-label={t('scorecard.score_aria', { n: result.score })}>
        <ScoreRing score={result.score} color={GRADE_COLOR[result.grade]} />
        <span className={`pill mt-5 ${GRADE_BADGE[result.grade]}`}>
          <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden /> {gradeLabel(result.grade, uiLocale)}
        </span>
        <p className="mt-3 text-center text-[12.5px] text-muted">{gradeTagline(result.grade, uiLocale)}</p>
        {/* Task 10 Phase 3: explicit score provenance — the displayed score is
            attributed to the evaluator that actually produced it. */}
        {provenance && <p className="mt-2 text-center text-[11.5px] text-muted">{provenance}</p>}
      </div>
    </section>
  );
}
