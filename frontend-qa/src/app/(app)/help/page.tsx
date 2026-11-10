'use client';

import {
  BookOpen, UserPlus, FileText, Play, BarChart3, Download,
  Lightbulb, AlertTriangle, CheckCircle2, XCircle, MinusCircle,
  ChevronRight,
} from 'lucide-react';
import Link from 'next/link';
import { PageHeader } from '@/components/app-shell';
import { useT } from '@/lib/i18n';

function StepCard({
  icon: Icon,
  title,
  description,
  step,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
  step: number;
}) {
  return (
    <div className="card flex gap-4 p-5">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent/10 text-accent">
        <Icon size={20} />
      </div>
      <div>
        <h3 className="text-[15px] font-semibold">{title}</h3>
        <p className="mt-1 text-[13.5px] leading-relaxed text-muted">{description}</p>
      </div>
    </div>
  );
}

function GradeRow({ grade, color, label }: { grade: string; color: string; label: string }) {
  return (
    <div className="flex items-center gap-3 rounded-xl px-4 py-2.5 odd:bg-line/[0.03]">
      <span className={`inline-flex h-8 w-8 items-center justify-center rounded-lg text-[13px] font-bold text-white ${color}`}>
        {grade}
      </span>
      <span className="text-[14px]">{label}</span>
    </div>
  );
}

export default function HelpPage() {
  const t = useT();

  const steps = [
    { icon: UserPlus, title: t('help.step1_title'), desc: t('help.step1_desc') },
    { icon: FileText, title: t('help.step2_title'), desc: t('help.step2_desc') },
    { icon: Play, title: t('help.step3_title'), desc: t('help.step3_desc') },
    { icon: BarChart3, title: t('help.step4_title'), desc: t('help.step4_desc') },
    { icon: Download, title: t('help.step5_title'), desc: t('help.step5_desc') },
  ];

  const categories = [
    { icon: AlertTriangle, color: 'text-amber-500', label: t('help.cat_ambiguity') },
    { icon: XCircle, color: 'text-rose-500', label: t('help.cat_incomplete') },
    { icon: MinusCircle, color: 'text-orange-500', label: t('help.cat_weak') },
    { icon: MinusCircle, color: 'text-sky-500', label: t('help.cat_passive') },
  ];

  const tips = [
    t('help.tip1'),
    t('help.tip2'),
    t('help.tip3'),
    t('help.tip4'),
    t('help.tip5'),
  ];

  return (
    <>
      <PageHeader
        crumb={t('help.crumb')}
        title={t('help.title')}
        subtitle={t('help.subtitle')}
      />

      <div className="space-y-8">
        {/* ── Memulai ── */}
        <section>
          <h2 className="mb-4 flex items-center gap-2 text-[20px] font-semibold">
            <BookOpen size={22} className="text-accent" />
            {t('help.getting_started')}
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {steps.map((s, i) => (
              <StepCard key={i} icon={s.icon} title={s.title} description={s.desc} step={i + 1} />
            ))}
          </div>
        </section>

        {/* ── Skor & Grade ── */}
        <section>
          <h2 className="mb-4 flex items-center gap-2 text-[20px] font-semibold">
            <BarChart3 size={22} className="text-accent" />
            {t('help.scores_title')}
          </h2>
          <div className="card p-5">
            <p className="mb-4 text-[14px] text-muted">{t('help.scores_desc')}</p>
            <div className="space-y-1">
              <GradeRow grade="A" color="bg-emerald-500" label={`85–100 · ${t('help.grade_a')}`} />
              <GradeRow grade="B" color="bg-lime-500" label={`70–84 · ${t('help.grade_b')}`} />
              <GradeRow grade="C" color="bg-amber-500" label={`55–69 · ${t('help.grade_c')}`} />
              <GradeRow grade="D" color="bg-orange-500" label={`35–54 · ${t('help.grade_d')}`} />
              <GradeRow grade="E" color="bg-rose-500" label={`0–34 · ${t('help.grade_e')}`} />
            </div>
          </div>
        </section>

        {/* ── Kategori Temuan ── */}
        <section>
          <h2 className="mb-4 flex items-center gap-2 text-[20px] font-semibold">
            <AlertTriangle size={22} className="text-accent" />
            {t('help.categories_title')}
          </h2>
          <div className="card divide-y divide-line/[0.07] p-2">
            {categories.map((cat, i) => (
              <div key={i} className="flex items-center gap-3 px-4 py-3">
                <cat.icon size={18} className={cat.color} />
                <span className="text-[14px]">{cat.label}</span>
              </div>
            ))}
          </div>
        </section>

        {/* ── Tips ── */}
        <section>
          <h2 className="mb-4 flex items-center gap-2 text-[20px] font-semibold">
            <Lightbulb size={22} className="text-accent" />
            {t('help.tips_title')}
          </h2>
          <div className="card p-5">
            <ul className="space-y-3">
              {tips.map((tip, i) => (
                <li key={i} className="flex items-start gap-3 text-[14px]">
                  <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-emerald-500" />
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* ── CTA ── */}
        <div className="card flex flex-col items-center gap-3 px-8 py-10 text-center">
          <BookOpen size={28} className="text-accent" />
          <p className="text-[15px] font-medium">
            {t('help.getting_started')}
          </p>
          <Link href="/editor" className="btn-primary mt-1 h-11 px-6 text-[14px]">
            {t('history.open_editor')} <ChevronRight size={15} aria-hidden />
          </Link>
        </div>
      </div>
    </>
  );
}

