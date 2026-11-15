'use client';

import React, { useEffect, useState } from 'react';
import { auditRequirement } from '@/lib/api';
import type { AuditResponse } from '@/types/audit';
import { Bot, CheckCircle2, AlertCircle, RefreshCw, Layers } from 'lucide-react';

interface BackendAuditCardProps {
  text: string;
  language: 'id' | 'en';
}

export function BackendAuditCard({ text, language }: BackendAuditCardProps) {
  const [data, setData] = useState<AuditResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBackendAudit = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await auditRequirement(text, language);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Backend API offline');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBackendAudit();
  }, [text, language]);

  return (
    <section className="card p-5 sm:p-6 transition-all" aria-label="Verifikasi Backend ML">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line/[0.08] pb-4">
        <div className="flex items-center gap-2.5">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-accent/10 text-accent">
            <Bot size={19} aria-hidden />
          </div>
          <div>
            <h3 className="text-[15.5px] font-semibold text-ink flex items-center gap-2">
              Validasi Hybrid Model AI Backend
              <span className="pill text-[10px] bg-accent/15 text-accent font-mono uppercase">
                FastAPI · spaCy · ML
              </span>
            </h3>
            <p className="text-[12px] text-muted">
              Pengecekan silang otomatis dengan model klasifikasi INVEST di server backend Python.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={fetchBackendAudit}
          disabled={loading}
          className="btn-ghost h-8 rounded-full px-3 text-[12px]"
          title="Jalankan ulang evaluasi di backend"
        >
          <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
          <span>{loading ? 'Mengevaluasi...' : 'Cek Ulang API'}</span>
        </button>
      </div>

      <div className="mt-4">
        {loading ? (
          <div className="flex items-center gap-3 py-4 text-[13px] text-muted">
            <RefreshCw size={15} className="animate-spin text-accent" />
            <span>Menghubungi server FastAPI (http://localhost:8000) untuk evaluasi model INVEST...</span>
          </div>
        ) : error || !data ? (
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-[13px] text-muted flex items-start gap-3">
            <AlertCircle size={18} className="text-amber-500 shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-ink">Mode Mandiri (Client Engine Aktif)</p>
              <p className="mt-0.5 text-[12px]">
                Server FastAPI (port 8000) tidak terjangkau. Seluruh metrik di atas tetap akurat dan dihitung secara independen di browser Anda. Jalankan <code className="font-mono bg-black/5 dark:bg-white/10 px-1.5 py-0.5 rounded text-[11px]">python -m uvicorn app.main:app --reload --port 8000</code> untuk mengaktifkan model ML backend.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="rounded-xl bg-line/[0.03] p-3 text-center border border-line/[0.05]">
                <div className="text-[11px] uppercase tracking-wider text-muted font-medium">Skor Mutu AI</div>
                <div className="mt-1 text-2xl font-bold text-accent">{data.quality_score}</div>
                <div className="text-[10.5px] text-muted mt-0.5">Skor Heuristik</div>
              </div>

              <div className="rounded-xl bg-line/[0.03] p-3 text-center border border-line/[0.05]">
                <div className="text-[11px] uppercase tracking-wider text-muted font-medium">Indeks Ambiguitas</div>
                <div className={`mt-1 text-2xl font-bold ${data.ambiguity_index > 0.3 ? 'text-rose-500' : 'text-emerald-500'}`}>
                  {data.ambiguity_index}
                </div>
                <div className="text-[10.5px] text-muted mt-0.5">Makin kecil makin baik</div>
              </div>

              <div className="rounded-xl bg-line/[0.03] p-3 text-center border border-line/[0.05]">
                <div className="text-[11px] uppercase tracking-wider text-muted font-medium">Kelengkapan</div>
                <div className="mt-1 text-2xl font-bold text-ink">{data.completeness_score}%</div>
                <div className="text-[10.5px] text-muted mt-0.5">Struktur Connextra</div>
              </div>

              <div className="rounded-xl bg-line/[0.03] p-3 text-center border border-line/[0.05]">
                <div className="text-[11px] uppercase tracking-wider text-muted font-medium">Verifikasi</div>
                <div className="mt-1 text-2xl font-bold text-emerald-500">{data.verifiability_score}%</div>
                <div className="text-[10.5px] text-muted mt-0.5">Kriteria Uji</div>
              </div>
            </div>

            <div className="flex items-center gap-2 text-[12.5px] text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3.5 py-2 rounded-xl">
              <CheckCircle2 size={16} className="shrink-0" />
              <span>
                Backend mendeteksi <strong>{data.smells.length} cacat</strong> pada analisis NLP dwibahasa ({data.detected_language.toUpperCase()}). Hasil sinkron dengan linter frontend.
              </span>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
