# Historical Dataset Integration Spec — Family B → Canonical Dataset (v1.0-draft)

**Status:** Spesifikasi (Task 04). Mengikuti skema kanonik Task 03 §3 dan hasil forensik Task 04B. Tidak dieksekusi terhadap data apa pun.
**Prinsip:** label historis biner **dipertahankan apa adanya**, **selalu dapat dibedakan** dari anotasi baru tiga-kelas, dan **tidak pernah** bocor ke test set.

---

## 1. Sumber yang diintegrasikan

| Sumber | Cakupan | Artefak bukti |
|---|---|---|
| Birth state 221 baris berlabel (108 EN + 113 ID) | `dataset-{eng,indo}-label-final/*.csv` @ `236ea51` | blob hash per file (tercantum di arsip `pre_writeback_236ea51/MANIFEST.json`) |
| 85 baris yang selamat di HEAD (file tak tersentuh writeback) | subset birth | blob identik |
| 5 baris badcamp-EN earlier-round — **rekord EN tambahan, bukan tambahan hitungan 221**: story `badcamp_001`–`005` sudah tercakup di 221 via pasangan ID-nya yang berlabel di `dataset-indo-label-final/badcamp.csv` @ `236ea51` (verifikasi terukur, lihat Assessment §3.1) | `dataset-english-label/badcamp-english.csv` @ `236ea51` | blob `974e38e437` |
| **TIDAK diintegrasikan:** ~738 baris hasil model-assisted (`e23701c`), label model lain, Family A | — | kelas C Task 04B — quarantined |

## 2. Representasi di skema kanonik

Setiap baris historis yang lolos seleksi direpresentasikan sebagai **record kanonik dengan blok historis terpisah** — bukan pengganti blok anotasi baru:

```json
{
  "story_id": "RQ-g19-alfred-en-0007",
  "source_id": "g19_alfred_007",
  "language": "en",
  "original_text": "…",
  "provenance": {
    "annotation_source": "historical_236ea51",
    "source_commit": "236ea51806050c39f500c941cc8144b88120f491",
    "source_blob_sha1": "c5d73e6941…",
    "provenance_class": "A | A' | A'' | B",
    "provenance_notes": "single unnamed annotator; annotator_a = all-pass aggregate; no metadata"
  },
  "historical_labels": {
    "scheme": "binary_0_1",
    "y_I": 1, "y_N": 1, "y_V": 1, "y_E": 0, "y_S": 1, "y_T": 1,
    "labels_as_committed": true,
    "snapshot": "pre_writeback_236ea51"
  },
  "annotations": [],              // KOSONG — historis bukan anotasi baru
  "final": null,                  // TIDAK diisi dari label historis kecuali lolos OD-7 (lihat §4)
  "annotation_status": "historical_candidate",
  "dataset_split": "unassigned"   // historis TIDAK PERNAH test (§5)
}
```

**Aturan pembedaan (mutlak):**
1. Label historis **tidak pernah** ditulis ke `annotations[]` atau `final` — selalu di blok `historical_labels` dengan `scheme: binary_0_1`.
2. Anotasi baru (`PASS/FAIL/INSUFFICIENT_EVIDENCE`) hanya pernah ada di `annotations[]`/`final`.
3. Kedua skema **tidak pernah dicampur** dalam satu kolom; konsumen data dapat memfilter berdasar `annotation_source` / `scheme`.
4. `INSUFFICIENT_EVIDENCE` **tidak ada** dalam data historis — kehadirannya di record mana pun menandakan record itu bukan historis.
5. **Pra-syarat pemetaan `0 → FAIL`: makna `0` harus terkonfirmasi lebih dulu** — kombinasi konfirmasi annotator asli (Validation Plan Fase V1) dan kesepakatan dengan anotasi baru (Fase V4). Bila `0` ternyata mencakup kasus yang menurut skema baru adalah `INSUFFICIENT_EVIDENCE` (atau tidak dapat dipastikan), **pemetaan `0 → FAIL` tidak boleh dipakai untuk training**: baris terkait dikeluarkan dari mapping, atau seluruh pemetaan ditunda sampai makna `0` terkonfirmasi.

## 3. Kelayakan seleksi baris historis

Baris masuk arsip kanonik bila memenuhi kelas Task 04B **dan** gate di bawah. **Kelas A' (nilai aslinya ditimpa writeback) TIDAK otomatis gugur** — nilai aslinya dapat dipulihkan dari blob arsip `236ea51` (`pre_writeback_236ea51/`), dan itulah nilai yang dipakai untuk `historical_labels`; nilai HEAD-nya (hasil writeback) tidak pernah dipakai. Kelas B hanya eligible setelah konfirmasi annotator (G2) — kelas C tidak pernah eligible.

| Gate | Sifat | Sumber |
|---|---|---|
| G1 Baris ada di blob `236ea51` (arsip terverifikasi) | **Wajib** | Task 04B / arsip |
| G2 Konfirmasi annotator asli diterima | **Wajib** | Validation Plan Fase V1 |
| G3 Lolos pemeriksaan distribusi/pola mencurigakan | **Wajib** | Validation Plan Fase V2–V3 |
| G4 Tercakup sampel perbandingan baru dengan kesesuaian memadai | **Opsional, bukti pendukung saja** — kesepakatan dengan anotasi baru adalah semantic concordance, bukan bukti provenance, dan tidak pernah menjadi dasar tunggal sertifikasi kelas | Validation Plan Fase V4 |

