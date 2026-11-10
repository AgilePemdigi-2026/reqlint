'use client';

import {
  CalendarDays,
  ChevronDown,
  Copy,
  Download,
  RefreshCw,
  FileSearch,
  CheckCircle2,
  Cpu,
  Layers,
  ArrowRight,
} from 'lucide-react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';
import { PageHeader } from '@/components/app-shell';
import { DiffViewer } from '@/components/audit/diff-viewer';
import { FindingsTable } from '@/components/audit/findings-table';
import { AcceptanceCard, RevisionCard } from '@/components/audit/revision-cards';
import { ScoreCard } from '@/components/audit/score-card';
import { SummaryCard } from '@/components/audit/summary-card';
import { Popover } from '@/components/popover';
import { useToast } from '@/components/providers';
import {
  adaptBackendAuditToAnalysisResult,
  acceptanceCriteria,
  analyze,
  revise,
  type AcceptanceCriteria,
  type AnalysisResult,
  type Revision,
} from '@/lib/analyzer';
import { createAudit, setDraft, touchAudit, useAudit } from '@/lib/audits';
import {
  apiApplyAudit,
  apiDownloadExport,
  apiGetAuditDetail,
  apiGetAuditStatus,
  apiReanalyzeAudit,
  type BackendAuditDetail,
} from '@/lib/api';
import { buildExport, copyText, download, toMarkdown, type ExportFormat } from '@/lib/export';
import { formatDate } from '@/lib/format';
import { useT, useUILocale } from '@/lib/i18n';

const EXPORTS: Array<{ format: ExportFormat; label: string }> = [
  { format: 'md', label: 'Markdown (.md)' },
  { format: 'csv', label: 'CSV (.csv)' },
  { format: 'json', label: 'JSON (.json)' },
];

