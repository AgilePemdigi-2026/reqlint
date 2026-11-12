import { analyze } from './analyze';
import { splitClauses } from './clauses';
import { rulesFor } from './rules';
import type { AcceptanceCriteria, Language, Revision } from './types';
import { STORY } from './rules';

const VERB_MAP: Record<string, string> = {
  disimpan: 'menyimpan', dibuat: 'membuat', dikirim: 'mengirim', ditampilkan: 'menampilkan',
  dicatat: 'mencatat', diverifikasi: 'memverifikasi', divalidasi: 'memvalidasi', dihapus: 'menghapus',
  diubah: 'mengubah', diperbarui: 'memperbarui', diakses: 'mengakses', dilindungi: 'melindungi',
  dienkripsi: 'mengenkripsi', diproses: 'memproses', dihitung: 'menghitung', ditolak: 'menolak',
  diterima: 'menerima', diperiksa: 'memeriksa', dikonfirmasi: 'mengonfirmasi', diunggah: 'mengunggah',
  diunduh: 'mengunduh', dilaporkan: 'melaporkan', dikelola: 'mengelola', dicadangkan: 'mencadangkan',
};

const PASSIVE_REWRITE =
  /^(?<obj>.+?)\s+(?<modal>harus|wajib|perlu|akan|dapat|bisa|boleh)\s+(?<verb>di\p{L}+)(?:\s+oleh\s+(?<agent>[^.!?,;]+?))?\s*(?<end>[.!?]*)$/iu;

const upperFirst = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
/** Turunkan huruf pertama kecuali kata berupa singkatan (huruf kedua juga kapital). */
const lowerFirst = (s: string) => (/^\p{Lu}\p{Lu}/u.test(s) ? s : s.charAt(0).toLowerCase() + s.slice(1));

/** "Data harus disimpan oleh sistem." → "Sistem harus menyimpan data." (hanya untuk kata kerja yang dikenal). */
function rewritePassiveId(clause: string): string {
  const m = PASSIVE_REWRITE.exec(clause);
  const g = m?.groups;
  if (!g) return clause;
  const active = VERB_MAP[g.verb.toLowerCase()];
  if (!active) return clause;
  const agent = g.agent?.trim() || 'sistem';
  return `${upperFirst(agent)} ${g.modal.toLowerCase()} ${active} ${lowerFirst(g.obj.trim())}${g.end ?? ''}`;
}

function reviseClause(text: string, lang: Language): string {
  let s = text;
  if (lang === 'id') s = rewritePassiveId(s);

  for (const rule of rulesFor(lang)) {
    if (!rule.replacement) continue;
    s = s.replace(new RegExp(rule.pattern.source, rule.pattern.flags), rule.replacement);
  }

  if (lang === 'id') {
    // Normalisasi gaya: "user" → "pengguna" (bukan bagian dari kata majemuk bertanda hubung).
    s = s.replace(/(?<![\p{L}\p{N}_-])(user)(?![\p{L}\p{N}_-])/giu, (w) =>
      w[0] === 'U' ? 'Pengguna' : 'pengguna',
    );
    s = s.replace(/\bdengan\s+(dalam\s+waktu)/gi, '$1');
  }
  return s.replace(/[ \t]{2,}/g, ' ').replace(/\s+([,.;!?])/g, '$1');
}

/** Buat draf revisi berbasis aturan. Angka pengganti adalah nilai contoh yang perlu disesuaikan tim. */
export function revise(text: string, lang: Language): Revision {
  let out = text;
  for (const c of [...splitClauses(text)].reverse()) {
    const revised = reviseClause(c.text, lang);
    if (revised !== c.text) out = out.slice(0, c.start) + revised + out.slice(c.end);
  }
  // P0.1/R2-1: Revision kini juga membawa evaluasi lokal atas teks asli agar
  // before/after memakai evaluator yang sama (skema konsisten dengan adapter).
  return { text: out, changed: out !== text, result: analyze(out, lang), originalLocal: analyze(text, lang) };
}

// ───────────── Acceptance criteria (BDD) ─────────────

export function acceptanceCriteria(text: string, lang: Language): AcceptanceCriteria | null {
  const clauses = splitClauses(text);
  const id = lang === 'id';

  for (const c of clauses) {
    const g = STORY[lang].parse.exec(c.text)?.groups;
    if (!g?.role || !g.goal) continue;
    const role = g.role.trim();
    const goal = g.goal.trim();
    return id
      ? {
          given: `${upperFirst(role)} berada pada konteks fitur terkait dan sistem dalam kondisi normal.`,
          when: `${upperFirst(role)} melakukan aksi: ${goal}.`,
          then: g.benefit
            ? `Sistem memenuhi kebutuhan tersebut sehingga tujuan tercapai: ${g.benefit.trim()}.`
            : 'Sistem memenuhi kebutuhan tersebut dan hasilnya dapat diverifikasi.',
        }
      : {
          given: `The ${role} is in the relevant feature context and the system is in a normal state.`,
          when: `The ${role} performs: ${goal}.`,
          then: g.benefit
            ? `The system fulfils the need so that the goal is met: ${g.benefit.trim()}.`
            : 'The system fulfils the need and the outcome can be verified.',
        };
  }

  const modal = id ? /\b(harus|wajib|akan)\b/i : /\b(shall|must|will)\b/i;
  const req = clauses.find((c) => modal.test(c.text));
  if (!req) return null;
  return id
    ? {
        given: 'Sistem dalam kondisi normal dan pengguna telah terautentikasi.',
        when: 'Kondisi pemicu terpenuhi (tentukan pemicu spesifik).',
        then: req.text,
      }
    : {
        given: 'The system is in a normal state and the user is authenticated.',
        when: 'The triggering condition occurs (specify the exact trigger).',
        then: req.text,
      };
}
