# Annotation QC Checklist (Koordinator/QC)

Checklist per batch, dijalankan setelah setiap ronde anotasi dikumpulkan. Semua pemeriksaan dapat dijalankan secara otomatis (skrip stdlib) kecuali yang ditandai [MANUAL].

## 1. Kelengkapan label

- [ ] Setiap baris cerita punya **tepat satu** label per kriteria: `PASS` | `FAIL` | `INSUFFICIENT_EVIDENCE` (huruf kapital persis).
- [ ] Tidak ada sel label kosong, `NaN`, `?`, `OK`, `1/0`, atau nilai lain di luar tiga nilai sah.
- [ ] Semua baris punya `annotator_id`, `annotation_round` ∈ {R1, R2}, dan keenam kolom `*_confidence` ∈ {LOW, MEDIUM, HIGH}.
- [ ] Jumlah baris per annotator = jumlah cerita batch (tidak ada yang terlewat).
- [ ] Kolom identitas (`story_id`, `project_id`, `language`, `original_text`) **identik** dengan batch sumber — annotator tidak mengubahnya.

## 2. Validitas evidence span

- [ ] Format `start-end` (1-based, inklusif), beberapa bukti dipisah `;` — tidak ada teks bebas di kolom evidence.
- [ ] `1 ≤ start ≤ end ≤ len(original_text)` untuk setiap rentang (validasi otomatis terhadap teks).
- [ ] Rentang yang dikutip benar-benar memuat frasa yang dirujuk rationale [MANUAL — sampling ≥ 10 span per batch].
- [ ] FAIL berbasis ketiadaan (MISSING_BENEFIT dsb.) memakai span seluruh teks `1-<len>`.
- [ ] PASS boleh tanpa evidence; FAIL/IE **wajib** punya evidence.

## 3. Konsistensi rationale

- [ ] Setiap FAIL/IE punya rationale diawali **kode tertutup** yang sah (daftar di Guideline §1–§6).
- [ ] Kode rationale sesuai kriterianya (mis. `MISSING_BENEFIT` hanya di kolom valuable).
- [ ] Pola `POLA-BARU:` di notes dikumpulkan — kandidat revisi guideline.
- [ ] [MANUAL] Baca sampel rationale FAIL (≥ 10 per kriteria): apakah penjelasan selaras dengan kode dan evidence?
- [ ] Tidak ada rationale yang mengandung informasi di luar teks ("aplikasi ini biasanya…", "tim ini pasti…").

## 4. Konsistensi antarbahasa (bila story berpasangan EN–ID dianotasi)

- [ ] Untuk setiap pasangan terjemahan, bandingkan label EN vs ID per annotator — catat tingkat perbedaan (diagnosis bahasa, bukan kesalahan wajib; perbedaan yang bisa dijelaskan konteks terjemahan boleh sah, tapi > 20% pasangan berbeda pada satu kriteria = sinyal definisi kriteria kurang stabil antarbahasa).
- [ ] Terjemahan kata kunci (sehingga/so that, dan/and, cepat/fast) tidak mengubah arah penilaian secara sistematis.
- [ ] Evidence span mengacu pada teks bahasa masing-masing (bukan posisi cerita pasangannya).

## 5. Duplikasi dan ID

- [ ] `story_id` unik per file; tidak ada ID di luar batch.
- [ ] Cerita duplikat/serupa dalam batch ditandai di notes (`DUPLIKAT-DENGAN:`) dan tetap dianotasi keduanya.
- [ ] `original_text` di file annotator **byte-identik** dengan sumber batch (tidak diedit).
- [ ] Pasangan terjemahan dalam satu batch tidak dipecah antar-annotator berbeda tanpa koordinasi (untuk analisis konsistensi antarbahasa).

## 6. Label mencurigakan (red flags — [MANUAL] untuk kasus tertanda otomatis)

- [ ] **All-pass massal**: cerita dengan 6×PASS berlebihan (> 80% batch) → sinyal ambang PASS terlalu longgar; sampling review wajib.
- [ ] **All-fail beruntun**: blok cerita berurutan 6×FAIL → cek apakah annotator lelah atau memang klaster cerita buruk.
- [ ] **IE berlebihan** pada satu kriteria (> ambang OD-5) → review definisi kriteria.
- [ ] Label yang **tidak konsisten dengan evidence-nya sendiri** (mis. `FAIL MISSING_BENEFIT` padahal teks memuat "so that …").
- [ ] Confidence `HIGH` pada banyak IE → kontradiktif; sampling review.
- [ ] Pola label mengikuti urutan baris (periodik) → indikasi penilaian mekanis.
- [ ] Waktu pengisian ekstrem (bila tersedia) — terlalu cepat per cerita.

## 7. Missing values

- [ ] Sel label kosong = **missing wajib diperbaiki** oleh annotator pemilik sebelum file diterima (bukan diisi QC).
- [ ] Sel evidence/rationale kosong pada PASS = sah. Pada FAIL/IE = wajib dilengkapi annotator.
- [ ] `notes` kosong = sah.
- [ ] Cerita rusak/terpotong sehingga tak bisa dianotasi: diberi IE + notes (`TEKS-RUSAK`) — **tidak dibuang diam-diam**; koordinator mencatat dan memutuskan (re-extract dari sumber / keluar dari batch).
- [ ] QC **tidak pernah** mengisi/mengubah label — QC hanya menandai dan mengembalikan ke annotator pemilik.

## 8. Penutup batch

- [ ] Semua poin di atas lulus → batch dinyatakan siap untuk agregasi agreement (Protocol §5) dan Round 2.
- [ ] Simpan laporan QC per batch (hasil checklist + temuan) untuk jejak audit.
- [ ] Ingat: agregasi agreement hanya untuk statistik — label individual tetap sumber kebenaran hingga adjudication.
