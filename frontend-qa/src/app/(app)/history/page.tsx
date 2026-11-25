'use client';

import { ArrowRight, History, Search, Trash2, X, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { PageHeader } from '@/components/app-shell';
import { useToast } from '@/components/providers';
import type { Category, Grade } from '@/lib/analyzer';
import { buildHistoryRows, rowGrade, rowScore, type HistoryRow } from '@/lib/history';
import { clearAudits, deleteAudit, syncAudits, useAudits, type Audit } from '@/lib/audits';
import { apiGetAuditsHistory } from '@/lib/api';
import { GRADE_BADGE, categoryLabelT, formatDate, gradeLabel } from '@/lib/format';
import { useT, useUILocale } from '@/lib/i18n';

type DateFilter = 'all' | 'today' | '7d' | '30d';
type LangFilter = 'all' | 'id' | 'en';
type SortKey = 'newest' | 'oldest' | 'score-desc' | 'score-asc';

const DAY_MS = 24 * 60 * 60 * 1000;

function inDateRange(iso: string, range: DateFilter): boolean {
  if (range === 'all') return true;
  if (range === 'today') return new Date(iso).toDateString() === new Date().toDateString();
  return Date.now() - new Date(iso).getTime() <= (range === '7d' ? 7 : 30) * DAY_MS;
}

export default function HistoryPage() {
  const audits = useAudits();
  const toast = useToast();
  const t = useT();
  const uiLocale = useUILocale();
  const [query, setQuery] = useState('');
  const [dateRange, setDateRange] = useState<DateFilter>('all');
  const [grade, setGrade] = useState<Grade | 'all'>('all');
  const [lang, setLang] = useState<LangFilter>('all');
  const [category, setCategory] = useState<Category | 'all'>('all');
  const [sort, setSort] = useState<SortKey>('newest');
  const [syncing, setSyncing] = useState<boolean>(false);

  // Task 09: opsi filter dwibahasa (dulu ID statis).
  const DATE_OPTIONS: Array<{ value: DateFilter; label: string }> = [
    { value: 'all', label: t('history.date_all') },
    { value: 'today', label: t('history.date_today') },
    { value: '7d', label: t('history.date_7d') },
    { value: '30d', label: t('history.date_30d') },
  ];

  // Mengambil dan menyinkronkan riwayat dari backend FastAPI secara otomatis
  useEffect(() => {
    let cancelled = false;
    async function loadBackendHistory() {
      try {
        setSyncing(true);
        const res = await apiGetAuditsHistory({ limit: 50 });
        if (cancelled || !res?.data?.items) return;

        const backendAudits: Audit[] = res.data.items.map((item) => ({
          id: String(item.id_audit),
          seq: item.id_audit,
          createdAt: item.tanggal_audit || new Date().toISOString(),
          title: item.judul_klausul || t('history.audit_num', { id: item.id_audit }),
          text: item.judul_klausul || t('history.clause_fallback'),
          language: 'id',
          // P0/FUNC-06: bawa skor & status TERSIMPAN dari backend.
          backendScore: item.skor_kualitas,
          backendStatus: item.status_audit,
          requestedEvaluator: item.evaluator ?? null,
          modelVersion: item.model_version ?? null,
        }));
        syncAudits(backendAudits);
      } catch (err) {
        console.warn('Gagal memuat riwayat audit dari backend, menggunakan riwayat lokal:', err);
      } finally {
        if (!cancelled) setSyncing(false);
      }
    }

    loadBackendHistory();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeFilters =
    (dateRange !== 'all' ? 1 : 0) + (grade !== 'all' ? 1 : 0) + (lang !== 'all' ? 1 : 0) + (category !== 'all' ? 1 : 0);

  const resetFilters = () => {
    setQuery('');
    setDateRange('all');
    setGrade('all');
    setLang('all');
    setCategory('all');
  };

  // P0/FUNC-06 & UI-46 + P0.1/R3-1: item backend menampilkan skor & status
  // TERSIMPAN dari backend; PROCESSING/FAILED tampil sebagai status tanpa
  // skor placeholder. Mesin lokal hanya untuk audit offline di browser ini.
  const rows = useMemo<HistoryRow[]>(() => buildHistoryRows(audits), [audits]);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = rows.filter((row) => {
      const { audit, result } = row;
      const id = audit?.id || '';
      const title = audit?.title || '';
      const text = audit?.text || '';
      const createdAt = audit?.createdAt || new Date().toISOString();
      const language = audit?.language || 'id';

      if (q && !`${id} ${title} ${text}`.toLowerCase().includes(q)) return false;
      if (!inDateRange(createdAt, dateRange)) return false;
      // P0.1/R3-1: baris pending (PROCESSING/FAILED) tidak punya grade — tidak
      // ikut filter grade.
      if (grade !== 'all' && rowGrade(row) !== grade) return false;
      if (lang !== 'all' && language !== lang) return false;
      // Filter kategori hanya bermakna untuk audit lokal (temuan detail tidak
      // tersedia pada payload riwayat backend).
      if (category !== 'all' && !(result && result.findings.some((f) => f.category === category))) return false;
      return true;
    });

    return [...list].sort((a, b) => {
      const aDate = a.audit?.createdAt || '';
      const bDate = b.audit?.createdAt || '';
      switch (sort) {
        case 'oldest':
          return aDate.localeCompare(bDate);
        case 'score-desc':
          return rowScore(b) - rowScore(a);
        case 'score-asc':
          return rowScore(a) - rowScore(b);
        default:
          return bDate.localeCompare(aDate);
      }
    });
  }, [rows, query, dateRange, grade, lang, category, sort]);

  const remove = (id: string) => {
    deleteAudit(id);
    toast(t('history.deleted', { id }));
  };

  const removeAll = () => {
    if (!window.confirm(t('history.confirm_delete_all'))) return;
    clearAudits();
    toast(t('history.all_deleted'));
  };

  return (
    <>
      <PageHeader
        crumb={t('history.crumb')}
        title={t('history.title')}
        subtitle={
          audits.length > 0
            ? t('history.subtitle_count', { visible: visible.length, total: audits.length })
            : t('history.subtitle_empty')
        }
        right={
          <div className="flex items-center gap-2.5">
            <label className="relative">
              <span className="sr-only">{t('history.search_sr')}</span>
              <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted" aria-hidden />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={t('history.search_placeholder')}
                className="field h-10 w-[230px] rounded-full pl-10 text-[13px]"
              />
            </label>
            {audits.length > 0 && (
              <button type="button" onClick={removeAll} className="btn-ghost h-10 rounded-full px-4 text-[13px] text-rose-600 dark:text-rose-400">
                <Trash2 size={14} aria-hidden /> {t('history.delete_all')}
              </button>
            )}
          </div>
        }
      />

      {audits.length > 0 && (
        <div className="card mb-5 flex flex-wrap items-center gap-3 p-3">
          <select aria-label={t('history.filter_date_aria')} value={dateRange} onChange={(e) => setDateRange(e.target.value as DateFilter)} className="field h-10 w-auto rounded-full px-4 text-[13px]">
            {DATE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>

          <select aria-label={t('history.filter_grade_aria')} value={grade} onChange={(e) => setGrade(e.target.value as Grade | 'all')} className="field h-10 w-auto rounded-full px-4 text-[13px]">
            <option value="all">{t('history.grade_all')}</option>
            {(['excellent', 'good', 'needs-improvement', 'poor'] as Grade[]).map((g) => (
              <option key={g} value={g}>{gradeLabel(g, uiLocale)}</option>
            ))}
          </select>

          <select aria-label={t('history.filter_lang_aria')} value={lang} onChange={(e) => setLang(e.target.value as LangFilter)} className="field h-10 w-auto rounded-full px-4 text-[13px]">
            <option value="all">{t('history.lang_all')}</option>
            <option value="id">{t('history.lang_id')}</option>
            <option value="en">{t('history.lang_en')}</option>
          </select>

          <select aria-label={t('history.filter_category_aria')} value={category} onChange={(e) => setCategory(e.target.value as Category | 'all')} className="field h-10 w-auto rounded-full px-4 text-[13px]">
            <option value="all">{t('history.category_all')}</option>
            {(['ambiguity', 'non-testable', 'incomplete', 'weak-directive', 'passive-voice'] as Category[]).map((c) => (
              <option key={c} value={c}>{categoryLabelT(c, t)}</option>
            ))}
          </select>

          <select aria-label={t('history.filter_sort_aria')} value={sort} onChange={(e) => setSort(e.target.value as SortKey)} className="field h-10 w-auto rounded-full px-4 text-[13px] sm:ml-auto">
            <option value="newest">{t('history.sort_newest')}</option>
            <option value="oldest">{t('history.sort_oldest')}</option>
            <option value="score-desc">{t('history.sort_score_desc')}</option>
            <option value="score-asc">{t('history.sort_score_asc')}</option>
          </select>

          {(activeFilters > 0 || query) && (
            <button type="button" onClick={resetFilters} className="btn-ghost h-10 px-4 text-[13px]">
              <X size={14} aria-hidden /> {t('history.reset')}{activeFilters > 0 ? ` (${activeFilters})` : ''}
            </button>
          )}
        </div>
      )}

      {audits.length === 0 ? (
        <div className="card flex flex-col items-center gap-3 px-8 py-16 text-center">
          <History size={30} strokeWidth={1.5} className="text-muted" aria-hidden />
          <h2 className="text-[18px] font-semibold">{t('history.empty_title')}</h2>
          <p className="max-w-[360px] text-[14px] text-muted">
            {t('history.empty_desc')}
          </p>
          <Link href="/editor" className="btn-primary mt-2 h-11 px-6 text-[14px]">
            {t('history.open_editor')} <ArrowRight size={15} aria-hidden />
          </Link>
        </div>
      ) : visible.length === 0 ? (
        <div className="card px-8 py-12 text-center text-[14px] text-muted">
          {t('history.no_match')}{' '}
          <button type="button" onClick={resetFilters} className="font-medium text-accent hover:underline">
            {t('history.reset_filter')}
          </button>
        </div>
      ) : (
        <ul className="card divide-y divide-line/[0.07] overflow-hidden p-2">
          {visible.map((row) => {
            const { audit, result } = row;
            const grade = rowGrade(row);
            return (
            <li key={audit.id} className="flex flex-wrap items-center gap-x-5 gap-y-3 rounded-2xl px-4 py-4 transition hover:bg-line/[0.03]">
              <Link href={`/audit/${audit.id}`} className="min-w-0 flex-1 basis-[260px]">
                <p className="flex items-center gap-2.5 text-[12px] text-muted">
                  <span className="font-mono">{audit.id.startsWith('AUD-') ? audit.id : `AUD-${audit.id}`}</span>
                  <span aria-hidden>·</span>
                  {formatDate(audit.createdAt, uiLocale)}
                  <span aria-hidden>·</span>
                  {audit.language === 'en' ? 'EN' : 'ID'}
                  {audit.requestedEvaluator && (
                    <>
                      <span aria-hidden>·</span>
                      <span>
                        {t(`evaluator.${audit.requestedEvaluator}`) !== `evaluator.${audit.requestedEvaluator}`
                          ? t(`evaluator.${audit.requestedEvaluator}`)
                          : audit.requestedEvaluator}
                      </span>
                    </>
                  )}
                  {audit.modelVersion && (
                    <>
                      <span aria-hidden>·</span>
                      <code className="text-[11px]">{audit.modelVersion}</code>
                    </>
                  )}
                </p>
                <p className="mt-1 truncate text-[15px] font-semibold">{audit.title || t('history.fallback_title')}</p>
                <p className="mt-0.5 truncate text-[12.5px] text-muted">{(audit.text || audit.title || '').replace(/\s+/g, ' ')}</p>
              </Link>

              <div className="flex items-center gap-4">
                <span className="text-[12.5px] text-muted">
                  {row.pendingStatus
                    ? row.pendingStatus === 'PROCESSING'
                      ? t('history.processing_status')
                      : row.pendingStatus === 'FAILED'
                        ? t('history.failed_status')
                        : row.pendingStatus
                    : result
                      ? t('history.findings_count', { n: result.findings.length })
                      : t('history.score_from_backend')}
                </span>
                {row.pendingStatus ? (
                  // P0.1/R3-1: status, bukan skor placeholder 0.0.
                  <span className="pill bg-line/[0.06] text-muted">
                    {row.pendingStatus === 'FAILED' ? t('history.status_failed') : t('history.status_processing')}
                  </span>
                ) : (
                  <span className={`pill ${GRADE_BADGE[grade as Grade]}`}>
                    {rowScore(row)} · {gradeLabel(grade as Grade, uiLocale)}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-1">
                <Link href={`/audit/${audit.id}`} className="btn-ghost h-9 rounded-full px-3.5 text-[12.5px] shadow-none">
                  {t('history.open')} <ArrowRight size={13} aria-hidden />
                </Link>
                <button
                  type="button"
                  onClick={() => remove(audit.id)}
                  aria-label={t('history.delete_aria', { id: audit.id })}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-xl text-muted transition hover:bg-rose-500/10 hover:text-rose-600"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
