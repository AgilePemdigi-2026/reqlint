# Three-Evaluator Benchmark Specification (v1.0)

**Status:** Spesifikasi aktif (Task 04C). Menggantikan desain empat evaluator pada Task 03 §8 untuk **scope benchmark saat ini**.
**Prinsip:** tiga evaluator aktif, satu skema keluaran bersama, tiga label (`PASS` / `FAIL` / `INSUFFICIENT_EVIDENCE`), enam kriteria INVEST tetap.

---

## 1. Evaluator aktif

| | Evaluator A — Rule-Based | Evaluator B — Traditional ML | Evaluator C — LLM |
|---|---|---|---|
| Metode | Heuristik/rule deterministik (lexicon + pola bilingual) | TF-IDF + Logistic Regression **atau** Linear SVM | Prompt-based, keluaran terstruktur (JSON) |
| Cakupan | 6 kriteria independen | 6 kriteria, **One-vs-Rest** per kriteria | 6 kriteria independen |
| Label | PASS / FAIL / IE | PASS / FAIL / IE **hanya bila data anotasi mendukung** (lihat §1.1) | PASS / FAIL / IE eksplisit via prompt |
| Deterministik | Ya | Ya (seed tetap) | Tidak (sampling; temperature dicatat) |
| Bahasa | ID + EN (lexicon bilingual) | ID + EN (fitur tekstual) | ID + EN (prompt per bahasa cerita) |

### 1.1 Kebijakan tiga kelas untuk Evaluator B

- Klasifikasi tiga kelas (PASS/FAIL/IE) **hanya** jika data anotasi tervalidasi mendukung (jumlah contoh IE per kriteria memadai dan makna IE stabil).
- **Jangan asumsikan volume training yang diusulkan cukup.** Bila dukungan kelas tidak memadai:
  - jalankan sebagai **biner** (PASS vs FAIL) pada subset non-IE **dan laporkan sebagai eksploratori**;
  - dokumentasikan keterbatasan di hasil (jumlah contoh per kelas, ketiadaan IE, tidak dapat dibandingkan head-to-head penuh dgn A/C pada IE);
  - **dilarang** menggabungkan kelas diam-diam, membuat data sintetis, atau mengklaim generalisasi tanpa bukti.

### 1.2 Kebijakan IE untuk Evaluator A

Rule engine harus memiliki aturan IE eksplisit (bukan fallback PASS): kriteria diberi IE bila fitur penilaian tidak tersedia dari teks (contoh: tidak ada sinyal ukuran sama sekali untuk E). Aturan IE ditulis sebelum benchmark dan dibekukan bersama kode.

## 2. Skema keluaran bersama

Semua evaluator mengeluarkan struktur setara (JSON per story):

```json
{
  "story_id": "…",
  "evaluator": "A | B | C",
  "language": "en | id",
  "criteria": {
    "independent": {"label": "PASS | FAIL | INSUFFICIENT_EVIDENCE", "score": 0.0},
    "negotiable": {"label": "…", "score": 0.0},
    "valuable": {"label": "…", "score": 0.0},
    "estimable": {"label": "…", "score": 0.0},
    "small": {"label": "…", "score": 0.0},
    "testable": {"label": "…", "score": 0.0}
  },
  "latency_ms": 0,
  "output_valid": true,
  "error": null,
  "raw_output_ref": "pointer ke raw output untuk audit"
}
```

- `score` opsional (probabilitas/confidence bila evaluator menyediakan); `label` wajib.
- `output_valid` = false bila keluaran gagal di-parse/validasi → dihitung sebagai error, bukan sebagai label.
- Evaluator C wajib mencatat parameter prompt/model/temperature yang dipakai (reproducibility).

## 3. Evaluator yang dikeluarkan: Pretrained Encoder

- **Status terverifikasi:** tidak ada implementasi evaluator encoder di repo. Yang ada hanya: (a) penyebutan desain di Task 03 §8, (b) flag opsional `USE_E5_EMBEDDING = False` di skrip `coba`/`coba 2.py` yang **tidak pernah diaktifkan**, (c) referensi `sentence-transformers` yang tidak tercantum di requirements. Tidak ada model, checkpoint, hasil, atau prosedur tuning encoder.
- **Keputusan:** dikeluarkan dari scope benchmark aktif; menjadi **future work**. Tidak ada kode/artefak yang dihapus.
- **Rekomendasi:** arsipkan status ini sebagai "design mention only" (dokumen ini + changelog); tidak perlu tindakan lebih lanjut. Encoder tidak boleh disajikan sebagai evaluator aktif di dokumen benchmark/laporan.

## 4. Shared recommendation engine — di luar benchmark

Engine rekomendasi LLM (Stage-2 rewrite, `nlp_stage2.py` → `ai_rewrite`) **bukan evaluator keempat**. Ia menghasilkan saran perbaikan cerita, bukan klasifikasi INVEST. Penilaian kualitas rekomendasinya **ditunda** (deferred) dan tidak termasuk metrik benchmark klasifikasi mana pun. Perbedaan ini dicatat di semua laporan benchmark.

## 5. Metrik benchmark

**Primer** (per evaluator, per kriteria, per bahasa):
- Macro F1 tiga kelas **bila dukungan kelas memungkinkan** (semua kelas terwakili di test);
- Precision, recall, F1 per label;
- Confusion matrix 3×3.

**Sekunder:** micro F1; exact match (6 kriteria sekaligus); perbandingan deskriptif EN vs ID; error analysis (kutipan kasus salah).

**Operasional:** latency rata-rata; latency P95; biaya per 1.000 story (khusus evaluator C: token/harga); tingkat keluaran valid; tingkat error.

**Statistik:** bootstrap CI **boleh** dipertimbangkan dengan caveat eksplisit (resample dgn mempertahankan pasangan terjemahan/proyek); pengujian signifikansi formal dan perbandingan berpasangan kompleks **ditunda** sampai ukuran test final diketahui — jangan menarik kesimpulan statistik berlebihan dari test kecil.

**Aturan pelaporan:** bila Traditional ML kekurangan dukungan kelas → status **eksploratori**, dicatat di tabel hasil; tidak ada collapsing kelas; tidak ada klaim robust generalization tanpa bukti.

## 6. Kondisi evaluasi

1. Test set = test manifest bebas (Task 03 §6, roadmap S9) — **dibekukan sebelum** evaluasi model.
2. Project-level split; pasangan EN–ID satu split; tidak ada story kalibrasi atau historis di test.
3. Blinding: evaluator tidak pernah dilatih/di-tuning menggunakan test; annotator tidak melihat keluaran evaluator.
4. Evaluasi final test = satu run terdokumentasi per evaluator; rerun hanya bila bug infrastruktur (dicatat).
5. Semua evaluator menilai **teks yang sama** (batch test identik) dalam **kedua bahasa**.

## 7. Batasan yang diakui

- Ukuran test kecil (±40 story pada rencana sementara) → CI lebar; hasil dilaporkan dgn CI/caveat, bukan klaim kemenangan.
- IE alami kemungkinan jarang di beberapa kriteria → metrik IE bisa tidak stabil antar-evaluator; laporkan tingkat IE per evaluator.
- Evaluator B dapat jatuh ke status eksploratori (§1.1) — perbandingan tiga evaluator penuh tidak dijamin.
