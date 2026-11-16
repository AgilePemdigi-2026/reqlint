'use client';

import { Eye, EyeOff } from 'lucide-react';
import { useId, useState } from 'react';
import { useT } from '@/lib/i18n';

interface FieldProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label: string;
  error?: string;
}

export function TextField({ label, error, ...props }: FieldProps) {
  const id = useId();
  return (
    <div>
      <label htmlFor={id} className="label">
        {label}
      </label>
      <input
        id={id}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-err` : undefined}
        className={`field ${error ? 'border-rose-400/70 focus:border-rose-400 focus:ring-rose-400/15' : ''}`}
        {...props}
      />
      {error && (
        <p id={`${id}-err`} className="mt-1.5 text-[12.5px] text-rose-600 dark:text-rose-400">
          {error}
        </p>
      )}
    </div>
  );
}

export function PasswordField({ label, error, children, ...props }: FieldProps & { children?: React.ReactNode }) {
  const id = useId();
  const t = useT();
  const [shown, setShown] = useState(false);
  return (
    <div>
      <label htmlFor={id} className="label">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type={shown ? 'text' : 'password'}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-err` : undefined}
          className={`field pr-12 ${error ? 'border-rose-400/70 focus:border-rose-400 focus:ring-rose-400/15' : ''}`}
          {...props}
        />
        <button
          type="button"
          onClick={() => setShown((s) => !s)}
          aria-label={shown ? t('fields.hide_password') : t('fields.show_password')}
          className="absolute right-3 top-1/2 inline-flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full text-muted transition hover:text-ink"
        >
          {shown ? <EyeOff size={18} strokeWidth={1.6} /> : <Eye size={18} strokeWidth={1.6} />}
        </button>
      </div>
      {error && (
        <p id={`${id}-err`} className="mt-1.5 text-[12.5px] text-rose-600 dark:text-rose-400">
          {error}
        </p>
      )}
      {children}
    </div>
  );
}