Baris gagal gate tetap **tersimpan** dengan `integration_status = excluded_<reason>` — tidak pernah dihapus diam-diam.

## 4. Kelayakan penggunaan (training vs test vs calibration)

| Penggunaan | Baris historis tervalidasi (A/A'' + gate penuh) | Baris historis belum tervalidasi (B) | Anotasi baru 3-kelas |
|---|---|---|---|
| **Train set** | ✅ **BOLEH** setelah OD-7 disetujui **dan makna `0` terkonfirmasi** (aturan 4 di bawah), dengan tag `historical_binary` (mapping 1→PASS, 0→FAIL hanya saat konsumsi model, bukan di data) | ❌ | ✅ |
| **Val set** | ⚠️ dikecualikan dari val awal; boleh ditambahkan nanti bila OD-7 + G1–G3 penuh (G4 pendukung) dan tidak bentrok near-dup dgn test | ❌ | ✅ |
| **Test set (frozen)** | ❌ **TIDAK PERNAH** — test wajib 100% anotasi baru dua-annotator | ❌ | ✅ |
| **Calibration/reference** | ❌ (referensi anotasi = pilot-30; historis bukan acuan proses) | ❌ | ✅ (pilot-30 & hasil kalibrasi) |
| **Analisis/pembanding pasca-hoc** | ✅ selalu (overlay read-only) | ✅ | ✅ |

Alasan test-eligibility nol: (a) skema biner tak bisa menyatakan IE; (b) provenance tunggal tanpa dua annotator; (c) risiko near-dup dgn data train historis; (d) test sudah dibekukan pada anotasi baru (Task 03 §6).

## 5. Pencegahan kebocoran (leakage) antara historis ↔ kalibrasi ↔ test

1. **Partisi fisik:** data historis tinggal di file arsip + quarantine (`family_b_labels_quarantined.jsonl` per Task 03); tidak pernah digabung ke file batch anotasi.
2. **Batas peran:** annotator baru tidak pernah melihat data historis (Handbook §2; Protocol §2); QC tidak mengisi label.
3. **Project-level split (Task 03 §6.1):** proyek yang dialokasikan sebagai **test** tidak boleh menyumbang baris historis apa pun ke train/val — penyaringannya berbasis `project_id` (dan `split_group_key` = `translation_pair_id` else `story_id`), **bukan** hanya near-dup filtering. Near-duplicate checking tetap berlaku sebagai **pemeriksaan tambahan** di atas batas proyek, bukan penggantinya.
4. **Near-dup gate antar-partisi:** sebelum test freeze, jalankan pembanding near-duplicate antara (a) semua baris test baru dan (b) semua baris historis terintegrasi — pasangan ≥ ambang → salah satu dikeluarkan dari test (pilih yang baru) dan dicatat.
5. **Pair-coherence:** pasangan EN–ID historis berlabel sama (100% sync) tidak dihitung dua sampel; pasangan diberi `translation_pair_id` dan dianggap satu unit untuk split.
6. **Model training hygiene:** model yang dilatih dengan data historis **tidak boleh** digunakan untuk memilih/mengukur test; laporan benchmark memisahkan "model trained incl. historical" vs "model trained new-only".
7. **Audit jejak:** setiap keputusan integrasi baris (retained/excluded/superseded) dicatat dengan alasan + hash bukti.

**Eksperimen pembanding `new-only` vs `new + historical` dipertahankan**, tetapi hanya dijalankan bila kedua syarat terpenuhi: (a) baris historis yang dipakai **lolos gate G1–G3**, dan (b) **semantik label kompatibel** — makna `0` terkonfirmasi (aturan 5 di §4). Tanpa itu, eksperimen ditunda.

## 6. Alur integrasi (stages, sesudah Validation Plan lulus)

1. **S-I1 Seleksi:** terapkan gate G1–G4 per baris → daftar `retained` / `excluded`.
2. **S-I2 Konversi representasi:** bangun record kanonik (§2) untuk baris retained; `historical_labels` verbatim dari arsip (bukan dari HEAD).
3. **S-I3 Validasi skema:** lint constraint (blok terpisah, tidak ada IE di historis, provenance lengkap, pair coherence).
4. **S-I4 Integrasi split:** retained masuk train (post OD-7 **+ konfirmasi makna `0`**); project-level split + `split_group_key` gate antar-partisi (Task 03 §6.1); near-dup gate sebagai pemeriksaan tambahan; test tetap bebas historis.
5. **S-I5 Pencatatan:** update `dataset_version` changelog; semua keputusan baris teraudit.

## 7. Risiko yang diakui

1. Label historis bersifat biner — model yang dilatih darinya tidak belajar IE; laporkan keterbatasan ini di benchmark.
2. Distribusi historis timpang (y_V 98.2% positif) — kombinasi dgn data baru harus diukur ulang, bukan diasumsikan seimbang.
3. 100% sinkron EN↔ID berarti data historis **tidak menambah** informasi antarbahasa yang independen.
4. Jika annotator asli tidak memberi konfirmasi (Fase V1 gagal), seluruh 221 baris tetap kelas B — jatuhnya ke "pembanding pasca-hoc", dan benchmark sepenuhnya bergantung pada anotasi baru.
