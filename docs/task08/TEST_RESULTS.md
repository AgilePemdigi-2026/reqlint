# TEST_RESULTS (Task 08)

**Eksekusi nyata 2026-11-15, setelah seluruh perubahan Task 08.** Baseline Task 07: pytest 91, vitest 45, BDD 32, tsc clean, build sukses.

## Hasil

| Suite | Perintah | Hasil | Δ |
|---|---|---:|---|
| Backend pytest | `python -m pytest backend/tests -q` | **91 passed** (×2 run: awal 66,5 s & akhir 91,7 s) | tanpa regresi |
| BDD runner | `python run_bdd.py` | **32 passed** (32,2 s) | tanpa regresi |
| Frontend vitest | `npx vitest run` | **51 passed** (6 file) | **+6** (parity i18n 2 + evaluator options 2 + export integrity 7 − dipindah pengelompokan; total 45→51: +6 test Task 08) |
| TypeScript | `npx tsc --noEmit` | **clean** (setelah 3 perbaikan type: adapter return-type, LABELS, `seq` fixture) | — |
| Production build | `npx next build` | **sukses** (exit 0, 2×) | — |
| Live CSS verification | curl/python ke `next start` | asset CSS **HTTP 200, 47,009 bytes** berisi `:root` vars + utilities; halaman /, /editor, /login = 200 | — |
| Live ISO sweep | curl HTML landing/editor/login/help/register | **0 kemunculan "29148"** | — |
| Docker build/compose | — | **BLOCKED** (Docker tidak terinstal; dinyatakan eksplisit — bukan "passed") | — |

## Test baru Task 08 (6)

`src/lib/i18n.test.ts` (2 file uji digabung):
1. Paritas kamus: setiap key punya `id` + `en` non-empty.
2. Set locale EN → `t('evaluator.llm')` = 'LLM/SLM'; fallback raw key utk key tak dikenal.
3. `EVALUATOR_OPTIONS` tepat 3 evaluator + default `rule_based`.
4. Setiap `labelKey` ada di kamus.

`src/lib/export.test.ts` (+7, Task 07):
- md/json membawa identitas evaluator + model version; advisory terpisah; tanpa klaim ISO; tanpa meta → tanpa klaim.

## CSS chain (live)

```
HTML /  →  /_next/static/css/6ac9028014178432.css  →  HTTP 200, 47,009 bytes
           :root variables (--ink …)  +  Tailwind utilities (.card, .bg-ink, …)
Halaman: / 200 · /editor 200 · /login 200 · /history 200 · /help 200 · /register 200 · /contact 200
ISO sweep HTML: landing 0 · editor 0 · login 0 · help 0 · register 0
```

## Catatan kejujuran

- Dua test Task 07 sempat gagal saat transisi label (advisory inversion + prefix heading `## ` hilang saat refactor LABELS) — diperbaiki, bukan disembunyikan; keduanya kini bagian dari test yang hijau.
- `docker build/compose` dinyatakan **BLOCKED**, bukan passed.
