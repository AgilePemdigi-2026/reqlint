'use client';

import { ArrowRight, FileUp, Languages } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useRef, useState } from 'react';
import { ScoreRing } from '@/components/audit/score-card';
import { useToast } from '@/components/providers';
import { analyze, type AnalysisResult, type Language } from '@/lib/analyzer';
import { setDraft } from '@/lib/audits';
import { CATEGORY_STYLE, GRADE_BADGE, GRADE_COLOR, categoryLabelT, gradeLabel } from '@/lib/format';
import { useT, useUILocale } from '@/lib/i18n';
import { readTextFile } from '@/lib/pdf';
import { TEMPLATES } from '@/lib/templates';
import { MAX_CHARS } from '@/lib/validation';

const BAD = TEMPLATES.find((t) => t.id === 'login')!;
const GOOD = TEMPLATES.find((t) => t.id === 'good')!;

const TABS: Array<{ lang: Language }> = [{ lang: 'id' }, { lang: 'en' }];

/** Demo interaktif di hero: analisis berjalan di browser tanpa perlu login. */
export function DemoCard() {
  const router = useRouter();
  const toast = useToast();
  const t = useT();
  const uiLocale = useUILocale();
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
    if (file.size > 8 * 1024 * 1024) return toast(t('demo.toast_too_large'));
    try {
      const content = (await readTextFile(file)).trim();
      if (!content) return toast(t('demo.toast_no_text'));
      load(content.slice(0, MAX_CHARS));
    } catch {
      toast(t('demo.toast_read_fail'));
    }
  }

  function openFullReport() {
    // Simpan sebagai draf; /editor meminta login bila belum masuk, lalu melanjutkan dengan draf ini.
    setDraft({ text, language });
    router.push('/editor');
  }

  return (
    <div className="overflow-hidden rounded-[22px] border border-black/[0.08] bg-white shadow-[0_10px_40px_-14px_rgba(0,0,0,0.2)] dark:border-white/10 dark:bg-[#1c1c20]">
      {/* Tab bahasa */}
      <div role="tablist" aria-label={t('demo.tab_aria')} className="grid grid-cols-2 border-b border-black/[0.08] dark:border-white/10">
        {TABS.map(({ lang }) => {
          const active = language === lang;
          return (
            <button
              key={lang}
              type="button"
              role="tab"
              aria-selected={active}
              onClick={() => load(BAD.text[lang], lang)}
              className={`flex items-center justify-center gap-2.5 py-[18px] text-[16px] transition ${
                active
                  ? 'bg-[#e4efe8] font-semibold text-emerald-900 shadow-[inset_0_-3px_0_0_#166534] dark:bg-emerald-400/15 dark:text-emerald-200 dark:shadow-[inset_0_-3px_0_0_#6ee7b7]'
                   : 'bg-white text-ink/60 hover:bg-black/[0.03] hover:text-ink dark:bg-[#1c1c20] dark:hover:bg-white/[0.04]'
                  } ${lang === 'id' ? 'border-r border-black/[0.08] dark:border-white/10' : ''}`}
            >
              <Languages size={18} strokeWidth={1.6} aria-hidden /> {t(`general.${lang === 'id' ? 'indonesian' : 'english'}`)}
            </button>
          );
        })}
      </div>

      <div className="px-7 pt-6">
        <div className="flex flex-wrap items-center gap-3 text-[18px] text-ink/45">
          {t('demo.paste_or')}
          <input
            ref={fileInput}
            type="file"
            accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
            className="sr-only"
            tabIndex={-1}
            aria-label={t('demo.upload_aria')}
            onChange={onFile}
          />
          <button
            type="button"
            onClick={() => fileInput.current?.click()}
            className="inline-flex items-center gap-2 rounded-full bg-black/[0.06] px-4 py-2 text-[14.5px] font-medium text-ink/80 transition hover:bg-black/10 dark:bg-white/10 dark:hover:bg-white/15"
          >
            <FileUp size={16} aria-hidden /> {t('demo.upload')}
          </button>
        </div>

        <textarea
          value={text}
          onChange={(e) => load(e.target.value)}
          maxLength={MAX_CHARS}
          spellCheck={false}
          aria-label={t('demo.textarea_aria')}
          placeholder={t('demo.placeholder')}
          className="mt-4 block h-[260px] w-full resize-none bg-transparent text-[16.5px] leading-[1.75] text-ink outline-none placeholder:text-ink/30"
        />
      </div>

      {result && (
        <div className="mx-6 mb-4 rounded-2xl border border-line/[0.08] bg-black/[0.02] p-4 dark:bg-white/[0.03]" aria-live="polite">
          <div className="flex items-center gap-5">
            <div role="img" aria-label={t('demo.score_aria', { n: result.score })}>
              <ScoreRing score={result.score} color={GRADE_COLOR[result.grade]} size={88} />
            </div>
            <div className="min-w-0 flex-1">
              <span className={`pill ${GRADE_BADGE[result.grade]}`}>{gradeLabel(result.grade, uiLocale)}</span>
              <p className="mt-2 text-[13.5px] text-ink/60">
                {t('demo.findings_line', { n: result.findings.length, iso: result.compliance.iso29148 ?? 0, invest: result.compliance.invest ?? 0 })}
              </p>
            </div>
          </div>
          {result.findings.length > 0 && (
            <ul className="mt-3 space-y-2 border-t border-line/[0.08] pt-3">
              {result.findings.slice(0, 3).map((f) => (
                <li key={f.id} className="flex flex-wrap items-center gap-2 text-[12.5px]">
                  <span className={`pill px-2 py-0.5 text-[10.5px] ${CATEGORY_STYLE[f.category]}`}>
                    {categoryLabelT(f.category, t)}
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
            {t('demo.full_report')} <ArrowRight size={14} aria-hidden />
          </button>
        </div>
      )}

      {/* Contoh */}
      <div className="flex flex-wrap items-center gap-3 px-7 pb-6 pt-2 text-[16px] text-ink/55">
        {t('demo.examples')}
        <button
          type="button"
          onClick={() => load(BAD.text[language])}
          className="rounded-lg bg-[#fbf1df] px-3.5 py-2 text-[15px] text-[#6b4a12] transition hover:brightness-95 dark:bg-amber-400/15 dark:text-amber-200"
        >
          {t('demo.bad_draft')}
        </button>
        <button
          type="button"
          onClick={() => load(GOOD.text[language])}
          className="rounded-lg bg-[#dff1ea] px-3.5 py-2 text-[15px] text-[#1c5a45] transition hover:brightness-95 dark:bg-emerald-400/15 dark:text-emerald-200"
        >
          {t('demo.good_draft')}
        </button>
      </div>

      {/* Footer kartu */}
      <div className="flex items-center justify-between gap-4 border-t border-black/[0.08] px-7 py-5 dark:border-white/10">
        <span className="text-[15px] text-ink/50">
          {text.length.toLocaleString(uiLocale === 'en' ? 'en-US' : 'id-ID')}/{MAX_CHARS.toLocaleString(uiLocale === 'en' ? 'en-US' : 'id-ID')} {t('demo.chars_suffix')}
        </span>
        <button
          type="button"
          disabled={empty}
          onClick={() => setResult(analyze(text, language))}
          className="btn-primary h-14 gap-3 rounded-full px-9 text-[18px]"
        >
          {t('demo.analyze')} <ArrowRight size={20} aria-hidden />
        </button>
      </div>
    </div>
  );
}
