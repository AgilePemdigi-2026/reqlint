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
    <section className="card flex flex-col p-6" aria-label="Rekomendasi perbaikan">
      <div className="flex items-center justify-between">
        <h2 className="flex items-center gap-2.5 text-[16px] font-semibold">
          <Wand2 size={16} strokeWidth={1.6} className="text-muted" aria-hidden />
          {t('audit.revision_title')} <span className="font-normal text-muted">{t('audit.auto_badge')}</span>
        </h2>
        <span className="eyebrow text-[10.5px]">{t('audit.revision_eyebrow')}</span>
      </div>

      {revision.changed ? (
        <p className="mt-4 whitespace-pre-line rounded-2xl border border-line/[0.07] bg-card/70 p-4 text-[13.5px] leading-relaxed">
          {revision.text}
        </p>
      ) : (
        <p className="mt-4 rounded-2xl border border-dashed border-line/15 p-4 text-[13.5px] leading-relaxed text-muted">
          {t('audit.no_auto_revision')}
        </p>
      )}

      {revision.changed && (
        <p className="mt-2.5 text-[11.5px] leading-snug text-muted">
          Angka pada revisi (mis. 2 detik, 3 langkah) adalah nilai contoh — sesuaikan dengan target tim Anda.
          {remaining > 0 && ` Masih ada ${remaining} temuan yang perlu diperbaiki manual.`}
        </p>
      )}

      <div className="mt-auto flex flex-wrap items-center gap-2.5 pt-5">
        {revision.changed && (
          <button type="button" onClick={onApply} className="btn-primary h-9 rounded-full px-4 text-[12.5px]">
            <CheckCheck size={14} aria-hidden /> {t('audit.apply')}
          </button>
        )}
        <button type="button" onClick={onEdit} className="btn-ghost h-9 rounded-full px-4 text-[12.5px] shadow-none">
          {t('audit.edit_manual')} <ArrowUpRight size={13} aria-hidden />
        </button>
        <span className="ml-auto text-[10.5px] text-muted">Lebih jelas. Lebih terukur.</span>
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
    <section className="card flex flex-col p-6" aria-label="Acceptance criteria">
      <div className="flex items-center justify-between">
        <h2 className="flex items-center gap-2.5 text-[16px] font-semibold">
          <ListChecks size={16} strokeWidth={1.6} className="text-muted" aria-hidden />
          {t('audit.acceptance_title')}
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
          <p className="mt-auto pt-3 text-[11.5px] text-muted">
            {t('audit.criteria_eyebrow')} — draf template
          </p>
        </>
      ) : (
        <p className="mt-4 rounded-2xl border border-dashed border-line/15 p-4 text-[13.5px] leading-relaxed text-muted">
          Tulis klausul dengan format &quot;Sebagai …, saya ingin …, agar …&quot; atau kalimat berisi &quot;harus&quot; untuk
          membuat acceptance criteria.
        </p>
      )}
    </section>
  );
}
