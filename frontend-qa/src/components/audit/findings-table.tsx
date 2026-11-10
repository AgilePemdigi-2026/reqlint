'use client';

import { ArrowUpRight, CheckCircle2 } from 'lucide-react';
import type { Finding } from '@/lib/analyzer';
import { CATEGORY_LABEL, CATEGORY_STYLE } from '@/lib/format';
import { useT } from '@/lib/i18n';

export function FindingsTable({ findings, onOpenEditor }: { findings: Finding[]; onOpenEditor: () => void }) {
  const t = useT();

  return (
    <section className="card p-6" aria-label="Temuan cacat">
      <div className="flex items-center justify-between">
        <h2 className="flex items-center gap-2.5 text-[16px] font-semibold">
          {t('audit.findings_title')}
          <span className="pill bg-line/[0.06] px-2 py-0.5 text-[11px] text-muted">{findings.length}</span>
        </h2>
        <button
          type="button"
          onClick={onOpenEditor}
          className="inline-flex items-center gap-1.5 text-[12px] font-medium text-muted transition hover:text-ink"
        >
          {t('audit.findings_view_editor')} <ArrowUpRight size={13} aria-hidden />
        </button>
      </div>

      {findings.length === 0 ? (
        <div className="mt-6 flex flex-col items-center gap-2 rounded-2xl bg-emerald-500/[0.07] px-4 py-8 text-center">
          <CheckCircle2 size={26} className="text-emerald-600 dark:text-emerald-400" aria-hidden />
          <p className="text-[14.5px] font-semibold">{t('audit.no_defects')}</p>
          <p className="text-[12.5px] text-muted">{t('audit.clean_pass')}</p>
        </div>
      ) : (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[640px] border-collapse text-left">
            <thead>
              <tr className="text-[11.5px] font-medium text-muted">
                <th className="w-[130px] pb-3 pr-3 font-medium">{t('audit.col_location')}</th>
                <th className="w-[140px] pb-3 pr-3 font-medium">{t('audit.col_category')}</th>
                <th className="w-[180px] pb-3 pr-3 font-medium">{t('audit.col_term')}</th>
                <th className="pb-3 font-medium">{t('audit.col_recommendation')}</th>
              </tr>
            </thead>
            <tbody>
              {findings.map((f, i) => (
                <tr key={f.id} className="border-t border-line/[0.07] align-top text-[13px]">
                  <td className="py-3.5 pr-3">
                    <span className="mr-3 text-[10.5px] text-faint">{String(i + 1).padStart(2, '0')}</span>
                    {t('audit.sentence')} {f.clause}
                  </td>
                  <td className="py-3.5 pr-3">
                    <span className={`pill ${CATEGORY_STYLE[f.category]}`}>{CATEGORY_LABEL[f.category]}</span>
                  </td>
                  <td className="py-3.5 pr-3">
                    <code className="rounded-md bg-line/[0.06] px-2 py-1 font-mono text-[11.5px]">{f.term}</code>
                  </td>
                  <td className="py-3.5 leading-relaxed text-muted">{f.recommendation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
