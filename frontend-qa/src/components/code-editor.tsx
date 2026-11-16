'use client';

import { useMemo } from 'react';
import { liveMarks, type Language } from '@/lib/analyzer';

const DEFAULT_MIN_LINES = 8;

interface Segment {
  text: string;
  marked: boolean;
}

/** Potong satu baris menjadi segmen biasa/bergaris-bawah berdasarkan rentang yang diberikan. */
function segmentsFor(line: string, lineStart: number, marks: Array<{ start: number; end: number }>): Segment[] {
  const out: Segment[] = [];
  let cursor = 0;
  for (const m of marks) {
    const s = Math.max(m.start - lineStart, 0);
    const e = Math.min(m.end - lineStart, line.length);
    if (e <= s || s < cursor) continue;
    if (s > cursor) out.push({ text: line.slice(cursor, s), marked: false });
    out.push({ text: line.slice(s, e), marked: true });
    cursor = e;
  }
  if (cursor < line.length) out.push({ text: line.slice(cursor), marked: false });
  return out;
}

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: Language;
  maxLength?: number;
  ariaLabel?: string;
  /** Task 09: placeholder mengikuti locale UI (opsional). */
  placeholder?: string;
  /** Jumlah baris minimum yang selalu ditampilkan (tinggi editor). */
  minLines?: number;
}

/**
 * Editor teks bernomor baris dengan garis bergelombang real-time.
 * Teknik: <textarea> transparan ditumpuk di atas lapisan "backdrop" dengan tipografi identik,
 * sehingga garis bawah dan nomor baris selalu sejajar tanpa sinkronisasi scroll.
 */
export function CodeEditor({
  value,
  onChange,
  language,
  maxLength,
  ariaLabel = 'Editor draf kebutuhan',
  placeholder,
  minLines = DEFAULT_MIN_LINES,
}: CodeEditorProps) {
  const marks = useMemo(() => liveMarks(value, language), [value, language]);

  const lines = useMemo(() => {
    const raw = value.split('\n');
    let offset = 0;
    const rows = raw.map((line) => {
      const row = { text: line, segments: segmentsFor(line, offset, marks) };
      offset += line.length + 1;
      return row;
    });
    while (rows.length < minLines) rows.push({ text: '', segments: [] });
    return rows;
  }, [value, marks, minLines]);

  return (
    <div className="relative overflow-hidden rounded-[20px] border border-line/[0.07] bg-field/70 focus-within:border-accent/40 focus-within:ring-4 focus-within:ring-accent/10">
      <span className="pointer-events-none absolute inset-y-0 left-[48px] w-px bg-line/[0.07]" aria-hidden />
      <div className="grid">
        <div className="editor-layer pointer-events-none select-none" aria-hidden>
          {lines.map((line, i) => (
            <div key={i} className="relative min-h-[26px]">
              <span className="absolute -left-[60px] top-0 w-[48px] text-center text-[12.5px] text-faint">{i + 1}</span>
              {line.segments.map((seg, j) =>
                seg.marked ? (
                  <span key={j} className="squiggle">
                    {seg.text}
                  </span>
                ) : (
                  <span key={j} className="text-transparent">
                    {seg.text}
                  </span>
                ),
              )}
              {'​'}
            </div>
          ))}
        </div>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          maxLength={maxLength}
          spellCheck={false}
          aria-label={ariaLabel}
          rows={1}
          placeholder={placeholder ?? 'Contoh: Sebagai pengguna, saya ingin … agar …'}
          className="editor-layer resize-none overflow-hidden border-0 bg-transparent text-ink caret-ink outline-none placeholder:text-faint"
        />
      </div>
      <span className="pointer-events-none absolute bottom-3 right-5 text-[10.5px] font-medium uppercase tracking-[0.1em] text-faint">
        Plain text
      </span>
    </div>
  );
}
