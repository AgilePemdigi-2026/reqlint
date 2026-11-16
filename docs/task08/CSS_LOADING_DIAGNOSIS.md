# CSS_LOADING_DIAGNOSIS (Task 08 Phase 1)

## Gejala

Halaman tampil sebagai HTML polos tanpa CSS saat local testing.

## Investigasi (empiris, bukan asumsi)

1. **Konfigurasi** — tailwind/postcss/next.config/layout import: semua benar (content glob mencakup `./src/**`, globals.css di-import layout, darkMode 'class').
2. **Live test produksi** (`next start -p 3000`):
   - HTML `/` merujuk `/_next/static/css/app/layout.css?v=…` (path app-router ber-versi).
   - **Request asset tersebut → HTTP 404** dengan body HTML (8.7 KB) — bukan CSS. Browser mendapat HTML untuk request stylesheet → tampil tanpa styling. **Ini akar gejalanya.**
3. **`.next` on-disk**: hanya ada `.next/static/css/a49d578a60420068.css` (hashed) — path yang dirujuk HTML **tidak ada di disk**.
4. **`next start` fresh pada `.next` terbaru** → `500 Internal Server Error`: `Cannot find module './vendor-chunks/next.js'` — output build server **kehilangan vendor-chunks**.
5. **`rm -rf .next` + clean rebuild** → vendor-chunks **tetap tidak di-emit** → **reproducible**, bukan sekadar artefak stale.
6. **Eksperimen terkontrol (A/B):** satu-satunya config non-standar adalah `outputFileTracing: false` di `next.config.js`.
   - Dengan flag → build selesai exit 0 tapi vendor-chunks tidak di-emit & asset CSS tidak konsisten.
   - **Flag dihapus + clean rebuild** → build inline paket dgn benar → `next start`: root **200**, HTML merujuk `/_next/static/css/6ac9028014178432.css`, **asset CSS HTTP 200 (47 KB)** berisi `:root` variables (`--ink`, dst.) dan utilities (`.card`, `.bg-ink`).
7. **Faktor pemicu kejadian user:** server `next start` lama yang masih berjalan ketika `.next` dibangun ulang (EADDRINUSE terbukti di log) → HTML in-memory merujuk asset build lama yang sudah tak ada.

## Root cause

**`outputFileTracing: false` di `next.config.js` merusak output build produksi Next 14.2 (App Router) di lingkungan ini**: server bundles kehilangan vendor-chunks dan asset CSS tidak ter-emit konsisten → CSS 404 → halaman tanpa CSS. Kondisi diperparah oleh server lama yang berjalan saat rebuild.

## Fix

1. **Hapus `outputFileTracing: false`** dari `next.config.js` (nilai default = true; file `.nft.json` tracing yang dihasilkan kecil dan tidak mengganggu `next start` maupun Docker).
2. **Prosedur lokal yang benar** (didokumentasikan): matikan server lama → `next build` → `next start`. Jangan rebuild saat server berjalan.

## Verifikasi pasca-fix (eksekusi nyata)

- `npx next build` → exit 0, clean.
- `next start` fresh → `/`, `/editor`, `/login` = **200**; asset CSS `6ac9028014178432.css` = **200, 47,009 bytes**, berisi `:root` variables + utilities Tailwind.
- ISO sweep pada HTML live: landing/editor/login = 0 kecocokan "29148".
- Selektor evaluator hadir di bundle produksi (chunk editor/audit memuat "Traditional ML" & radiogroup).

## Catatan deployment

Docker/Coolify membangun di container fresh (build + start dalam lifecycle sama) sehingga tidak mewarisi `.next` stale — root cause ini spesifik workflow lokal. Tetap: flag dihapus permanen agar parity lokal↔Docker terjaga.
