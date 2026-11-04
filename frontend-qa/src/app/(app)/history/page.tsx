'use client';

import { ArrowRight, History, Search, Trash2, X } from 'lucide-react';
import Link from 'next/link';
import { useMemo, useState } from 'react';
import { PageHeader } from '@/components/app-shell';
import { useToast } from '@/components/providers';
import { analyze } from '@/lib/analyzer';
import type { Category, Grade } from '@/lib/analyzer';
import { clearAudits, deleteAudit, useAudits } from '@/lib/audits';
import { CATEGORY_LABEL, GRADE_BADGE, GRADE_LABEL, formatDate } from '@/lib/format';

type DateFilter = 'all' | 'today' | '7d' | '30d';
type LangFilter = 'all' | 'id' | 'en';
type SortKey = 'newest' | 'oldest' | 'score-desc' | 'score-asc';

const DATE_OPTIONS: Array<{ value: DateFilter; label: string }> = [
  { value: 'all', label: 'Semua tanggal' },
  { value: 'today', label: 'Hari ini' },
  { value: '7d', label: '7 hari terakhir' },
  { value: '30d', label: '30 hari terakhir' },
];

const DAY_MS = 24 * 60 * 60 * 1000;

function inDateRange(iso: string, range: DateFilter): boolean {
  if (range === 'all') return true;
  if (range === 'today') return new Date(iso).toDateString() === new Date().toDateString();
  return Date.now() - new Date(iso).getTime() <= (range === '7d' ? 7 : 30) * DAY_MS;
}

