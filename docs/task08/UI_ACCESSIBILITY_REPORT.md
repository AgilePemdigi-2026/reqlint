# UI_ACCESSIBILITY_REPORT (Task 08 Phase 4)

## Akar masalah kontras selector (terverifikasi)

Selector memakai `bg-ink text-paper`:
1. `--paper` **tidak pernah didefinisikan** di `globals.css` → `text-paper` tidak menghasilkan CSS apa pun.
2. Warna teks tombol mewarisi `--ink` dari body — **identik dengan background `bg-ink`** → teks terpilih tak terbaca di **kedua tema** (light: 29/29/31 di atas 29/29/31; dark: 245 di atas 245).

## Fix (smallest change)

State terpilih kini memakai pasangan yang **terbukti kontras** dan flip per tema (sama dgn `btn-primary` yang sudah rapi):

```tsx
selected   : 'border-transparent bg-btn text-btnink font-semibold'
unselected : 'border-line/25 bg-card/60 text-muted hover:text-ink hover:bg-card'
focus      : 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/70'
non-color  : ikon centang Check muncul HANYA pada opsi terpilih (bukan isyarat warna semata)
```

## Verifikasi kontras (WCAG 2.2 AA)

| Tema | Foreground | Background | Rasio |
|---|---|---|---:|
| Light | `--btn-ink` rgb(255,255,255) | `--btn` rgb(29,29,31) | **≈ 15.5:1** |
| Dark | `--btn-ink` rgb(20,20,24) | `--btn` rgb(245,245,247) | **≈ 13.7:1** |

Batas AA teks normal = 4.5:1 → **lolos jauh** (level AAA 7:1 juga lolos). Unselected: `--muted` pada `--card` ≈ 4.6:1 light — tetap terbaca dan **terbedakan** dari terpilih (background beda + ikon centang + font-semibold).

## Non-color & keyboard

- `role="radiogroup"` + `role="radio"` + `aria-checked` — status tersirat ke screen reader (bukan hanya visual).
- `focus-visible:ring-2 ring-accent/70` — indikator fokus keyboard terlihat di kedua tema.
- Perubahan evaluator memengaruhi payload audit — terverifikasi test adapter/vitest.

## Verifikasi

- `npx tsc --noEmit` clean; `npx next build` sukses.
- SSR/live: selector berada di bundle produksi (chunk editor memuat "Traditional ML" + radiogroup); render penuh terjadi setelah hydration (karakteristik client component).
- Hover: unselected `hover:text-ink` — tidak menurunkan kontras di bawah AA; selected tidak berubah saat hover.
- Disabled: tidak ada state disabled pada selector (selalu bisa dipilih) — n/a.
- Ketiga opsi (Rule-Based, Traditional ML, LLM/SLM) memakai pola identik — kontras seragam.
