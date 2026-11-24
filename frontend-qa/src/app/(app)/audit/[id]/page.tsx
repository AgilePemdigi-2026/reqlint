'use client';

import {
  CalendarDays,
  ChevronDown,
  Copy,
  Download,
  RefreshCw,
  FileSearch,
  ShieldAlert,
  Cpu,
  CheckCircle2,
  XCircle,
  MinusCircle,
  ArrowRight,
} from 'lucide-react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { PageHeader } from '@/components/app-shell';
import { DiffViewer } from '@/components/audit/diff-viewer';
import { FindingsTable } from '@/components/audit/findings-table';
import { DimensionResults } from '@/components/audit/dimension-results';
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
import { resolveAiSuggestionStatus } from '@/lib/ai-status';
import { useT, useUILocale, translations } from '@/lib/i18n';
import axios from 'axios';
import {
  apiApplyAudit,
  apiDownloadExport,
  apiGetAuditDetail,
  apiGetAuditStatus,
  apiReanalyzeAudit,
  extractApiError,
  type BackendAuditDetail,
} from '@/lib/api';
import { buildExport, copyText, download, toMarkdown, type ExportFormat } from '@/lib/export';
import { formatDate } from '@/lib/format';

const EXPORTS: Array<{ format: ExportFormat; label: string }> = [
  { format: 'md', label: 'Markdown (.md)' },
  { format: 'csv', label: 'CSV (.csv)' },
  { format: 'json', label: 'JSON (.json)' },
];

/**
 * Task 09/Phase 5: pesan galat provider dilokalkan berdasarkan kode mesin
 * dari backend (evaluator_error.code). Pesan mentah backend hanya fallback
 * bila kode tidak dikenal — kode tidak pernah menampilkan kredensial.
 */
function localizedEvaluatorError(code: string | null | undefined, fallback: string, t: (k: string) => string): string {
  if (code && translations[`llm_error.${code}`]) return t(`llm_error.${code}`);
  return fallback;
}

type PagePhase = 'loading' | 'processing' | 'ready' | 'error';
type LoadErrorKind = 'network' | 'auth' | 'not_found' | 'http';
interface LoadErrorState {
  kind: LoadErrorKind;
  message?: string;
}

