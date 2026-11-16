# Annotator Handbook — ReqLint INVEST

**Untuk:** Annotator A-01 dan A-02 (dua orang, independen).
**Baca sebelum bekerja:** `INVEST_ANNOTATION_GUIDELINE.md` (definisi & aturan), `ANNOTATION_PROTOCOL.md` (alur ronde).
**Alat:** `ANNOTATION_TEMPLATE.csv` (Excel / Google Sheets) + teks User Story dari batch yang ditugaskan.

---

## 1. Tujuan anotasi

Anda menilai **kualitas intrinsik tiap User Story** terhadap enam kriteria INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable) **hanya berdasarkan teks cerita**, sehingga dataset benchmark yang adil dapat dibangun. Penilaian Anda adalah **data penelitian** — bukan review produk. Kualitas, konsistensi, dan independensi penilaian Anda lebih penting daripada kecepatan.

Yang TIDAK menjadi tujuan Anda: memperbaiki cerita, menilai "keren/tidaknya" fitur, menebak intent bisnis di luar teks, atau menyetujui/membantah penilaian orang lain.

## 2. Aturan independensi (WAJIB)

1. **Round 1: bekerja 100% mandiri.** Dilarang berdiskusi, bertanya, atau melihat hasil Annotator lain — termasuk lewat grup, komentar, atau file bersama. Pertanyaan hanya ke koordinator, dan jawaban koordinator yang bersifat substansi (bukan prosedur) wajib dicatat dan diteruskan identik ke annotator lain.
2. **Dilarang melihat** label historis apa pun (Family B, korpus 1000, model) — file-file itu tidak berada di folder anotasi dan tidak boleh dicari.
3. **Dilarang menjalankan atau melihat output** alat evaluator/model ReqLint untuk cerita yang dianotasi.
4. Round 2 hanya dimulai setelah Round 1 sepenuhnya selesai dan dikumpulkan; daftar kasus yang direview diberikan koordinator.
5. Simpan pekerjaan Anda hanya di file milik Anda (`ANNOTATION_TEMPLATE_A-01.csv` / `A-02`).

## 3. Langkah kerja (per cerita)

1. **Buka file batch Anda** (salinan `ANNOTATION_TEMPLATE.csv` yang sudah berisi daftar cerita). Jangan mengubah kolom identitas (`story_id` … `original_text`). Isi `annotation_round` dengan `R1` (Round 1) atau `R2` (Round 2) sesuai fase yang ditetapkan koordinator saat batch dibagikan.
2. **Baca cerita 2× secara utuh.** Baca sebagai "pemilik kebutuhan" pada Round 1 (apakah saya paham apa yang diminta dan untuk apa?) lalu sebagai "penguji" (apakah setiap klaim dapat diverifikasi/dikritik dari teks?).
3. **Nilai enam kriteria satu per satu**, urutan bebas namun konsisten (disarankan urutan kolom: I, N, V, E, S, T). Untuk setiap kriteria:
   - Tentukan apakah ada **bukti positif pemenuhan**, **bukti positif pelanggaran**, atau **informasi tak cukup** (lihat Guideline §0.4).
   - Pilih tepat satu label: `PASS` / `FAIL` / `INSUFFICIENT_EVIDENCE`.
   - Isi `*_evidence`: rentang karakter `start-end` (1-based, inklusif) dari `original_text`; beberapa bukti dipisah `;`. Untuk FAIL berbasis ketiadaan (mis. `MISSING_BENEFIT`), tulis rentang seluruh teks.
   - Isi `*_rationale`: **kode rationale dari daftar tertutup** di Guideline (mis. `MISSING_BENEFIT`, `PRESCRIPTIVE_UI`), boleh diikuti `: ` dan kalimat pendek. Wajib untuk FAIL/IE; disarankan untuk PASS.
4. **Isi keenam kolom `*_confidence`**: `LOW` / `MEDIUM` / `HIGH` — keyakinan Anda **per kriteria** (bukan satu nilai untuk seluruh cerita).
5. **Isi `notes`** hanya untuk hal yang perlu diketahui koordinator/QC (keraguan pola baru, cerita rusak/duplikat, teks terpotong). Kosongkan bila tidak ada.
6. **Jangan mengedit teks cerita.** Jika teks tampak rusak/terpotong, tetap anotasi apa adanya (atau IE bila tidak mungkin) dan catat di `notes`.
7. Lanjut cerita berikutnya. Satu sesi dianjurkan ≤ 15–20 cerita agar konsentrasi terjaga; beristirahat lebih baik daripada menurunkan konsistensi.

## 4. Cara membaca User Story

