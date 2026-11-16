#!/usr/bin/env node
/**
 * Task 09 — i18n source audit.
 *
 * Heuristic scanner for user-facing strings that bypass the i18n dictionary
 * in TSX components/pages. It deliberately distinguishes user-facing text
 * from identifiers, CSS classes, API values, model names and machine-readable
 * error codes via allow-lists below.
 *
 * Heuristics are conservative — the report is an AID for rendered-page
 * verification, never a substitute for it (per docs/task09 requirements).
 *
 * Usage: node scripts/i18n-source-audit.mjs
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(fileURLToPath(new URL('.', import.meta.url)), '..');

// Files known to contain user-facing strings but NOT rendered by any route
// (legacy/unused components — documented in docs/task09, out of scope).
const KNOWN_DEAD = [
  'src/components/analysis/AuditScorecard.tsx',
  'src/components/analysis/SmellList.tsx',
  'src/components/audit/backend-audit-card.tsx',
  'src/components/editor/RequirementEditor.tsx',
];

// Technical tokens allowed verbatim in UI (recognized terminology).
const TECH_TOKENS = /^(reqlint|invest|fastapi|spacy|api|jwt|pdf|csv|json|markdown|gherkin|bdd|iso|nlp|ml|llm|slm|en|id|url|http|https|plain text|bom|dev|stage[12]?|given|when|then|pass|fail|insufficient_evidence|rule-based|traditional ml|user story|model version|allam|gpt-oss|qwen|groq|ollama|phi3|llama|tbd|role|action|benefit|before ?\/ ?after|independen|negotiable|valuable|estimable|small|testable|independent|ux|ui|ai|quality scorecard|diff viewer|1-click|.+@.+\..+|[\d\s.,:/%()\-–·#>→+*✦◌]*|[a-z0-9._/-]+)$/i;

// CSS/Tailwind class and identifier-ish strings (never user-facing).
const CSSISH = /^(bg|text|border|rounded|flex|grid|gap|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|w|h|min|max|inline|block|hidden|sr|hover|dark|focus|disabled|animate|transition|whitespace|truncate|font|leading|tracking|shadow|opacity|items|justify|content|self|place|object|overflow|z|absolute|relative|fixed|sticky|inset|top|right|bottom|left|basis|grow|shrink|divide|ring|outline|fill|stroke|decorate|underline|uppercase|lowercase|capitalize|italic|normal|bold|semibold|medium|light|mono|sans|serif|select|pointer|cursor|resize|scroll|snap|will|content-|appearance|accent|caret)[\w[\]/.#-]*$/i;

// Keys / routes / enum-ish values.
const KEYS = /^(nav\.|login\.|register\.|history\.|contact\.|help\.|evaluator\.|editor\.|audit\.|findings\.|summary\.|forgot\.|reset\.|general\.|landing\.|demo\.|revision\.|acceptance\.|diff\.|scorecard\.|badge\.|category\.|grade\.|tagline\.|ai_status\.|adapter\.|validation\.|api\.|llm_error\.|\/|#|[a-z-]+:[a-z-]+)/i;

function* walk(dir) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) yield* walk(full);
    else yield full;
  }
}

const files = [...walk(join(ROOT, 'src'))].filter((f) => f.endsWith('.tsx'));

const findings = [];
let flaggedTotal = 0;

for (const file of files) {
  const rel = relative(ROOT, file).replace(/\\/g, '/');
  const src = readFileSync(file, 'utf8');
  const flagged = [];

  const add = (s, kind, line) => {
    const text = s.trim();
    if (!text) return;
    if (CSSISH.test(text)) return;
    if (KEYS.test(text)) return;
    if (TECH_TOKENS.test(text)) return;
    if (/^[A-Z0-9_]+$/.test(text) && text.length < 30) return; // SCREAMING_CASE codes
    if (/^[{}\[\]<>\\|`^~]/.test(text)) return;
    flagged.push({ kind, line, text: text.length > 90 ? text.slice(0, 90) + '…' : text });
  };

  const lines = src.split('\n');
  lines.forEach((line, idx) => {
    const n = idx + 1;
    // 1) toast('...') / toast(`...`) literals
    for (const m of line.matchAll(/\btoast\(\s*['"`]([^'"`]+)['"`]/g)) add(m[1], 'toast', n);
    // 2) user-facing JSX attributes
    for (const m of line.matchAll(/\b(?:aria-label|placeholder|title|aria-description)=\{?['"]([^'"]+)['"]/g)) add(m[1], 'attr', n);
    // 3) JSX text: >text< on a single line (skip tags/components/braces)
    for (const m of line.matchAll(/>\s*([^<>{}]+?)\s*<\//g)) {
      const inner = m[1];
      if (inner.includes('{') || inner.includes('`')) continue;
      add(inner.replace(/&\w+;/g, ' '), 'jsx', n);
    }
    // 4) window.confirm('...') literals
    for (const m of line.matchAll(/window\.confirm\(\s*['"`]([^'"`]+)['"`]/g)) add(m[1], 'confirm', n);
  });

  if (flagged.length) {
    flaggedTotal += flagged.length;
    findings.push({ file: rel, dead: KNOWN_DEAD.includes(rel), flagged });
  }
}

console.log('══ i18n source audit — hardcoded user-facing strings (heuristic) ══');
for (const f of findings) {
  console.log(`\n${f.file}${f.dead ? '  [KNOWN-LEGACY/UNRENDERED]' : ''} — ${f.flagged.length}`);
  for (const it of f.flagged) console.log(`  L${it.line} [${it.kind}] ${JSON.stringify(it.text)}`);
}
console.log(`\nTOTAL flagged strings: ${flaggedTotal}`);
console.log('Files with flags (rendered surfaces):', findings.filter((f) => !f.dead).length);
console.log('\nNOTE: heuristic aid only — verify rendered pages in both locales for acceptance.');
process.exit(0);
