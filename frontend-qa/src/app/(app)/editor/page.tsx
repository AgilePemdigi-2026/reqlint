'use client';

import { ArrowRight, ChevronDown, FileText, FileUp, Languages, Lightbulb, X, Check, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useMemo, useRef, useState } from 'react';
import { PageHeader } from '@/components/app-shell';
import { CodeEditor } from '@/components/code-editor';
import { Popover } from '@/components/popover';
import { useToast } from '@/components/providers';
import { countWords, liveMarks, splitClauses, suggestTitle, type Language } from '@/lib/analyzer';
import { createAudit, dismissTip, setDraft, useDraft, useTipDismissed } from '@/lib/audits';
import { apiCreateAudit, uploadDocumentPdf } from '@/lib/api';
import { useT } from '@/lib/i18n';
import {
  ANALYZER_CATEGORY_OPTIONS,
  DEFAULT_ML_MODEL,
  ML_MODEL_OPTIONS,
  resolveEvaluatorPayload,
  type AnalyzerCategory,
  type MlModelId,
} from '@/lib/evaluator-options';
import { TEMPLATES } from '@/lib/templates';
import { useFileImport } from '@/lib/use-file-import';
import { MAX_CHARS } from '@/lib/validation';

const LANGUAGES: Record<Language, string> = { id: 'Bahasa Indonesia', en: 'English' };

