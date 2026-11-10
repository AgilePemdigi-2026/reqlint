'use client';

import { ArrowRight, FileUp, Languages } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useRef, useState } from 'react';
import { ScoreRing } from '@/components/audit/score-card';
import { useToast } from '@/components/providers';
import { analyze, type AnalysisResult, type Language } from '@/lib/analyzer';
import { setDraft } from '@/lib/audits';
import { CATEGORY_LABEL, CATEGORY_STYLE, GRADE_BADGE, GRADE_COLOR, GRADE_LABEL } from '@/lib/format';
import { readTextFile } from '@/lib/pdf';
import { TEMPLATES } from '@/lib/templates';
import { MAX_CHARS } from '@/lib/validation';
import { useUILocale } from '@/lib/i18n';

const BAD = TEMPLATES.find((t) => t.id === 'login')!;
const GOOD = TEMPLATES.find((t) => t.id === 'good')!;

const TABS: Array<{ lang: Language; label: string }> = [
  { lang: 'id', label: 'Bahasa Indonesia' },
  { lang: 'en', label: 'English' },
];

/** Demo interaktif di hero: analisis berjalan di browser tanpa perlu login. */
export function DemoCard() {
  const router = useRouter();
  const toast = useToast();
  const locale = useUILocale();
  const fileInput = useRef<HTMLInputElement>(null);
  const [language, setLanguage] = useState<Language>('id');
  const [text, setText] = useState(BAD.text.id);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const empty = text.trim().length === 0;

  const load = (value: string, lang: Language = language) => {
    setLanguage(lang);
    setText(value);
    setResult(null);
  };

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    if (file.size > 8 * 1024 * 1024) return toast('Berkas terlalu besar (maks. 8 MB).');
    try {
      const content = (await readTextFile(file)).trim();
      if (!content) return toast('Tidak ada teks yang dapat dibaca dari berkas ini.');
      load(content.slice(0, MAX_CHARS));
    } catch {
      toast('Gagal membaca berkas. Pastikan berkas tidak rusak atau terkunci.');
    }
  }

  function openFullReport() {
    setDraft({ text, language });
    router.push('/editor');
  }

  return (
    <div className="card overflow-hidden rounded-[28px] border border-black/10 bg-white/70 shadow-2xl backdrop-blur-md dark:border-white/10 dark:bg-[#1c1c1f]/80">
      {/* Header kartu */}
      <div className="flex items-center justify-between border-b border-black/[0.08] px-7 py-4 dark:border-white/10">
        <div className="flex items-center gap-1 rounded-full bg-black/[0.05] p-1 dark:bg-white/[0.08]">
          {TABS.map((tab) => (
            <button
              key={tab.lang}
              type="button"
              onClick={() => load(BAD.text[tab.lang], tab.lang)}
              className={`rounded-full px-4 py-1.5 text-[14px] font-medium transition ${
                language === tab.lang
                  ? 'bg-white text-ink shadow-sm dark:bg-card'
                  : 'text-ink/60 hover:text-ink'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <input
          ref={fileInput}
          type="file"
          accept=".pdf,.txt,.md"
          className="sr-only"
          onChange={onFile}
        />
        <button
          type="button"
          onClick={() => fileInput.current?.click()}
          className="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-[13.5px] font-medium text-ink/70 transition hover:bg-black/[0.04] hover:text-ink dark:hover:bg-white/[0.06]"
        >
          <FileUp size={15} /> {locale === 'id' ? 'Unggah berkas' : 'Upload file'}
        </button>
      </div>

      {/* Area input teks */}
      <div className="px-7 pt-6">
        <textarea
          value={text}
          onChange={(e) => {
            setText(e.target.value.slice(0, MAX_CHARS));
            setResult(null);
          }}
          rows={5}
          className="field w-full resize-none rounded-2xl p-4 font-mono text-[14.5px] leading-relaxed"
          placeholder={locale === 'id' ? 'Tulis user story Anda di sini...' : 'Type your user story here...'}
        />
      </div>

      {/* Hasil evaluasi ringkas jika sudah dianalisis */}
      {result && (
        <div className="mx-7 mb-4 mt-2 rounded-2xl border border-line/[0.08] bg-line/[0.02] p-4">
          <div className="flex items-center gap-4">
            <div role="img" aria-label={`Skor ${result.score} dari 100`}>
              <ScoreRing score={result.score} color={GRADE_COLOR[result.grade]} size={88} />
            </div>
            <div className="min-w-0 flex-1">
              <span className={`pill ${GRADE_BADGE[result.grade]}`}>{GRADE_LABEL[result.grade]}</span>
              <p className="mt-2 text-[13.5px] text-ink/60">
                {result.findings.length} {locale === 'id' ? 'temuan' : 'findings'} · ISO 29148 {result.compliance.iso29148}% · INVEST {result.compliance.invest}%
              </p>
            </div>
          </div>
          {result.findings.length > 0 && (
            <ul className="mt-3 space-y-2 border-t border-line/[0.08] pt-3">
              {result.findings.slice(0, 3).map((f) => (
                <li key={f.id} className="flex flex-wrap items-center gap-2 text-[12.5px]">
                  <span className={`pill px-2 py-0.5 text-[10.5px] ${CATEGORY_STYLE[f.category]}`}>
                    {CATEGORY_LABEL[f.category]}
                  </span>
                  <code className="rounded bg-line/[0.06] px-1.5 py-0.5 font-mono text-[11.5px]">{f.term}</code>
                  <span className="text-ink/60">{f.recommendation}</span>
                </li>
              ))}
            </ul>
          )}
          <button
            type="button"
            onClick={openFullReport}
            className="mt-4 inline-flex items-center gap-1.5 text-[13.5px] font-semibold text-accent hover:underline"
          >
            {locale === 'id' ? 'Lihat laporan lengkap, saran revisi & diff' : 'View full report, revision & diff'}{' '}
            <ArrowRight size={14} aria-hidden />
          </button>
        </div>
      )}

      {/* Contoh */}
      <div className="flex flex-wrap items-center gap-3 px-7 pb-6 pt-2 text-[16px] text-ink/55">
        {locale === 'id' ? 'Contoh:' : 'Examples:'}
        <button
          type="button"
          onClick={() => load(BAD.text[language])}
          className="rounded-lg bg-[#fbf1df] px-3.5 py-2 text-[15px] text-[#6b4a12] transition hover:brightness-95 dark:bg-amber-400/15 dark:text-amber-200"
        >
          {locale === 'id' ? 'Draf bermasalah' : 'Defective draft'}
        </button>
        <button
          type="button"
          onClick={() => load(GOOD.text[language])}
          className="rounded-lg bg-[#dff1ea] px-3.5 py-2 text-[15px] text-[#1c5a45] transition hover:brightness-95 dark:bg-emerald-400/15 dark:text-emerald-200"
        >
          {locale === 'id' ? 'Draf yang baik' : 'Good draft'}
        </button>
      </div>

      {/* Footer kartu */}
      <div className="flex items-center justify-between gap-4 border-t border-black/[0.08] px-7 py-5 dark:border-white/10">
        <span className="text-[15px] text-ink/50">
          {text.length.toLocaleString(locale === 'en' ? 'en-US' : 'id-ID')}/{MAX_CHARS.toLocaleString(locale === 'en' ? 'en-US' : 'id-ID')}{' '}
          {locale === 'id' ? 'karakter' : 'characters'}
        </span>
        <button
          type="button"
          disabled={empty}
          onClick={() => setResult(analyze(text, language))}
          className="btn-primary h-14 gap-3 rounded-full px-9 text-[18px]"
        >
          {locale === 'id' ? 'Analisis' : 'Analyze'} <ArrowRight size={20} aria-hidden />
        </button>
      </div>
    </div>
  );
}