export default function AuditPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const toast = useToast();
  const t = useT();
  const uiLocale = useUILocale();

  // Local browser record. For AUD-* ids this IS the audit (offline rule-based
  // engine). For numeric backend ids it is only a cache of the submission —
  // Task 10: it must NEVER be rendered as a substitute for the backend result.
  const localAudit = useAudit(id);
  const isLocalAuditId = id.startsWith('AUD-');

  const [backendDetail, setBackendDetail] = useState<BackendAuditDetail | null>(null);
  const [phase, setPhase] = useState<PagePhase>(isLocalAuditId ? 'ready' : 'loading');
  const [loadError, setLoadError] = useState<LoadErrorState | null>(null);
  const [pollingStage, setPollingStage] = useState<string>('');
  const [applyingRevision, setApplyingRevision] = useState<boolean>(false);
  const [reanalyzing, setReanalyzing] = useState<boolean>(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  /** Task 10 Phase 4: single load/poll lifecycle used by initial load,
   * reanalysis and retry. Stops polling on any terminal state. */
  const loadAudit = useCallback(async () => {
    clearTimer();
    setPhase('loading');
    setLoadError(null);
    setPollingStage('');
    try {
      const res = await apiGetAuditDetail(id);
      const detail = res.data;
      if (!detail) {
        setLoadError({ kind: 'not_found' });
        setPhase('error');
        return;
      }
      if (detail.status_audit === 'PROCESSING') {
        setPollingStage(t('audit.poll_stage1'));
        setPhase('processing');
        timerRef.current = setInterval(async () => {
          try {
            const statusRes = await apiGetAuditStatus(id);
            const s = statusRes.data;
            if (s?.stage1_ready) setPollingStage(t('audit.poll_stage2'));
            if (s?.status_audit && s.status_audit !== 'PROCESSING') {
              clearTimer();
              const finalDetail = await apiGetAuditDetail(id);
              if (finalDetail.data) {
                setBackendDetail(finalDetail.data);
                setPhase('ready');
              } else {
                setPhase('error');
              }
            }
          } catch (pollErr) {
            console.warn('Polling error:', pollErr);
          }
        }, 1000);
      } else {
        setBackendDetail(detail);
        setPhase('ready');
      }
    } catch (err) {
      console.warn('Gagal memuat audit dari backend:', err);
      // Classify the actual failure rather than misreporting HTTP 401/404/500
      // as "Backend tidak dapat dihubungi". Never fall back to local Rule-Based.
      if (axios.isAxiosError(err)) {
        const status = err.response?.status;
        if (status === 401 || status === 403) {
          setLoadError({ kind: 'auth', message: extractApiError(err).message });
        } else if (status === 404) {
          setLoadError({ kind: 'not_found', message: extractApiError(err).message });
        } else if (err.response) {
          setLoadError({ kind: 'http', message: extractApiError(err).message });
        } else {
          setLoadError({ kind: 'network' });
        }
      } else {
        setLoadError({ kind: 'network' });
      }
      setPhase('error');
    }
  }, [id, t]);

  useEffect(() => {
    if (isLocalAuditId) return; // offline browser audit — nothing to load
    loadAudit();
    return clearTimer;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, isLocalAuditId]);

  const adapted = useMemo(() => {
    if (backendDetail) {
      return adaptBackendAuditToAnalysisResult(backendDetail);
    }
    return null;
  }, [backendDetail]);

  const localResult: AnalysisResult | null = useMemo(() => {
    if (!isLocalAuditId || !localAudit) return null;
    return analyze(localAudit.text, localAudit.language);
  }, [isLocalAuditId, localAudit]);

  const localRevision: Revision | null = useMemo(() => {
    if (!isLocalAuditId || !localAudit) return null;
    return revise(localAudit.text, localAudit.language);
  }, [isLocalAuditId, localAudit]);

  const localCriteria: AcceptanceCriteria | null = useMemo(() => {
    if (!isLocalAuditId || !localAudit || !localRevision) return null;
    return acceptanceCriteria(localRevision.changed ? localRevision.text : localAudit.text, localAudit.language);
  }, [isLocalAuditId, localAudit, localRevision]);

  const auditTitle = backendDetail?.judul_klausul ?? localAudit?.title ?? t('history.audit_num', { id });
  const auditCreatedAt = backendDetail?.tanggal_audit ?? localAudit?.createdAt ?? new Date().toISOString();
  const currentText = backendDetail?.diff?.original?.teks ?? localAudit?.text ?? '';
  const currentLang = adapted?.result?.language ?? localResult?.language ?? localAudit?.language ?? 'id';

  // The evaluator the user REQUESTED (shown during processing and in the banner).
  const requestedEvaluator = (backendDetail?.requested_evaluator ?? localAudit?.requestedEvaluator ?? null) as
    | string
    | null;
  const requestedName = requestedEvaluator
    ? t(`evaluator.${requestedEvaluator}`) !== `evaluator.${requestedEvaluator}`
      ? t(`evaluator.${requestedEvaluator}`)
      : requestedEvaluator
    : null;

  // ── Backend audit states (Task 10 lifecycle) ──
  if (!isLocalAuditId && (phase === 'loading' || phase === 'processing')) {
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
          <h2 className="text-[20px] font-semibold text-ink">{t('audit.loading_title')}</h2>
          <p className="mt-1.5 text-[14px] text-muted">{phase === 'processing' ? (pollingStage || t('audit.poll_prepare')) : t('audit.poll_prepare')}</p>
          {requestedName && (
            <p className="mt-2 text-[13px] text-muted">
              {t('audit.processing_requested', { name: requestedName })}
            </p>
          )}
        </div>

        <div className="w-full max-w-sm rounded-xl border border-line/[0.08] bg-line/[0.02] p-4 text-left space-y-2.5">
          <div className="flex items-center justify-between text-[12px]">
            <span className="flex items-center gap-2">
              <CheckCircle2 size={14} className="text-emerald-500" /> {t('audit.stage1_label')}
            </span>
            <span className="text-muted font-mono">{t('audit.stage1_done')}</span>
          </div>
          <div className="flex items-center justify-between text-[12px]">
            <span className="flex items-center gap-2">
              <RefreshCw size={14} className="animate-spin text-accent" /> {t('audit.stage2_label')}
            </span>
            <span className="text-accent font-mono">{t('audit.stage2_processing')}</span>
          </div>
        </div>
      </div>
    );
  }

  if (!isLocalAuditId && phase === 'error') {
    const errKind = loadError?.kind ?? 'network';
    const errTitle =
      errKind === 'auth'
        ? t('audit.auth_error_title')
        : errKind === 'not_found'
          ? t('audit.server_not_found_title')
          : errKind === 'http'
            ? t('audit.http_error_title')
            : t('audit.backend_error_title');
    const errDesc =
      errKind === 'auth'
        ? t('audit.auth_error_desc', { id })
        : errKind === 'not_found'
          ? t('audit.server_not_found_desc', { id })
          : errKind === 'http'
            ? (loadError?.message || t('audit.backend_error_desc', { id }))
            : t('audit.backend_error_desc', { id });

    return (
      <div className="card mx-auto flex max-w-[560px] flex-col items-center gap-4 px-8 py-14 text-center">
        <ShieldAlert size={30} strokeWidth={1.5} className="text-amber-600 dark:text-amber-400" aria-hidden />
        <h1 className="text-[20px] font-semibold">{errTitle}</h1>
        <p className="text-[14px] text-muted">{errDesc}</p>
        <div className="flex flex-wrap items-center justify-center gap-2">
          {errKind === 'auth' ? (
            <Link href="/login" className="btn-primary mt-1 h-11 px-6 text-[14px]">
              {t('audit.auth_login_cta')}
            </Link>
          ) : (
            <button type="button" onClick={() => loadAudit()} className="btn-primary mt-1 h-11 px-6 text-[14px]">
              <RefreshCw size={14} className="mr-1.5 inline" aria-hidden /> {t('audit.backend_error_retry')}
            </button>
          )}
          <Link href="/editor" className="btn-ghost mt-1 h-11 px-6 text-[14px]">
            {t('audit.back_editor')}
          </Link>
        </div>
      </div>
    );
  }

  // ── Terminal state: FAILED evaluation → explicit failure, no score card ──
  if (!isLocalAuditId && phase === 'ready' && backendDetail?.status_audit === 'FAILED') {
    const evaluatorName = requestedName ?? (backendDetail.requested_evaluator as string) ?? '';
    const errorCode = backendDetail.evaluator_error_code ?? backendDetail.evaluator_error?.code ?? null;
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
                <CalendarDays size={13} aria-hidden /> {formatDate(auditCreatedAt, uiLocale)}
              </span>
            </span>
          }
        />
        <div className="card mx-auto flex max-w-[620px] flex-col items-center gap-4 px-8 py-14 text-center">
          <ShieldAlert size={30} strokeWidth={1.5} className="text-rose-600 dark:text-rose-400" aria-hidden />
          <h1 className="text-[20px] font-semibold">{t('audit.failed_title')}</h1>
          <p className="max-w-[520px] text-[14px] text-muted">{t('audit.failed_desc', { name: evaluatorName })}</p>
          {errorCode && (
            <p className="text-[13px] text-red-700 dark:text-red-300" role="alert">
              <strong>{t('audit.eval_unavailable')}:</strong>{' '}
              {localizedEvaluatorError(errorCode, backendDetail.evaluator_error?.message ?? errorCode, t)}
              <span className="ml-1 text-muted">{t('audit.no_fallback')}</span>
            </p>
          )}
          <button
            type="button"
            onClick={rerunFromFailure}
            disabled={reanalyzing}
            className="btn-primary mt-1 h-11 px-6 text-[14px] disabled:opacity-60"
          >
            <RefreshCw size={14} className={reanalyzing ? 'animate-spin mr-1.5 inline' : 'mr-1.5 inline'} aria-hidden />
            {t('audit.rerun')}
          </button>
          <Link href="/editor" className="btn-ghost h-10 px-5 text-[13px]">
            {t('audit.back_editor')}
          </Link>
        </div>
      </>
    );
  }

  const result: AnalysisResult | null = adapted ? adapted.result : localResult;
  const revision: Revision | null = adapted ? adapted.revision : localRevision;
  const criteria: AcceptanceCriteria | null = adapted ? adapted.criteria : localCriteria;

  if (!result || !revision) {
    return (
      <div className="card mx-auto flex max-w-[520px] flex-col items-center gap-3 px-8 py-14 text-center">
        <FileSearch size={30} strokeWidth={1.5} className="text-muted" aria-hidden />
        <h1 className="text-[20px] font-semibold">{t('audit.not_found')}</h1>
        <p className="text-[14px] text-muted">
          {t('audit.not_found_desc', { id })}
        </p>
        <Link href="/editor" className="btn-primary mt-2 h-11 px-6 text-[14px]">
          {t('audit.back_editor')}
        </Link>
      </div>
    );
  }

  /** Task 10: reanalysis from the FAILED panel shares the rerun lifecycle. */
  function rerunFromFailure() {
    setReanalyzing(true);
    apiReanalyzeAudit(backendDetail!.id_audit)
      .then(() => loadAudit())
      .catch(() => toast(t('audit.toast_rerun_fail')))
      .finally(() => setReanalyzing(false));
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
          toast(t('audit.toast_apply_ok'));
          const refreshed = await apiGetAuditDetail(backendDetail.id_audit);
          if (refreshed.data) setBackendDetail(refreshed.data);
          if (res.data.konten_revisi) {
            setDraft({ text: res.data.konten_revisi, language: currentLang });
          }
        }
      } catch (err) {
        toast(t('audit.toast_apply_fail'));
      } finally {
        setApplyingRevision(false);
      }
      return;
    }

    // Offline local audit (browser engine)
    const next = createAudit(revision.text, currentLang);
    setDraft({ text: revision.text, language: currentLang });
    toast(t('audit.toast_revision_applied'));
    router.push(`/audit/${next.id}`);
  };

  /** Jalankan Ulang Analisis (backend audit, terminal non-FAILED state) */
  const rerun = async () => {
    if (backendDetail) {
      setReanalyzing(true);
      try {
        toast(t('audit.toast_rerun_started'));
        await apiReanalyzeAudit(backendDetail.id_audit);
        // Task 10: re-enter the processing lifecycle (clears stale results,
        // shows the pipeline card and polls until terminal state).
        setBackendDetail(null);
        await loadAudit();
      } catch (err) {
        toast(t('audit.toast_rerun_fail'));
      } finally {
        setReanalyzing(false);
      }
      return;
    }

    if (localAudit) {
      touchAudit(localAudit.id);
      toast(t('audit.toast_rules_updated'));
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
    const ok = await copyText(
      toMarkdown(dummyAudit, result, revision, {
        evaluator: adapted?.actualEvaluator ?? adapted?.evaluator,
        modelVersion: adapted?.modelVersion,
        aiInvestNotes: adapted?.aiInvestNotes,
        locale: uiLocale,
      })
    );
    toast(ok ? t('audit.toast_copy_ok') : t('audit.toast_copy_fail'));
  };

  /** Ekspor Dokumen Resmi */
  const exportAs = async (format: ExportFormat) => {
    if (backendDetail && (format === 'md' || format === 'json')) {
      try {
        toast(t('audit.toast_downloading', { fmt: format.toUpperCase() }));
        const { blob, filename } = await apiDownloadExport(backendDetail.id_audit, format, uiLocale);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
        toast(t('audit.toast_download_ok', { name: filename }));
        return;
      } catch (err) {
        console.warn('Ekspor backend gagal, beralih ke generator lokal:', err);
      }
    }

    const dummyAudit = {
      id: String(id),
      seq: 1,
      createdAt: auditCreatedAt,
      title: auditTitle,
      text: currentText,
      language: currentLang,
    };
    const { filename, mime, content } = buildExport(format, dummyAudit, result, revision, {
      evaluator: adapted?.actualEvaluator ?? adapted?.evaluator,
      modelVersion: adapted?.modelVersion,
      aiInvestNotes: adapted?.aiInvestNotes,
      locale: uiLocale,
    });
    download(filename, mime, content);
    toast(t('audit.toast_download_ok', { name: filename }));
  };

  // P0.1/R3-2: status transparan saran tahap AI (mock vs provider vs gagal).
  const aiStatus = backendDetail ? resolveAiSuggestionStatus(backendDetail, uiLocale) : null;

  const bannerActualName = adapted?.actualEvaluator
    ? t(`evaluator.${adapted.actualEvaluator}`) !== `evaluator.${adapted.actualEvaluator}`
      ? t(`evaluator.${adapted.actualEvaluator}`)
      : String(adapted.actualEvaluator)
    : requestedName;

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
              <CalendarDays size={13} aria-hidden /> {formatDate(auditCreatedAt, uiLocale)}
            </span>
            <span aria-hidden>·</span>
            <span className="truncate max-w-[280px] font-medium">{auditTitle}</span>
            {backendDetail && (
              <>
                <span aria-hidden>·</span>
                <span className="pill text-[10.5px] bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20 font-medium">
                  {t('audit.pipeline_pill')}
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
              trigger={({ toggle }) => (
                <button type="button" onClick={toggle} className="btn-primary h-10 rounded-full px-4 text-[13px]">
                  <Download size={14} aria-hidden /> {t('audit.export')} <ChevronDown size={13} aria-hidden />
                </button>
              )}
            >
              {(close) =>
                EXPORTS.map(({ format, label }) => (
                  <button
                    key={format}
                    type="button"
                    className="menu-item"
                    onClick={() => {
                      exportAs(format);
                      close();
                    }}
                  >
                    {label}
                  </button>
                ))
              }
            </Popover>
          </div>
        }
      />

      <div className="space-y-5">
        {/* Task 06 + Task 10: explicit evaluator provenance (requested vs actual),
            model identity, and separate generation status. */}
        <div className="card flex flex-wrap items-center gap-x-6 gap-y-2 px-5 py-3 text-[12.5px] text-muted">
          <span>
            {t('audit.evaluator_requested')}:{' '}
            <strong className="text-ink">
              {requestedName ??
                (adapted?.evaluator === 'traditional_ml'
                  ? t('evaluator.traditional_ml')
                  : adapted?.evaluator === 'multimodel_router'
                    ? t('evaluator.multimodel_router')
                    : adapted?.evaluator === 'llm'
                      ? t('evaluator.llm')
                      : t('evaluator.rule_based'))}
            </strong>
          </span>
          {backendDetail && (
            <span>
              {t('audit.evaluator_actual')}:{' '}
              <strong className={adapted?.actualEvaluator ? 'text-ink' : 'text-amber-600'}>
                {bannerActualName ?? '—'}
              </strong>
            </span>
          )}
          {adapted?.modelVersion && (
            <span>
              {t('audit.model_label')}: <code className="text-[11.5px]">{adapted.modelVersion}</code>
            </span>
          )}
          {adapted?.generation?.status && (
            <span>
              {t('audit.generator_label')}:{' '}
              <strong className={adapted.generation.status === 'DONE' ? 'text-ink' : 'text-amber-600'}>
                {adapted.generation.status === 'DONE'
                  ? t('audit.gen_done', { provider: adapted.generation.provider ?? '-' })
                  : t('audit.gen_failed')}
              </strong>
            </span>
          )}
        </div>

        {adapted?.evaluatorError && (
          <div className="card border-red-400/40 bg-red-500/[0.06] px-5 py-3 text-[13px] text-red-700 dark:text-red-300" role="alert">
            <strong>{t('audit.eval_unavailable')}:</strong>{' '}
            {localizedEvaluatorError(
              adapted.evaluatorError.code,
              adapted.evaluatorError.message,
              t,
            )}
            <span className="ml-1 text-muted">{t('audit.no_fallback')}</span>
          </div>
        )}

        {/* Task 10 Phase 5: generator failure detail is explicit, never disguised. */}
        {adapted?.generation?.status === 'FAILED' && adapted.generation.error && (
          <p className="text-[12.5px] text-amber-700 dark:text-amber-400">
            {t('audit.gen_failed_detail', { error: adapted.generation.error })}
          </p>
        )}

        <div className="grid gap-5 lg:grid-cols-[minmax(0,340px)_1fr]">
          <ScoreCard result={result} provenance={bannerActualName ? t('audit.score_provenance', { name: bannerActualName }) : undefined} />
          <SummaryCard result={result} />
        </div>

        {/* Task 10 Phase 3: dimension-level results from the actual evaluator
            (Traditional ML / LLM evidence previously invisible in the UI). */}
        {adapted?.evaluation?.dimensions && bannerActualName && (
          <DimensionResults
            dimensions={adapted.evaluation.dimensions}
            evaluatorLabel={bannerActualName}
            verdict={adapted.evaluation.verdict}
          />
        )}

        <FindingsTable findings={result.findings} onOpenEditor={() => openInEditor(currentText)} />

        {adapted?.aiInvestNotes && (
          <div className="card px-5 py-3 text-[12.5px] text-muted">
            <span className="font-medium text-ink">{t('audit.advisory_title')}:</span> {t('audit.advisory_desc')}
            <ul className="mt-2 grid gap-1 sm:grid-cols-2">
              {Object.entries(adapted.aiInvestNotes).map(([crit, flagged]) => (
                <li key={crit}>
                  {crit}:{' '}
                  {flagged === false
                    ? t('audit.flagged')
                    : flagged === true
                      ? t('audit.passed_llm')
                      : t('audit.unknown_val')}{' '}
                  <span className="text-muted">{t('audit.advisory_note')}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {aiStatus && (
          <p
            className={`text-[12.5px] leading-relaxed ${
              aiStatus.kind === 'unavailable' ? 'text-amber-700 dark:text-amber-400' : 'text-muted'
            }`}
          >
            <strong>AI:</strong> {aiStatus.explanation}
          </p>
        )}

        <p className="text-[12.5px] leading-relaxed text-muted">
          {t('audit.privacy_note')}
        </p>

        <div className="grid gap-5 md:grid-cols-2">
          <RevisionCard
            revision={revision}
            remaining={revision.result.findings.length}
            onApply={applyRevision}
            onEdit={() => openInEditor(revision.changed ? revision.text : currentText)}
          />
          <AcceptanceCard criteria={criteria} />
        </div>

        {revision.changed && (
          <DiffViewer
            before={currentText}
            after={revision.text}
            beforeScore={revision.originalLocal.score}
            afterScore={revision.result.score}
            localEstimate
            onApply={applyRevision}
            canApply={!applyingRevision}
          />
        )}
      </div>
    </>
  );
}
