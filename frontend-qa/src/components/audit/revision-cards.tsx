'use client';

import { ArrowUpRight, CheckCheck, ListChecks, Wand2 } from 'lucide-react';
import type { AcceptanceCriteria, Revision } from '@/lib/analyzer';
import { useT } from '@/lib/i18n';

export function RevisionCard({
  revision,
  remaining,
  onApply,
  onEdit,
}: {
  revision: Revision;
  /** Jumlah temuan yang masih tersisa pada draf revisi (perlu perbaikan manual). */
  remaining: number;
  onApply: () => void;
  onEdit: () => void;
}) {
  const t = useT();
  return (
    <section className="card flex flex-col p-6" aria-label={t('revision.aria')}>
      <div className="flex items-center justify-between">
        <h2 className="flex items-center gap-2.5 text-[16px] font-semibold">
          <Wand2 size={16} strokeWidth={1.6} className="text-muted" aria-hidden />
          {t('revision.title')} <span className="font-normal text-muted">{t('revision.auto_tag')}</span>
        </h2>
        <span className="eyebrow text-[10.5px]">{t('revision.tag')}</span>
      </div>

      {revision.changed ? (
        <p className="mt-4 whitespace-pre-line rounded-2xl border border-line/[0.07] bg-card/70 p-4 text-[13.5px] leading-relaxed">
          {revision.text}
        </p>
      ) : (
        <p className="mt-4 rounded-2xl border border-dashed border-line/15 p-4 text-[13.5px] leading-relaxed text-muted">
          {t('revision.empty')}
        </p>
      )}

      {revision.changed && (
        <p className="mt-2.5 text-[11.5px] leading-snug text-muted">
          {t('revision.note')}
          {remaining > 0 && ` ${t('revision.remaining', { n: remaining })}`}
        </p>
      )}

      <div className="mt-auto flex flex-wrap items-center gap-2.5 pt-5">
        {revision.changed && (
          <button type="button" onClick={onApply} className="btn-primary h-9 rounded-full px-4 text-[12.5px]">
            <CheckCheck size={14} aria-hidden /> {t('revision.apply')}
          </button>
        )}
        <button type="button" onClick={onEdit} className="btn-ghost h-9 rounded-full px-4 text-[12.5px] shadow-none">
          {t('revision.edit_manual')} <ArrowUpRight size={13} aria-hidden />
        </button>
        <span className="ml-auto text-[10.5px] text-muted">{t('revision.tagline')}</span>
      </div>
    </section>
  );
}

export function AcceptanceCard({ criteria }: { criteria: AcceptanceCriteria | null }) {
  const t = useT();
  const rows = criteria
    ? [
        ['Given', criteria.given],
        ['When', criteria.when],
        ['Then', criteria.then],
      ]
    : [];
  return (
    <section className="card flex flex-col p-6" aria-label={t('acceptance.aria')}>
      <div className="flex items-center justify-between">
        <h2 className="flex items-center gap-2.5 text-[16px] font-semibold">
          <ListChecks size={16} strokeWidth={1.6} className="text-muted" aria-hidden />
          {t('acceptance.title')}
        </h2>
        <span className="pill bg-line/[0.06] px-2 py-0.5 text-[10.5px] text-muted">BDD</span>
      </div>

      {criteria ? (
        <>
          <dl className="mt-4 divide-y divide-line/[0.07] text-[13px]">
            {rows.map(([k, v]) => (
              <div key={k} className="grid grid-cols-[56px_1fr] gap-4 py-3">
                <dt className="font-mono text-[11.5px] font-medium text-accent">{k}</dt>
                <dd className="leading-relaxed text-muted">{v}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-auto pt-3 text-[11.5px] text-muted">{t('acceptance.note')}</p>
        </>
      ) : (
        <p className="mt-4 rounded-2xl border border-dashed border-line/15 p-4 text-[13.5px] leading-relaxed text-muted">
          {t('acceptance.empty')}
        </p>
      )}
    </section>
  );
}
