# Historical Annotator Interview Guide (Task 04C)

**Tujuan:** memperjelas provenance 221 label historis Family B melalui percakapan singkat yang **netral dan tidak menuduh**, dengan annotator asli (kommiter `236ea51`/`e23701c`).
**Batas:** **tidak memblokir Task 05.** Jawaban tidak mengubah label historis; hanya memperbarui status provenance di dokumen validasi.
**Format yang disarankan:** percakapan 30–45 menit atau jawaban tertulis; boleh asinkron. Tanyakan izin sebelum merekam/mengutip.

## Framing pembuka (baca ke annotator)

> "Kami sedang menata ulang dataset untuk benchmark. Anotasi yang kamu kerjakan dulu adalah bagian penting dari sejarah proyek ini dan kami ingin menghormatinya — bukan menguji apakah kamu benar atau salah. Ada beberapa hal yang hanya kamu yang tahu jawabannya, dan itu akan membantu kami memutuskan bagaimana data lama ini diperlakukan. Tidak ada jawaban yang 'salah'."

**Pembedaan yang disampaikan kepada annotator:** yang kami tahu dari Git hanyalah *kapan file berubah dan oleh siapa di-commit*. Yang kami tidak tahu adalah *bagaimana kamu benar-benar mengerjakannya* — itulah yang ingin kami dengar langsung.

---

## Bagian 1 — Pekerjaan manual (Git: hanya membuktikan commit, bukan cara kerja)

1. Apakah 221 baris berlabel pada dataset terakhir sebelum model-assisted (25 Okt) dikerjakan **manual** oleh kamu, atau ada bagian yang dihasilkan alat/proses lain?
2. Berapa perkiraan jumlah cerita yang benar-benar kamu nilai sendiri?
3. Apakah ada sesi lain sebelum/sesudah tanggal itu yang tidak pernah di-push?

## Bagian 2 — Interpretasi enam kriteria

4. Bagaimana kamu mengartikan tiap kriteria saat itu (I, N, V, E, S, T)? Apakah kamu membaca pedoman anotasi yang ada?
5. Apakah ada kriteria yang kamu anggap "sulit dinilai" atau sering ragu? (ini membantu memetakan kemungkinan bahwa `0` berarti "tidak yakin", bukan "buruk")

## Bagian 3 — Makna 0 dan 1

6. Dalam praktik, apa arti `0` dan `1` untukmu? (mis. `0` = buruk? `0` = ragu/tidak bisa dinilai? bergantung kriteria?)
7. Apakah `annotator_a` kamu isi sebagai penilaian keseluruhan, atau dihitung dari enam kolom?

## Bagian 4 — Pasangan EN–ID

8. Untuk story yang ada versi Inggris dan Indonesianya: apakah keduanya kamu nilai **terpisah**, atau label versi satu dipakai/dipindah ke versi lain? (Git menunjukkan label EN dan ID identik 100% — kami ingin tahu proses di baliknya)

## Bagian 5 — Linimasa & cadangan lokal

9. Kapan sesi anotasi dilakukan, berapa lama, dengan alat apa?
10. Apakah masih ada **file cadangan lokal** (Excel/CSV versi kerja) dari sebelum commit 27 Okt? Bila ada, dapatkah dibagikan? (ini bisa menunjukkan apakah ada label manual tambahan yang tertimpa)

## Bagian 6 — 24 perbedaan antar-snapshot

11. Kami menemukan 24 story yang labelnya berubah antara dua versi dataset sebelum model (daftar terlampir). Apakah kamu ingat mengapa nilai-nilai ini berubah — revisi sadar, salah salin, atau proses lain?

## Bagian 7 — Izin penggunaan penelitian

12. Apakah kamu mengizinkan anotasi tersebut (dan identitasmu sebagai annotator) dipakai dan disebut dalam penelitian/benchmark ReqLint?
13. Apakah kamu ingin anonim, atau dicantumkan sebagai annotator?

---

## Templat pencatatan jawaban

| # | Pertanyaan | Jawaban | Bukti pendukung (file/backup) | Tanggal konfirmasi |
|---|---|---|---|---|
| 1 | … | | | |

## Pemisahan bukti (aturan wajib saat menulis laporan)

- **Fakta Git (sudah terverifikasi):** commit `236ea51` (25 Okt) memuat 221 baris berlabel; `e23701c` (27 Okt) menambah `coba 2.py` + model dan menimpa 116 baris; `annotator_a` = agregat all-pass di semua versi; `annotator_b` kosong.
- **Yang hanya bisa dijawab annotator:** semua pertanyaan di atas.
- **Jangan** menampilkan label historis sebagai "kunci jawaban" atau membandingkannya di depan annotator dgn nada menguji.
- **Tidak memblokir Task 05:** rekonstruksi dataset kanonik berjalan paralel; hasil interview hanya memperbarui status provenance (Assessment §4 / Integration Spec §3) dan keputusan OD-7/OD-9.