- **Identifikasi tiga bagian** (jika ada): peran ("Sebagai X" / "As an X"), aksi ("saya ingin …" / "I want to …"), manfaat ("sehingga …" / "so that …"). Ketiga-tiganya **sering tidak lengkap** — itu normal di korpus nyata dan justru yang dinilai.
- **Tandai secara mental** pola yang relevan per kriteria: ketergantungan (I), detail implementasi (N), manfaat (V), kuantifier kabur/objek konkret (E), aksi majemuk vs tunggal (S), hasil terukur vs subjektif (T).
- **Baca kata sambung dan kata rujukan dengan saksama**: "dan juga", "serta", "sekalian" (S); "setelah", "tersebut", "hanya setelah" (I); "cepat/mudah/various/dll" (E/T); "tombol/SQL/font/backend" (N).
- Jika teks mengandung istilah domain yang tidak Anda pahami (mis. "OAI-PMH", "MARCXML") — itu **bukan** alasan IE otomatis. Nilai dari struktur kalimat: apakah hasilnya dapat diverifikasi, apakah lingkupnya terbatas. IE hanya bila penilaian memang butuh asumsi.

## 5. Cara memberi label (contoh berpikir)

Cerita: *"Sebagai user, saya ingin proses login berjalan dengan cepat dan mudah."*

- **T** → "cepat dan mudah" = klaim kualitatif tanpa ukuran → `FAIL`, evidence = rentang "cepat dan mudah", rationale `SUBJECTIVE_ADJECTIVE: tidak ada batasan waktu/langkah`.
- **E** → lingkup login sendiri cukup konkret, tetapi "cepat dan mudah" tidak menambah ukuran; tidak ada kuantifier terbuka → `PASS` (`CONCRETE_OBJECTS`) — atau `FAIL` bila Anda menilai "mudah" membuka cakupan desain tak terbatas; pilih dan konsisten, catat di notes bila ragu.
- **V** → tidak ada manfaat yang dinyatakan (untuk siapa, untuk apa?) → `FAIL` `MISSING_BENEFIT`, evidence = seluruh teks.
- **I** → berdiri sendiri → `PASS`.
- **N** → tidak memnormakan implementasi → `PASS`.
- **S** → satu kapabilitas → `PASS`.

Perhatikan: contoh ini **ilustratif**, bukan kunci jawaban. Penilaian Anda harus mengikuti Guideline.

## 6. Cara menulis evidence & rationale

- **Evidence** hanya berisi rentang/rentang karakter, **1-based inklusif** terhadap `original_text`. Contoh benar: `18-46`, `1-79`, `18-46;77-103`. Contoh salah: `kata "cepat"`, `seluruh kalimat kedua` (tidak dapat diverifikasi otomatis). FAIL berbasis ketiadaan → rentang seluruh teks `1-N` (N = panjang teks).
- **Rationale** = kode tertutup, lalu `: ` dan penjelasan maksimal satu kalimat. Contoh: `MISSING_BENEFIT: tidak ada klausa manfaat dan manfaat tidak tersurat dari aksi`; `PRESCRIPTIVE_UI: ukuran dan warna tombol ditentukan`.
- Kode untuk FAIL/IE **wajib** persis dari daftar Guideline §1–§6. Bila pola Anda tidak ada di daftar, gunakan kode terdekat dan jelaskan di kalimat, lalu catat di `notes` sebagai "pola baru: …" — pola baru akan ditinjau koordinator untuk revisi guideline.

## 7. Menangani kasus ambigu

1. Terapkan tie-breaker Guideline §9 (FAIL bila pola bisa dikutip; IE bila butuh asumsi; PASS butuh bukti positif).
2. Catat keraguan di `notes` (satu kalimat). Jangan menunggu/jawab sendiri lewat diskusi — Round 2 yang akan mengangkat kasus Anda.
3. Jika Anda menemukan **kelas ambiguitas baru** yang muncul berulang, tandai `notes` dengan `POLA-BARU:` — koordinator mengumpulkan ini untuk revisi guideline antara ronde kalibrasi.
4. **Jangan mengubah label lama** setelah sesi berakhir untuk "memperbaiki" — bila ada koreksi, buat di `notes` dengan alasan; koordinator yang memutuskan mekanisme koreksinya.

## 8. Hal yang dilarang (ringkas)

- Diskusi antar-annotator saat Round 1; melihat label/pekerjaan annotator lain.
- Melihat label historis atau output model/aplikasi ReqLint.
- Mengosongkan kolom label atau memakai nilai di luar `PASS`/`FAIL`/`INSUFFICIENT_EVIDENCE` (termasuk `?`, `-`, `OK`, `1/0`).
- Mengedit `story_id`, `original_text`, atau kolom identitas lain.
- Mengarang informasi (manfaat, ukuran, konteks proyek) yang tidak ada di teks.
- Menganotasi cerita di luar batch yang ditugaskan.

## 9. Kalau macet

- Lupa kode rationale → kembali ke tabel kriteria di Guideline.
- Cerita duplikat dalam batch → anotasi keduanya secara independen, catat di `notes` (`DUPLIKAT-DENGAN: <story_id lain>`).
- Cerita dalam bahasa campur → nilai berdasarkan isi yang dapat dipahami; catat di `notes` (`BAHASA-CAMPUR`).
- Merasa batch terlalu berat/lelah → berhenti sesi; jangan memaksa (pilot menunjukkan kelelahan menurunkan kualitas penilaian).
