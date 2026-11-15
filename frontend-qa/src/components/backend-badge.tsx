'use client';

import React, { useEffect, useState } from 'react';
import { checkBackendHealth } from '@/lib/api';
import { Server, RefreshCw } from 'lucide-react';
import { useT } from '@/lib/i18n';

export function BackendHealthBadge() {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [checking, setChecking] = useState(false);
  const t = useT();

  const check = async () => {
    setChecking(true);
    const res = await checkBackendHealth();
    setStatus(res.ok ? 'online' : 'offline');
    setChecking(false);
  };

  useEffect(() => {
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <button
      type="button"
      onClick={check}
      title={
        status === 'online'
          ? t('badge.online_title')
          : t('badge.offline_title')
      }
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[11.5px] font-medium transition-all ${
        status === 'online'
          ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/25 hover:bg-emerald-500/20'
          : status === 'offline'
          ? 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/25 hover:bg-amber-500/20'
          : 'bg-black/[0.05] dark:bg-white/[0.07] text-muted'
      }`}
    >
      <span className="relative flex h-2 w-2">
        {status === 'online' && (
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
        )}
        <span
          className={`relative inline-flex rounded-full h-2 w-2 ${
            status === 'online'
              ? 'bg-emerald-500'
              : status === 'offline'
              ? 'bg-amber-500'
              : 'bg-muted animate-pulse'
          }`}
        />
      </span>
      <span className="hidden sm:inline">
        {status === 'online' ? t('badge.online') : status === 'offline' ? t('badge.offline') : t('badge.checking')}
      </span>
      {checking && <RefreshCw size={11} className="animate-spin ml-0.5" />}
    </button>
  );
}
