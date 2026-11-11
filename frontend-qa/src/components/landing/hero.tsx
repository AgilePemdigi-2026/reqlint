import { ArrowRight, Lock, ShieldCheck } from 'lucide-react';
import Link from 'next/link';
import { DemoCard } from './demo-card';

export function Hero() {
  return (
    <section className="mx-auto grid max-w-[1280px] items-start gap-12 px-6 pb-24 pt-12 lg:grid-cols-[1fr_600px] lg:gap-16 lg:pt-20">
      <div className="lg:pt-14">
        <a
          href="#standar"
          className="inline-flex items-center gap-2 rounded-full bg-black/[0.05] px-4 py-2 text-[14.5px] text-ink/60 transition hover:text-ink dark:bg-white/[0.07]"
        >
          Mengacu pada ISO 29148 &amp; INVEST <ShieldCheck size={15} aria-hidden />
        </a>

        <h1 className="mt-5 text-[42px] font-medium leading-[1.04] tracking-[-0.03em] sm:text-[60px] lg:text-[66px]">
          <span className="block">Cek kualitas User Story</span>
          <span className="block">sebelum jadi bug.</span>
        </h1>

        <p className="mt-9 max-w-[640px] text-[18px] leading-[1.75] text-ink/60 lg:text-[19px]">
          ReqLint mengaudit draf kebutuhan Anda secara real-time: menandai istilah ambigu, kalimat pasif, dan klausul yang
          tidak bisa diuji — lengkap dengan skor, saran revisi, dan acceptance criteria. Cocok untuk analis bisnis, product
          owner, QA, dan mahasiswa rekayasa perangkat lunak.
        </p>

        <div className="mt-9 max-w-[600px] rounded-2xl bg-black/[0.045] p-6 dark:bg-white/[0.06]">
          <p className="text-[21px] font-medium">Mulai dalam hitungan detik</p>
          <p className="mt-1 text-[14.5px] text-ink/55">
            Tempel dari Jira, Confluence, Notion, atau Google Docs — atau unggah PDF. Tanpa instalasi.
          </p>
          <div className="mt-5 flex flex-wrap items-center gap-3">
            <Link
              href="/register"
              className="inline-flex h-12 items-center gap-2.5 rounded-full border border-black/25 bg-white/50 px-6 text-[16px] font-medium transition hover:bg-white dark:border-white/25 dark:bg-white/[0.06] dark:hover:bg-white/10"
            >
              Daftar gratis <ArrowRight size={17} aria-hidden />
            </Link>
            <Link href="/editor" className="px-3 text-[15.5px] font-medium text-ink/70 transition hover:text-ink">
              Buka editor
            </Link>
          </div>
        </div>
      </div>

      <div>
        <DemoCard />
        <p className="mt-5 flex items-center justify-center gap-2 text-[15px] text-ink/55">
          <Lock size={15} aria-hidden /> Analisis pada demo ini berjalan di browser Anda — teks demo tidak dikirim ke server.
        </p>
      </div>
    </section>
  );
}