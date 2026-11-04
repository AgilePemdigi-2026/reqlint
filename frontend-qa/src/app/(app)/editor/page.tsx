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
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadingPdf, setUploadingPdf] = useState(false);

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

    try {
      const res = await apiCreateAudit({
        konten: draft.text,
        judul_klausul: suggestTitle(draft.text, draft.language),
        tipe_masukan: 'manual',
      });

      if (res.data?.id_audit) {
        toast('Draf diterima backend. Menjalankan model klasifikasi INVEST...');
        router.push(`/audit/${res.data.id_audit}`);
        return;
      }
    } catch (err) {
      console.warn('Backend API gagal dihubungi, beralih ke analisis lokal:', err);
    } finally {
      setAnalyzing(false);
    }

    // Fallback bila server backend tidak tersedia
    const localAudit = createAudit(draft.text, draft.language);
    toast('Menggunakan engine analisis mandiri browser.');
    router.push(`/audit/${localAudit.id}`);
  }

  /** Menangani unggah berkas PDF langsung ke endpoint backend */
  const onFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.name.toLowerCase().endsWith('.pdf')) {
      setUploadingPdf(true);
      try {
        toast('Mengekstraksi teks PDF di server...');
        const docRes = await uploadDocumentPdf(file);
        if (docRes && docRes.teks) {
          setDraft({ ...draft, text: docRes.teks });
          toast(`PDF "${docRes.nama_dokumen}" berhasil diekstraksi (${docRes.jumlah_karakter} karakter).`);
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
        crumb="Workspace / Draf Kebutuhan"
        title="Editor User Story"
        subtitle="Tulis atau tempel draf kebutuhan Anda. ReqLint akan mengauditnya menggunakan model INVEST & ISO 29148."
        right={
          <span className="pill bg-line/[0.06] text-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" aria-hidden /> Backend FastAPI Terhubung
          </span>
        }
      />

      <section className="card overflow-visible p-5 sm:p-6" aria-label="Editor">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line/[0.07] pb-5">
          <Popover
            trigger={({ toggle }) => (
              <button
                type="button"
                onClick={toggle}
                className="btn-ghost h-9 gap-2 rounded-full px-3 text-[12.5px]"
                aria-label="Pilih bahasa analisis"
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
              aria-label="Unggah berkas PDF atau teks"
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
                  <Loader2 size={16} className="animate-spin" aria-hidden /> Mengekstrak…
                </>
              ) : (
                <>
                  <FileUp size={16} aria-hidden /> Upload PDF
                </>
              )}
            </button>

            <Popover
              align="right"
              trigger={({ toggle }) => (
                <button type="button" onClick={toggle} className="btn-ghost h-11 whitespace-nowrap px-4 text-[14px]">
                  <FileText size={16} aria-hidden /> Contoh Template <ChevronDown size={14} aria-hidden />
                </button>
              )}
            >
              {(close) =>
                TEMPLATES.map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    className="menu-item"
                    onClick={() => {
                      update({ text: t.text[draft.language] });
                      close();
                    }}
                  >
                    {t.label[draft.language]}
                  </button>
                ))
              }
            </Popover>
          </div>
        </div>

        <div className="mt-5">
          <CodeEditor
            value={draft.text}
            onChange={(text) => update({ text })}
            language={draft.language}
            maxLength={MAX_CHARS}
          />
        </div>

        <p className="mt-3.5 flex items-center gap-2 text-[12.5px] text-muted" aria-live="polite">
          <span className={`h-1.5 w-1.5 rounded-full ${stats.flagged ? 'bg-amber-500' : 'bg-emerald-500'}`} aria-hidden />
          {empty
            ? 'Tulis atau tempel draf kebutuhan untuk mulai.'
            : stats.flagged
              ? 'Istilah yang digarisbawahi mungkin tidak terukur. Jalankan analisis untuk melihat evaluasi model INVEST.'
              : 'Belum ada istilah tidak terukur yang terdeteksi saat mengetik. Jalankan analisis untuk audit lengkap.'}
        </p>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-[13.5px] text-muted">
            <span>
              {stats.clauses} klausul · {stats.words} kata
            </span>
            <span className="h-4 w-px bg-line/10" aria-hidden />
            <span className="inline-flex items-center gap-1.5">
              <Check size={14} aria-hidden /> Tersimpan otomatis
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
                <Loader2 size={18} className="animate-spin" aria-hidden /> Menganalisis...
              </>
            ) : (
              <>
                Audit User Story <ArrowRight size={18} aria-hidden />
              </>
            )}
          </button>
        </div>
      </section>

      {!tipDismissed && (
        <aside className="card mt-5 flex items-center gap-4 rounded-[22px] px-4 py-3.5" aria-label="Tips">
          <span className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-line/[0.07] bg-card">
            <Lightbulb size={18} strokeWidth={1.6} aria-hidden />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-[14.5px] font-semibold">Kebutuhan yang baik dimulai dari tiga hal.</p>
            <p className="text-[12.5px] text-muted">
              Tentukan siapa penggunanya (Role), apa yang dibutuhkan (Action), dan mengapa itu penting (Benefit). Model AI kami membantu menyempurnakan sisanya.
            </p>
          </div>
          <a
            href="https://en.wikipedia.org/wiki/INVEST_(mnemonic)"
            target="_blank"
            rel="noreferrer"
            className="hidden items-center gap-1.5 whitespace-nowrap text-[12.5px] font-medium text-accent hover:underline sm:inline-flex"
          >
            Pelajari INVEST <ArrowRight size={14} aria-hidden />
          </a>
          <button
            type="button"
            onClick={dismissTip}
            aria-label="Tutup tips"
            className="inline-flex h-8 w-8 items-center justify-center rounded-full text-muted transition hover:bg-line/[0.06] hover:text-ink"
          >
            <X size={16} />
          </button>
        </aside>
      )}
    </>
  );
}