export default function EditorPage() {
  const router = useRouter();
  const draft = useDraft();
  const tipDismissed = useTipDismissed();
  const toast = useToast();
  const fileInput = useRef<HTMLInputElement>(null);
  const t = useT();
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadingPdf, setUploadingPdf] = useState(false);
  // Task 06 + granular ML selection: analyzer category + ML model dropdown.
  const [category, setCategory] = useState<AnalyzerCategory>('rule_based');
  const [mlModel, setMlModel] = useState<MlModelId>(DEFAULT_ML_MODEL);

  const { busy: localImporting, onChange: onLocalFile } = useFileImport((text) => setDraft({ ...draft, text }));

  const stats = useMemo(
    () => ({
      clauses: splitClauses(draft.text).length,
      words: countWords(draft.text),
      flagged: liveMarks(draft.text, draft.language).length,
    }),
    [draft.text, draft.language],
  );
  const empty = draft.text.trim().length === 0;

  const update = (patch: Partial<typeof draft>) => setDraft({ ...draft, ...patch });

  /** Menjalankan audit: mengirimkan draf ke pipeline backend FastAPI (Tahap 2) */
  async function analyzeNow() {
    if (empty || analyzing) return;
    setAnalyzing(true);
    const { evaluator, ml_model } = resolveEvaluatorPayload(category, mlModel);

    try {
      const res = await apiCreateAudit({
        konten: draft.text,
        judul_klausul: suggestTitle(draft.text, draft.language),
        tipe_masukan: 'manual',
        evaluator,
        ...(ml_model ? { ml_model } : {}),
      });

      if (res.data?.id_audit) {
        // Task 10: simpan evaluator yang diminta pada record lokal (provenance
        // untuk tampilan processing & riwayat).
        createAudit(draft.text, draft.language, String(res.data.id_audit), evaluator);
        toast(t('editor.sent_backend'));
        router.push(`/audit/${res.data.id_audit}`);
        return;
      }
    } catch (err) {
      console.warn('Backend API gagal dihubungi:', err);
    } finally {
      setAnalyzing(false);
    }

    // Task 06: fallback browser HANYA untuk Rule-Based. Traditional ML dan
    // LLM tidak punya implementasi lokal yang setara — tampilkan error,
    // jangan ganti evaluator secara diam-diam.
    if (evaluator !== 'rule_based') {
      const name = category === 'machine_learning' ? t(`ml_model.${mlModel}`) : t(`evaluator.${evaluator}`);
      toast(t('editor.needs_backend', { name }));
      setAnalyzing(false);
      return;
    }

    const localAudit = createAudit(draft.text, draft.language);
    toast(t('editor.local_fallback'));
    router.push(`/audit/${localAudit.id}`);
  }

  /** Menangani unggah berkas PDF langsung ke endpoint backend */
  const onFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.name.toLowerCase().endsWith('.pdf')) {
      setUploadingPdf(true);
      try {
        toast(t('editor.pdf_extracting_toast'));
        const docRes = await uploadDocumentPdf(file);
        if (docRes && docRes.teks) {
          setDraft({ ...draft, text: docRes.teks });
          toast(t('editor.pdf_done_toast', { name: docRes.nama_dokumen, n: docRes.jumlah_karakter }));
          e.target.value = '';
          return;
        }
      } catch (err) {
        console.warn('Ekstraksi PDF di backend gagal, menggunakan ekstraktor lokal:', err);
      } finally {
        setUploadingPdf(false);
      }
    }

    onLocalFile(e);
  };

  const isBusyUploading = uploadingPdf || localImporting;

  return (
    <>
      <PageHeader
        crumb={t('editor.crumb')}
        title={t('editor.title')}
        subtitle={t('editor.subtitle')}
        right={
          <span className="pill bg-line/[0.06] text-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" aria-hidden /> {t('editor.backend_connected')}
          </span>
        }
      />

      <section className="card overflow-visible p-5 sm:p-6" aria-label={t('editor.section_aria')}>
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line/[0.07] pb-5">
          <Popover
            trigger={({ toggle }) => (
              <button
                type="button"
                onClick={toggle}
                className="btn-ghost h-9 gap-2 rounded-full px-3 text-[12.5px]"
                aria-label={t('editor.analysis_lang_aria')}
              >
                <Languages size={14} aria-hidden /> {LANGUAGES[draft.language]}
              </button>
            )}
          >
            {(close) =>
              (Object.keys(LANGUAGES) as Language[]).map((l) => (
                <button
                  key={l}
                  type="button"
                  className="menu-item justify-between"
                  onClick={() => {
                    update({ language: l });
                    close();
                  }}
                >
                  {LANGUAGES[l]}
                  {l === draft.language && <Check size={15} aria-hidden />}
                </button>
              ))
            }
          </Popover>

          <div className="flex flex-wrap items-center gap-2.5">
            <input
              ref={fileInput}
              type="file"
              accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
              className="sr-only"
              onChange={onFileChange}
              aria-label={t('editor.upload_aria')}
              tabIndex={-1}
            />
            <button
              type="button"
              disabled={isBusyUploading}
              onClick={() => fileInput.current?.click()}
              className="btn-ghost h-11 whitespace-nowrap px-4 text-[14px]"
            >
              {isBusyUploading ? (
                <>
                  <Loader2 size={16} className="animate-spin" aria-hidden /> {t('editor.extracting')}
                </>
              ) : (
                <>
                  <FileUp size={16} aria-hidden /> {t('editor.upload_pdf')}
                </>
              )}
            </button>

            <Popover
              align="right"
              trigger={({ toggle }) => (
                <button type="button" onClick={toggle} className="btn-ghost h-11 whitespace-nowrap px-4 text-[14px]">
                  <FileText size={16} aria-hidden /> {t('editor.templates')} <ChevronDown size={14} aria-hidden />
                </button>
              )}
            >
              {(close) =>
                TEMPLATES.map((tpl) => (
                  <button
                    key={tpl.id}
                    type="button"
                    className="menu-item"
                    onClick={() => {
                      update({ text: tpl.text[draft.language] });
                      close();
                    }}
                  >
                    {tpl.label[draft.language]}
                  </button>
                ))
              }
            </Popover>
          </div>
        </div>

        <div className="mt-5">
          <div className="mb-3" role="radiogroup" aria-label={t('editor.evaluator_aria')}>
            <span className="mb-2 block text-[12.5px] font-medium text-muted">{t('editor.evaluator_label')}:</span>
            <div className="flex flex-wrap items-center gap-2">
              {ANALYZER_CATEGORY_OPTIONS.map((opt) => {
                const id = opt.id;
                const label = t(opt.labelKey);
                return (
                <button
                  key={id}
                  type="button"
                  role="radio"
                  aria-checked={category === id}
                  onClick={() => setCategory(id)}
                  className={`inline-flex items-center gap-1.5 rounded-full border px-4 py-1.5 text-[13px] transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/70 ${
                    category === id
                      ? 'border-transparent bg-btn text-btnink font-semibold'
                      : 'border-line/25 bg-card/60 text-muted hover:text-ink hover:bg-card'
                  }`}
                >
                  {category === id && (
                    <Check size={13} aria-hidden className="shrink-0" />
                  )}
                  {label}
                </button>
              );
              })}

              {category === 'machine_learning' && (
                <label className="inline-flex items-center gap-2 ml-1">
                  <span className="text-[12.5px] font-medium text-muted">{t('editor.ml_model_label')}:</span>
                  <select
                    aria-label={t('editor.ml_model_label')}
                    value={mlModel}
                    onChange={(e) => setMlModel(e.target.value as MlModelId)}
                    className="rounded-full border border-line/25 bg-card px-3.5 py-1.5 text-[13px] text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/70"
                  >
                    <optgroup label="ML V1">
                      {ML_MODEL_OPTIONS.filter((m) => m.group === 'ML V1').map((m) => (
                        <option key={m.id} value={m.id}>
                          {t(m.labelKey)}
                        </option>
                      ))}
                    </optgroup>
                    <optgroup label="ML V2">
                      {ML_MODEL_OPTIONS.filter((m) => m.group === 'ML V2').map((m) => (
                        <option key={m.id} value={m.id}>
                          {t(m.labelKey)}
                        </option>
                      ))}
                    </optgroup>
                  </select>
                </label>
              )}
            </div>
          </div>
          <CodeEditor
            value={draft.text}
            onChange={(text) => update({ text })}
            language={draft.language}
            maxLength={MAX_CHARS}
            ariaLabel={t('editor.editor_aria')}
            placeholder={t('editor.placeholder')}
          />
        </div>

        <p className="mt-3.5 flex items-center gap-2 text-[12.5px] text-muted" aria-live="polite">
          <span className={`h-1.5 w-1.5 rounded-full ${stats.flagged ? 'bg-amber-500' : 'bg-emerald-500'}`} aria-hidden />
          {empty
            ? t('editor.hint_empty')
            : stats.flagged
              ? t('editor.hint_flagged')
              : t('editor.hint_clean')}
        </p>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-[13.5px] text-muted">
            <span>
              {t('editor.clauses_count', { n: stats.clauses })} · {t('editor.words_count', { n: stats.words })}
            </span>
            <span className="h-4 w-px bg-line/10" aria-hidden />
            <span className="inline-flex items-center gap-1.5">
              <Check size={14} aria-hidden /> {t('editor.autosaved')}
            </span>
          </div>
          <button
            type="button"
            onClick={analyzeNow}
            disabled={empty || analyzing}
            className="btn-primary h-[52px] gap-3 px-7 text-[16px] disabled:opacity-60"
          >
            {analyzing ? (
              <>
                <Loader2 size={18} className="animate-spin" aria-hidden /> {t('editor.analyzing')}
              </>
            ) : (
              <>
                {t('editor.run_audit')} <ArrowRight size={18} aria-hidden />
              </>
            )}
          </button>
        </div>
      </section>

      {!tipDismissed && (
        <aside className="card mt-5 flex items-center gap-4 rounded-[22px] px-4 py-3.5" aria-label={t('editor.tip_aria')}>
          <span className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-line/[0.07] bg-card">
            <Lightbulb size={18} strokeWidth={1.6} aria-hidden />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-[14.5px] font-semibold">{t('editor.tip_title')}</p>
            <p className="text-[12.5px] text-muted">
              {t('editor.tip_desc')}
            </p>
          </div>
          <a
            href="https://en.wikipedia.org/wiki/INVEST_(mnemonic)"
            target="_blank"
            rel="noreferrer"
            className="hidden items-center gap-1.5 whitespace-nowrap text-[12.5px] font-medium text-accent hover:underline sm:inline-flex"
          >
            {t('editor.tip_learn')} <ArrowRight size={14} aria-hidden />
          </a>
          <button
            type="button"
            onClick={dismissTip}
            aria-label={t('editor.tip_close_aria')}
            className="inline-flex h-8 w-8 items-center justify-center rounded-full text-muted transition hover:bg-line/[0.06] hover:text-ink"
          >
            <X size={16} />
          </button>
        </aside>
      )}
    </>
  );
}
