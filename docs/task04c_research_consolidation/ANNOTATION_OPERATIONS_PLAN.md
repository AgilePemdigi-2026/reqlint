# Annotation Operations Plan (v1.0)

**Prinsip:** ringan, teraudit, bisa dijalankan oleh **koordinator yang ditunjuk** (tidak mengasumsikan project owner mengerjakan semua sendiri). Detail substansi anotasi tidak diduplikasi — acuan: Guideline, Handbook, Protocol, QC Checklist (folder `annotation_preparation/`).

## 1. Peran & onboarding

| Peran | Orang | Tugas |
|---|---|---|
| Project owner | — | Keputusan metodologis (OD), persetujuan alokasi |
| Koordinator | ditunjuk (bisa bukan owner) | batch, QC, statistik, arsip, komunikasi annotator |
| Annotator A-01, A-02 | dua orang lain | anotasi independen |
| A-03 (opsional) | 1 orang | adjudication |

**Onboarding checklist (per annotator):** baca Guideline + Handbook; terima batch + template; konfirmasi memahami 3 label & kode rationale; konfirmasi aturan independensi & larangan melihat label historis/model; uji buka file (encoding); mulai hanya setelah koordinator menandai batch `ASSIGNED`.

## 2. Alur kerja end-to-end

1. **Kalibrasi (30)** → QC → statistik agreement → revisi guideline bila perlu (Protocol §1).
2. **Round 1 produksi** — anotator bekerja independen per batch (Protocol §2).
3. **QC checklist** per batch yang dikumpulkan.
4. **Round 2** — hanya kriteria konflik (Protocol §3).
5. **Adjudication** — sisa konflik (Protocol §4).
6. **Konsolidasi** — `final` + provenance konsensus ditulis ke struktur kanonik; label individual diarsipkan immutable.

## 3. Batch & pengumpulan

- Batch dibagikan sebagai salinan file (tidak diedit bersama); satu batch = satu proyek (koheren, Protocol §2.1).
- Pengumpulan: annotator mengirim file hasil ke folder `submissions/<annotator>/<batch>/`; **koordinator mencatat waktu terima** sebagai `annotated_at` (metadata koleksi — annotator tidak mengisi timestamp).
- Setiap penerimaan diverifikasi: nama file, jumlah baris, SHA-256 dicatat koordinator.

## 4. Kepemilikan file & immutability

- File anotasi milik annotator; **tulis-sekali setelah dikumpulkan**. Koreksi = file/versi baru + alasan, bukan edit diam-diam.
- Label individual tidak pernah ditimpa oleh konsensus/adjudication (Protocol §6).

## 5. Penamaan, versi, backup, integritas

- `ANNOTATION_TEMPLATE_{A-XX}_{B-YY}_{R1|R2}.csv` — contoh: `ANNOTATION_TEMPLATE_A-01_CAL_R1.csv`.
- Setiap pengumpulan: koordinator menghitung SHA-256 dan menyimpannya di `submissions_manifest.csv` (file, annotator, round, batch, waktu terima, sha256).
- Backup: salinan di ≥2 lokasi (folder kerja + arsip); tidak pernah satu-satunya salinan.

## 6. Blinding

- Annotator tidak melihat: label/pekerjaan annotator lain, label historis, keluaran model, daftar konflik pasangannya.
- Daftar konflik Round 2 dibuat koordinator dan hanya berisi story_id + kriteria (tanpa label lawan).
- A-03 (adjudication) buta terhadap kedua label sampai selesai menilai.

## 7. Tanggung jawab QC koordinator

- Jalankan `ANNOTATION_QC_CHECKLIST.md` per batch yang dikumpulkan.
- Hitung agreement (Protocol §5.5) dan laporkan per kriteria/bahasa.
- Kumpulkan flag `POLA-BARU:`/`notes` untuk revisi guideline.
- Tidak pernah mengisi/mengubah label.

## 8. Penanganan pengecualian

| Situasi | Penanganan |
|---|---|
| Anotasi tidak lengkap | dikembalikan ke annotator pemilik untuk dilengkapi; QC tidak mengisi |
| Cerita ambigu/rusak | anotasi apa adanya (atau IE) + `notes`; koordinator memutuskan re-extract/keluar batch |
| Annotator sakit/tidak tersedia | batch ditunda; tidak ada penggantian annotator di tengah batch tanpa keputusan koordinator + catatan |
| Masalah teknis (encoding, file korup) | koordinator re-extract dari sumber; versi baru batch + catatan |
| Koreksi kesalahan setelah submit | file revisi baru + alasan; asli tetap tersimpan |

## 9. Progress tracking & status batch

Status batch (satu per batch, dikelola koordinator di `batch_status.csv`):

`NOT_STARTED → ASSIGNED → IN_PROGRESS → SUBMITTED → QC_PASSED → IN_R2 → ADJUDICATED → LOCKED`

Tracking minimal: batch, annotator, status, tanggal per perubahan, catatan. Cukup spreadsheet — tidak perlu alat baru.

## 10. Kerahasiaan & akses

- Identitas annotator dipetakan ke pseudonym A-XX; pemetaan disimpan terpisah, tidak masuk dataset.
- File label historis & model: akses terbatas ke koordinator; tidak dibagikan ke annotator.
- Hasil agreement/adjudication hanya dibagikan setelah ronde selesai dan tidak merujuk identitas.
- Data anotasi tidak dibagikan ke luar tim sebelum keputusan lisensi/publikasi.