export default function HistoryPage() {
  const audits = useAudits();
  const toast = useToast();
  const [query, setQuery] = useState('');
  const [dateRange, setDateRange] = useState<DateFilter>('all');
  const [grade, setGrade] = useState<Grade | 'all'>('all');
  const [lang, setLang] = useState<LangFilter>('all');
  const [category, setCategory] = useState<Category | 'all'>('all');
  const [sort, setSort] = useState<SortKey>('newest');

  const activeFilters =
    (dateRange !== 'all' ? 1 : 0) + (grade !== 'all' ? 1 : 0) + (lang !== 'all' ? 1 : 0) + (category !== 'all' ? 1 : 0);

  const resetFilters = () => {
    setQuery('');
    setDateRange('all');
    setGrade('all');
    setLang('all');
    setCategory('all');
  };

  const rows = useMemo(
    () => audits.map((a) => ({ audit: a, result: analyze(a.text, a.language) })),
    [audits],
  );

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = rows.filter(({ audit, result }) => {
      if (q && !`${audit.id} ${audit.title} ${audit.text}`.toLowerCase().includes(q)) return false;
      if (!inDateRange(audit.createdAt, dateRange)) return false;
      if (grade !== 'all' && result.grade !== grade) return false;
      if (lang !== 'all' && audit.language !== lang) return false;
      if (category !== 'all' && !result.findings.some((f) => f.category === category)) return false;
      return true;
    });
    return [...list].sort((a, b) => {
      switch (sort) {
        case 'oldest':
          return a.audit.createdAt.localeCompare(b.audit.createdAt);
        case 'score-desc':
          return b.result.score - a.result.score;
        case 'score-asc':
          return a.result.score - b.result.score;
        default:
          return b.audit.createdAt.localeCompare(a.audit.createdAt);
      }
    });
  }, [rows, query, dateRange, grade, lang, category, sort]);

  const remove = (id: string) => {
    deleteAudit(id);
    toast(`${id} dihapus dari riwayat.`);
  };

  const removeAll = () => {
    if (!window.confirm('Hapus seluruh riwayat audit di browser ini? Tindakan ini tidak dapat dibatalkan.')) return;
    clearAudits();
    toast('Seluruh riwayat dihapus.');
  };

  return (
    <>
      <PageHeader
        crumb="Workspace / Riwayat"
        title="History Audit"
        subtitle={
          audits.length > 0
            ? `Menampilkan ${visible.length} dari ${audits.length} audit di browser ini.`
            : 'Seluruh audit yang pernah Anda jalankan di browser ini.'
        }
        right={
          <div className="flex items-center gap-2.5">
            <label className="relative">
              <span className="sr-only">Cari audit</span>
              <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted" aria-hidden />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Cari ID, judul, atau isi…"
                className="field h-10 w-[230px] rounded-full pl-10 text-[13px]"
              />
            </label>
            {audits.length > 0 && (
              <button type="button" onClick={removeAll} className="btn-ghost h-10 rounded-full px-4 text-[13px] text-rose-600 dark:text-rose-400">
                <Trash2 size={14} aria-hidden /> Hapus semua
              </button>
            )}
          </div>
        }
      />

      {audits.length > 0 && (
        <div className="card mb-5 flex flex-wrap items-center gap-3 p-3">
          <select aria-label="Filter tanggal" value={dateRange} onChange={(e) => setDateRange(e.target.value as DateFilter)} className="field h-10 w-auto rounded-full px-4 text-[13px]">
            {DATE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>

          <select aria-label="Filter grade" value={grade} onChange={(e) => setGrade(e.target.value as Grade | 'all')} className="field h-10 w-auto rounded-full px-4 text-[13px]">
            <option value="all">Semua grade</option>
            {(Object.keys(GRADE_LABEL) as Grade[]).map((g) => (
              <option key={g} value={g}>{GRADE_LABEL[g]}</option>
            ))}
          </select>

          <select aria-label="Filter bahasa" value={lang} onChange={(e) => setLang(e.target.value as LangFilter)} className="field h-10 w-auto rounded-full px-4 text-[13px]">
            <option value="all">Semua bahasa</option>
            <option value="id">Indonesia</option>
            <option value="en">English</option>
          </select>

          <select aria-label="Filter kategori temuan" value={category} onChange={(e) => setCategory(e.target.value as Category | 'all')} className="field h-10 w-auto rounded-full px-4 text-[13px]">
            <option value="all">Semua kategori temuan</option>
            {(Object.keys(CATEGORY_LABEL) as Category[]).map((c) => (
              <option key={c} value={c}>{CATEGORY_LABEL[c]}</option>
            ))}
          </select>

          <select aria-label="Urutkan" value={sort} onChange={(e) => setSort(e.target.value as SortKey)} className="field h-10 w-auto rounded-full px-4 text-[13px] sm:ml-auto">
            <option value="newest">Terbaru</option>
            <option value="oldest">Terlama</option>
            <option value="score-desc">Skor tertinggi</option>
            <option value="score-asc">Skor terendah</option>
          </select>

          {(activeFilters > 0 || query) && (
            <button type="button" onClick={resetFilters} className="btn-ghost h-10 px-4 text-[13px]">
              <X size={14} aria-hidden /> Reset{activeFilters > 0 ? ` (${activeFilters})` : ''}
            </button>
          )}
        </div>
      )}

      {audits.length === 0 ? (
        <div className="card flex flex-col items-center gap-3 px-8 py-16 text-center">
          <History size={30} strokeWidth={1.5} className="text-muted" aria-hidden />
          <h2 className="text-[18px] font-semibold">Belum ada riwayat audit</h2>
          <p className="max-w-[360px] text-[14px] text-muted">
            Jalankan analisis dari editor, hasilnya akan tersimpan di sini.
          </p>
          <Link href="/editor" className="btn-primary mt-2 h-11 px-6 text-[14px]">
            Buka editor <ArrowRight size={15} aria-hidden />
          </Link>
        </div>
      ) : visible.length === 0 ? (
        <div className="card px-8 py-12 text-center text-[14px] text-muted">
          Tidak ada audit yang cocok dengan pencarian atau filter ini.{' '}
          <button type="button" onClick={resetFilters} className="font-medium text-accent hover:underline">
            Reset filter
          </button>
        </div>
      ) : (
        <ul className="card divide-y divide-line/[0.07] overflow-hidden p-2">
          {visible.map(({ audit, result }) => (
            <li key={audit.id} className="flex flex-wrap items-center gap-x-5 gap-y-3 rounded-2xl px-4 py-4 transition hover:bg-line/[0.03]">
              <Link href={`/audit/${audit.id}`} className="min-w-0 flex-1 basis-[260px]">
                <p className="flex items-center gap-2.5 text-[12px] text-muted">
                  <span className="font-mono">{audit.id}</span>
                  <span aria-hidden>·</span>
                  {formatDate(audit.createdAt)}
                  <span aria-hidden>·</span>
                  {audit.language === 'id' ? 'ID' : 'EN'}
                </p>
                <p className="mt-1 truncate text-[15px] font-semibold">{audit.title}</p>
                <p className="mt-0.5 truncate text-[12.5px] text-muted">{audit.text.replace(/\s+/g, ' ')}</p>
              </Link>

              <div className="flex items-center gap-4">
                <span className="text-[12.5px] text-muted">{result.findings.length} temuan</span>
                <span className={`pill ${GRADE_BADGE[result.grade]}`}>
                  {result.score} · {GRADE_LABEL[result.grade]}
                </span>
              </div>

              <div className="flex items-center gap-1">
                <Link href={`/audit/${audit.id}`} className="btn-ghost h-9 rounded-full px-3.5 text-[12.5px] shadow-none">
                  Buka <ArrowRight size={13} aria-hidden />
                </Link>
                <button
                  type="button"
                  onClick={() => remove(audit.id)}
                  aria-label={`Hapus ${audit.id}`}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-xl text-muted transition hover:bg-rose-500/10 hover:text-rose-600"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}