export default function AuditPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const toast = useToast();
  const t = useT();
  const locale = useUILocale();

  const localAudit = useAudit(id);

  const [backendDetail, setBackendDetail] = useState<BackendAuditDetail | null>(null);
  const [loadingBackend, setLoadingBackend] = useState<boolean>(true);
  const [pollingStage, setPollingStage] = useState<string>('Memulai audit kebutuhan...');
  const [applyingRevision, setApplyingRevision] = useState<boolean>(false);
  const [reanalyzing, setReanalyzing] = useState<boolean>(false);

  // 1. Ambil detail audit dari Backend FastAPI (Polling sampai COMPLETED/PARTIAL)
  useEffect(() => {
    let cancelled = false;
    let timer: NodeJS.Timeout | null = null;

    async function fetchAudit() {
      if (!id || id.startsWith('AUD-')) {
        setLoadingBackend(false);
        return;
      }

      try {
        setLoadingBackend(true);
        const res = await apiGetAuditDetail(id);
        if (cancelled) return;

        if (res.data) {
          if (res.data.status_audit === 'PROCESSING') {
            setPollingStage('Stage 1: Pengecekan Sintaks Connextra & Bau Teks...');
            // Polling status secara berkala
            timer = setInterval(async () => {
              try {
                const statusRes = await apiGetAuditStatus(id);
                if (cancelled) return;

                if (statusRes.data?.stage2_status === 'PROCESSING') {
                  setPollingStage('Stage 2: Model Klasifikasi INVEST (Machine Learning)...');
                }

                if (statusRes.data?.status_audit === 'COMPLETED' || statusRes.data?.status_audit === 'PARTIAL') {
                  if (timer) clearInterval(timer);
                  const finalDetail = await apiGetAuditDetail(id);
                  if (cancelled) return;
                  if (finalDetail.data) {
                    setBackendDetail(finalDetail.data);
                    setLoadingBackend(false);
                  }
                }
              } catch {
                if (timer) clearInterval(timer);
                if (!cancelled) setLoadingBackend(false);
              }
            }, 1200);
          } else {
            setBackendDetail(res.data);
            setLoadingBackend(false);
          }
        }
      } catch (err) {
        console.warn('Gagal memuat audit dari backend, beralih ke analisis lokal:', err);
        if (!cancelled) setLoadingBackend(false);
      }
    }

    fetchAudit();

    return () => {
      cancelled = true;
      if (timer) clearInterval(timer);
    };
  }, [id]);

  // 2. Adaptasi Model Backend ke Model Frontend (Local Fallback Ready)
  const adapted = useMemo(() => {
    if (!backendDetail) return null;
    return adaptBackendAuditToAnalysisResult(backendDetail);
  }, [backendDetail]);

  const result: AnalysisResult | null = useMemo(() => {
    if (adapted) return adapted.result;
    if (localAudit) return analyze(localAudit.text, localAudit.language);
    return null;
  }, [adapted, localAudit]);

  const revision: Revision | null = useMemo(() => {
    if (adapted) return adapted.revision;
    if (localAudit) return revise(localAudit.text, localAudit.language);
    return null;
  }, [adapted, localAudit]);

  const criteria: AcceptanceCriteria | null = useMemo(() => {
    if (adapted) return adapted.criteria;
    if (localAudit && revision) {
      return acceptanceCriteria(revision.changed ? revision.text : localAudit.text, localAudit.language);
    }
    return null;
  }, [adapted, localAudit, revision]);

  const auditTitle = backendDetail?.judul_klausul ?? localAudit?.title ?? `Audit #${id}`;
  const auditCreatedAt = backendDetail?.tanggal_audit ?? localAudit?.createdAt ?? new Date().toISOString();
  const currentText = backendDetail?.diff?.original?.teks ?? localAudit?.text ?? '';
  const currentLang = result?.language ?? localAudit?.language ?? 'id';

  // 3. Tampilan Loading Saat Pipeline Berjalan
  if (loadingBackend && !localAudit) {
    return (
      <div className="card mx-auto flex max-w-[560px] flex-col items-center gap-4 px-8 py-16 text-center">
        <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-accent/10 text-accent">
          <Cpu size={32} className="animate-pulse" />
          <span className="absolute -right-1 -top-1 flex h-4 w-4">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-accent"></span>
          </span>
        </div>
        <div>
          <h2 className="text-[20px] font-semibold text-ink">{t('audit.running_pipeline')}</h2>
          <p className="mt-1.5 text-[14px] text-muted">{pollingStage}</p>
        </div>

        <div className="w-full max-w-sm rounded-xl border border-line/[0.08] bg-line/[0.02] p-4 text-left space-y-2.5">
          <div className="flex items-center justify-between text-[12px]">
            <span className="flex items-center gap-2">
              <CheckCircle2 size={14} className="text-emerald-500" /> {t('audit.stage1_name')}
            </span>
            <span className="text-muted font-mono">{t('audit.stage_done')}</span>
          </div>
          <div className="flex items-center justify-between text-[12px]">
            <span className="flex items-center gap-2">
              <RefreshCw size={14} className="animate-spin text-accent" /> {t('audit.stage2_name')}
            </span>
            <span className="text-accent font-mono">{t('audit.stage_processing')}</span>
          </div>
        </div>
      </div>
    );
  }

  // 4. Tampilan Audit Tidak Ditemukan
  if (!result || !revision) {
    return (
      <div className="card mx-auto flex max-w-[520px] flex-col items-center gap-3 px-8 py-14 text-center">
        <FileSearch size={30} strokeWidth={1.5} className="text-muted" aria-hidden />
        <h1 className="text-[20px] font-semibold">{t('audit.not_found_title')}</h1>
        <p className="text-[14px] text-muted">
          {t('audit.not_found_desc', { id: String(id) })}
        </p>
        <Link href="/editor" className="btn-primary mt-2 h-11 px-6 text-[14px]">
          {t('audit.back_editor')}
        </Link>
      </div>
    );
  }

  const openInEditor = (text: string) => {
    setDraft({ text, language: currentLang });
    router.push('/editor');
  };

  /** Terapkan Revisi Rekomendasi AI (1-Click Apply) */
  const applyRevision = async () => {
    if (backendDetail) {
      setApplyingRevision(true);
      try {
        const res = await apiApplyAudit(backendDetail.id_audit, ['rewrite', 'acceptance_criteria']);
        if (res.data) {
          toast(t('audit.toast_apply_success'));
          // Segarkan data audit
          const refreshed = await apiGetAuditDetail(backendDetail.id_audit);
          if (refreshed.data) setBackendDetail(refreshed.data);
          if (res.data.konten_revisi) {
            setDraft({ text: res.data.konten_revisi, language: currentLang });
          }
        }
      } catch (err) {
        toast('Gagal menerapkan revisi ke backend. Menjalankan fallback lokal.');
      } finally {
        setApplyingRevision(false);
      }
      return;
    }

    // Fallback lokal
    const next = createAudit(revision.text, currentLang);
    setDraft({ text: revision.text, language: currentLang });
    toast('Revisi diterapkan. Menampilkan hasil audit baru.');
    router.push(`/audit/${next.id}`);
  };

  /** Jalankan Ulang Analisis */
  const rerun = async () => {
    if (backendDetail) {
      setReanalyzing(true);
      try {
        toast('Analisis ulang dimulai di backend...');
        await apiReanalyzeAudit(backendDetail.id_audit);
        setLoadingBackend(true);
        // Refresh detail
        const refreshed = await apiGetAuditDetail(backendDetail.id_audit);
        if (refreshed.data) setBackendDetail(refreshed.data);
      } catch (err) {
        toast('Gagal memulai analisis ulang di backend.');
      } finally {
        setReanalyzing(false);
        setLoadingBackend(false);
      }
      return;
    }

    if (localAudit) {
      touchAudit(localAudit.id);
      toast('Analisis dijalankan ulang dengan aturan terbaru.');
    }
  };

  /** Salin Markdown Hasil Audit */
  const copyResult = async () => {
    const dummyAudit = {
      id: String(id),
      seq: 1,
      createdAt: auditCreatedAt,
      title: auditTitle,
      text: currentText,
      language: currentLang,
    };
    const ok = await copyText(toMarkdown(dummyAudit, result, revision));
    toast(ok ? t('audit.toast_copied') : 'Gagal menyalin. Coba gunakan fitur Export.');
  };

  /** Ekspor Dokumen Resmi */
  const exportAs = async (format: ExportFormat) => {
    if (backendDetail && (format === 'md' || format === 'json')) {
      try {
        toast(`Mengunduh laporan ${format.toUpperCase()} dari backend...`);
        const { blob, filename } = await apiDownloadExport(backendDetail.id_audit, format);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
        toast(`${filename} berhasil diunduh.`);
        return;
      } catch (err) {
        console.warn('Ekspor backend gagal, beralih ke generator lokal:', err);
      }
    }

    // Generator lokal fallback
    const dummyAudit = {
      id: String(id),
      seq: 1,
      createdAt: auditCreatedAt,
      title: auditTitle,
      text: currentText,
      language: currentLang,
    };
    const { filename, mime, content } = buildExport(format, dummyAudit, result, revision);
    download(filename, mime, content);
    toast(`${filename} berhasil diunduh.`);
  };

  return (
    <>
      <PageHeader
        crumb={t('audit.crumb')}
        title={t('audit.title')}
        subtitle={
          <span className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[12.5px]">
            <span className="font-mono bg-line/[0.06] px-2 py-0.5 rounded text-ink font-medium">#{id}</span>
            <span aria-hidden>·</span>
            <span className="inline-flex items-center gap-1.5">
              <CalendarDays size={13} aria-hidden /> {formatDate(auditCreatedAt, locale)}
            </span>
            <span aria-hidden>·</span>
            <span className="truncate max-w-[280px] font-medium">{auditTitle}</span>
            {backendDetail && (
              <>
                <span aria-hidden>·</span>
                <span className="pill text-[10.5px] bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20 font-medium">
                  Pipeline 2-Tahap NLP + INVEST
                </span>
              </>
            )}
          </span>
        }
        right={
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              onClick={rerun}
              disabled={reanalyzing}
              className="btn-ghost h-10 rounded-full px-4 text-[13px] disabled:opacity-60"
            >
              <RefreshCw size={14} className={reanalyzing ? 'animate-spin' : ''} aria-hidden /> {t('audit.rerun')}
            </button>
            <button type="button" onClick={copyResult} className="btn-ghost h-10 rounded-full px-4 text-[13px]">
              <Copy size={14} aria-hidden /> {t('audit.copy')}
            </button>
            <Popover
              align="right"
              trigger={({ toggle: toggleExp }) => (
                <button type="button" onClick={toggleExp} className="btn-ghost h-10 rounded-full px-4 text-[13px]">
                  <Download size={14} aria-hidden /> {t('audit.export')} <ChevronDown size={13} aria-hidden />
                </button>
              )}
            >
              {(close) =>
                EXPORTS.map((e) => (
                  <button
                    key={e.format}
                    type="button"
                    className="menu-item"
                    onClick={() => {
                      exportAs(e.format);
                      close();
                    }}
                  >
                    {e.label}
                  </button>
                ))
              }
            </Popover>
            <button
              type="button"
              onClick={() => openInEditor(currentText)}
              className="btn-primary h-10 rounded-full px-5 text-[13px]"
            >
              {t('audit.open_editor')} <ArrowRight size={14} aria-hidden />
            </button>
          </div>
        }
      />

      <div className="space-y-6">
        {/* Row 1: Scorecard & Summary */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-[340px_1fr]">
          <ScoreCard result={result} />
          <SummaryCard result={result} />
        </div>

        {/* Row 2: Temuan Cacat */}
        <FindingsTable findings={result.findings} onOpenEditor={() => openInEditor(currentText)} />

        {/* Row 3: Rekomendasi AI & Kriteria Penerimaan */}
        <div className="grid gap-6 md:grid-cols-2">
          <RevisionCard
            revision={revision}
            remaining={result.findings.length}
            onApply={applyRevision}
            onEdit={() => openInEditor(revision.text)}
          />
          {criteria && <AcceptanceCard criteria={criteria} />}
        </div>

        {/* Row 4: Diff Viewer */}
        {revision.changed && (
          <DiffViewer
            original={currentText}
            revised={revision.text}
            originalScore={result.score}
            revisedScore={backendDetail?.diff?.revised?.skor ?? (result ? Math.min(100, result.score + 15) : undefined)}
          />
        )}
      </div>
    </>
  );
}
