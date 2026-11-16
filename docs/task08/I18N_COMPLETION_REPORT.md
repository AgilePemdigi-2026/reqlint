# I18N_COMPLETION_REPORT (Task 08 Phase 3)

**Mekanisme:** `lib/i18n.ts` — store persist `reqlint.ui_locale` (default `id`), kamus `translations` (kini **diekspor** untuk test), `t()` + `useT()` dengan fallback id → raw key.
**Bahasa:** `id` (default) + `en`. Toggle bahasa ada di app shell.

## 1. Inventarisasi & cakupan

Dikabelkan (hardcoded → `t()`) pada Task 08 — string yang ditambahkan Task 06/07 dan string inti alur produk:

| Surface | String yang dikabelkan |
|---|---|
| Editor | label "Evaluator:", 3 label opsi selector, toast backend diterima, error needs-backend (dengan {name}), toast fallback browser |
| Audit detail | "Audit tidak ditemukan" + desc, "Kembali ke editor", "Salin Hasil", badge Evaluator/Model/Generator, status generator (selesai/gagal), "Evaluator tidak tersedia", "— tidak ada fallback…", judul+desc advisory, status advisory (flagged/passed/unknown) |
| FindingsTable | judul, empty state (judul+desc), 4 header kolom, tautan "Lihat dalam editor" |
| SummaryCard | judul, "{n} temuan", "Analisis selesai", "Praktik penilaian", meter "Praktik Dokumen (heuristik)" |
| i18n lama diperbaiki | `register.subtitle`, `help.step3_desc` (klaim ISO dihapus) |

## 2. Keys & parity

- Total keys kini **211** (dari 190). Test baru `lib/i18n.test.ts`:
  - setiap key punya `id` dan `en` **non-empty**;
  - t() menghasilkan nilai EN saat locale EN dan fallback id → raw key;
  - label evaluator konsisten (Rule-Based/LLM/SLM tetap dikenali).
- Semua pasangan id/en lengkap: **0 key tidak lengkap** (terverifikasi test).

## 3. Sisa yang terdokumentasi (PARTIAL — bukan kegagalan skema)

1. **Landing page** (`/`, komponen `sections.tsx` + hero/footer): copy marketing masih ID statis dan **language toggle berada di app shell** (tidak di landing) → switching tidak memunculkan UI campuran di landing. Penanganan penuh landing = deferred (copy besar, nilai demo tercapai via app area).
2. **~18 string kecil** tersisa di halaman app tanpa i18n (umumnya aria-label dan label mikro; terinventarisasi via grep). Prioritas berikutnya bila diminta.
3. Export md/json: label dokumen mengikuti **bahasa cerita** via `meta.locale` (param) — bukan locale UI; sengaja agar bahasa laporan mengikuti bahasa cerita.
4. aria-label sebagian masih ID (mis. "Belum dievaluasi", "Lulus").

## 4. Language switching (verifikasi)

- Toggle bahasa (app shell) → `setUILocale` → semua komponen ber-`useT()` bereaktif (useSyncExternalStore).
- Locale persist di localStorage → refresh konsisten; SSR aman (store guard `typeof window`), tanpa hydration mismatch baru.
- Tidak ada navigasi yang mereset locale (store di luar router state).
- Dilarang diterjemahkan: `story_id`, `evaluator`, nama model, kode error (`LLM_EVALUATOR_UNAVAILABLE`), nama kolom API — tetap Inggris. ✅
