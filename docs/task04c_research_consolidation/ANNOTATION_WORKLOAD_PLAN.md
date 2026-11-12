# Annotation Workload & Capacity Plan (v1.0)

**Prinsip:** angka durasi **tidak direkayasa** — diukur dari pilot (§11.8 brief: pilot waktu 10 story). Sebelum pilot ada, semua estimasi bersifat **parametrik/skenario**, bukan prediksi. Unit kerja = **1 story × 1 annotator** (termasuk membaca, menilai 6 kriteria, mengisi evidence/rationale).

## 1. Volume target sementara (ceiling, bukan jaminan)

| Split | Stories | Annotator | Unit anotasi |
|---|---:|---|---:|
| Calibration | 30 | 2 | 60 |
| Training | 40 | 1 | 40 |
| Validation | 10 | 1 | 10 |
| Test | 40 | 2 | 80 |
| **Total** | **120** | | **190 unit** |

Di luar ini (bukan bagian 190): Round 2 re-review, adjudication, dan **historical validation 60 baris — DEFERRED** (tidak dihitung wajib; lihat §4).

## 2. Beban per annotator (2 annotator, tanpa split bahasa — OD-4 opsi a)

| Komponen | Unit per annotator |
|---|---:|
| Calibration | 30 |
| Training | 20 (dibagi dua) |
| Validation | 5 (dibagi dua) |
| Test | 40 |
| **Total Round 1** | **95** |
| Round 2 | subset konflik (diukur, lihat §3) |
| Adjudication | subset sisa konflik |

Bila OD-4 memilih split bahasa untuk train/val, beban tiap annotator berubah mengikuti pembagian — hitung ulang dengan rumus §3.

## 3. Formula estimasi

```
jam_total(ronde)   = unit × p / 60            (p = menit per story, dari pilot)
jam_R2             = konflik × p_r2 / 60      (konflik = unit × tingkat_konflik; p_r2 biasanya < p)
jam_adjudication   = sisa_konflik × p_adj / 60
hari_kalender      = jam_total / (J × h × f)  (J = jumlah annotator aktif, h = jam efektif/hari,
                                               f = faktor ketersediaan 0..1)
```

**Prosedur pengukuran pilot (10 story):** pilih 10 story beragam (EN+ID, sehat+bermasalah); annotator mencatat waktu mulai–selesai per cerita; koordinator menghitung p per annotator dan per bahasa; **ulangi setelah revisi guideline** bila ada. Hasil pilot menggantikan angka skenario di §4.

## 4. Tabel sensitivitas (ILUSTRATIF — bukan pengukuran)

Asumsi 190 unit Round 1 (tanpa R2/adjudication):

| p (menit/story) | Total jam | Contoh: 2 annotator × 1 jam/hari efektif |
|---:|---:|---:|
| 2 | 6,3 | ±3 hari kerja |
| 3 | 9,5 | ±5 hari kerja |
| 5 | 15,8 | ±8 hari kerja |
| 8 | 25,3 | ±13 hari kerja |

Jangan gunakan angka ini sebagai komitmen; **ganti dengan hasil pilot begitu tersedia.** Story historis yang lebih kompleks (potongan panjang) bisa melampaui p terbesar di tabel.

## 5. Pemisahan beban

| Paket | Unit | Status |
|---|---:|---|
| Calibration (30×2) | 60 | wajib — gate kualitas |
| Production R1 (train 40 + val 10 + test 80) | 130 | wajib |
| Round 2 | = konflik × 1 | terukur saat berjalan |
| Adjudication | = sisa konflik | terukur saat berjalan |
| **Historical validation (60 baris)** | **60** | **DEFERRED** — tidak dijadwalkan; hanya bila kapasitas tersisa dan OD disetujui |

## 6. Penjadwalan realistis

- Dasarkan pada **kapasitas aktual** yang dilaporkan tiap annotator saat onboarding (jam/hari yang realistis mereka sisihkan), bukan asumsi penuh waktu.
- Sisipkan buffer ≥ 25% untuk QC, Round 2, dan miskomunikasi.
- Kapan pun target tidak tercapai dgn kualitas terjaga → **turunkan volume** (§7), bukan kompresi waktu per story.

## 7. Alokasi alternatif bila target infeasible

| Tier | Cal (×2) | Train (×1) | Val (×1) | Test (×2) | Total unit |
|---|---:|---:|---:|---:|---:|
| T1 (rencana awal) | 30 | 40 | 10 | 40 | 190 |
| T2 | 20 | 24 | 8 | 30 | 132 |
| T3 (minimum layak) | 12 | 16 | 6 | 24 | 94 |

Batasan semua tier: calibration & test tetap **dua annotator**; test tetap dibekukan; kalibrasi tetap di luar train/val/test; penurunan jumlah dilaporkan + alasan di changelog. Di bawah T3, keluaran benchmark dinyatakan eksploratori.
