# 📋 Pedoman Anotasi Ilmiah INVEST & Pengadaan Korpus Data

Dokumen standar operasional pelabelan data, kriteria evaluasi INVEST, dan metodologi pengadaan korpus 1.000 *Agile User Story*.

---

## 1. Landasan Teoretis & Kriteria INVEST

Evaluasi kualitas *User Story* didasarkan pada kerangka kerja **INVEST** (*Bill Wake, 2003*) dan template **Connextra** (*Rachel Davies, 2001*):
$$\text{Sebagai } \langle \text{peran} \rangle, \text{ saya ingin } \langle \text{aksi} \rangle, \text{ sehingga } \langle \text{manfaat} \rangle$$

### 1.1 Matriks Kriteria Operasional

| Kriteria | Definisi Operasional | Cacat / Pelanggaran Tipikal | Tindakan Anotasi ($y=0$) |
|:---:|---|---|---|
| **I** (*Independent*) | Bebas dari ketergantungan urutan pengerjaan tiket teknis lain | Menyebutkan dependensi eksplisit (*"setelah modul X selesai"*) | Tandai $y_I = 0$ |
| **N** (*Negotiable*) | Menyatakan maksud esensial tanpa memaksakan rincian implementasi | Mengunci detail teknis kaku (*"menggunakan modal pop-up Tailwind CSS dan fungsi MySQL SELECT..."*) | Tandai $y_N = 0$ |
| **V** (*Valuable*) | Memberikan nilai bisnis yang jelas bagi persona pengguna | Klausa manfaat tidak ada (*missing benefit*) atau manfaat tidak masuk akal (*"sehingga saya bisa melihat layar"*) | Tandai $y_V = 0$ |
| **E** (*Estimable*) | Ruang lingkup cukup jelas untuk diperkirakan bobot ceritanya | Menggunakan kuantitas kabur (*"beberapa data"*, *"banyak dokumen"*, *"dan lain-lain"*) | Tandai $y_E = 0$ |
| **S** (*Small*) | Ukuran cerita dapat diselesaikan dalam 1 iterasi sprint | Mengandung konjungsi majemuk (*"dan juga... serta sekaligus..."*) menandakan cerita setingkat *Epic* | Tandai $y_S = 0$ |
| **T** (*Testable*) | Kriteria penerimaan dapat diverifikasi secara objektif | Mengandung kata sifat subjektif tak terukur (*"cepat"*, *"mudah"*, *"user-friendly"*, *"aman"*) atau kata direktif lemah (*"sebaiknya"*, *"bisa"*) | Tandai $y_T = 0$ |

---

## 2. Protokol Pelabelan & Integritas Ilmiah

### 2.1 Format Vektor Label
Setiap *User Story* dilabeli dengan vektor biner 6 dimensi:
$$[y_I, y_N, y_V, y_E, y_S, y_T] \in \{0, 1\}^6$$
* **Nilai 1**: Memenuhi kriteria dengan baik.
* **Nilai 0**: Terindikasi memiliki cacat kualitas pada kriteria terkait.
* **Opsi RAGU**: Jika anotator mengalami ambiguitas penafsiran, teks dimasukkan ke sesi rekonsiliasi konsensus.

### 2.2 Reliabilitas Antar-Penilai (Inter-Rater Reliability)
Untuk memastikan objektivitas pelabelan dan mencegah bias individu:
1. **Blind Annotation**: Dua anotator memberi label secara independen tanpa saling berkomunikasi.
2. **Kalkulasi Metrik**:
   * **Cohen's Kappa ($\kappa$)**: Mengukur kesepakatan penilai di luar peluang acak.
   * **PABAK (*Prevalence-Adjusted Bias-Adjusted Kappa*)**: Menangani paradoks Kappa pada distribusi kelas yang sangat timpang.
   $$\text{PABAK} = 2P_o - 1$$
3. **Konsensus**: Seluruh perbedaan label antara Anotator A dan Anotator B diselesaikan melalui diskusi bersama untuk menghasilkan label *ground truth* final.

---

## 3. Metodologi Pengadaan Korpus 1.000 User Story

Korpus data dirancang untuk mencakup 1.000 cerita berimbang dwibahasa (500 Bahasa Indonesia, 500 Bahasa Inggris).

### 3.1 Sumber Data
1. **Bahasa Inggris (500 Stories)**:
   * Mengadopsi domain publik dari repositori **Fabiano Dalpiaz et al.** (22 domain perangkat lunak: *OpenGov, FAA Aviation, CMS, SmartHome, Healthcare, Financial Systems, Logistics*).
2. **Bahasa Indonesia (500 Stories)**:
   * Dikompilasi dari proyek sistem informasi lokal dan studi kasus PPL (*SIAKAD/KRS, Perpustakaan Digital, POS Kasir UMKM, Ekspedisi Kargo, HRIS, Klinik Kesehatan*).

### 3.2 Mesin Perturbasi Terkontrol (*Controlled Perturbation Engine*)
Untuk memecahkan masalah kelangkaan contoh negatif (*imbalance class*), modul `perturbation_engine.py` menginjeksi kecacatan tunggal yang ortogonal pada cerita alami:
* **Injeksi Cacat T ($y_T = 0$)**: Mengganti klausul aksi menjadi kalimat subjektif (*"dengan sangat cepat dan mudah"*).
* **Injeksi Cacat S ($y_S = 0$)**: Menggabungkan dua cerita independen dengan konjungsi majemuk (*"dan juga... serta sekaligus menyinkronkan seluruh database"*).
* **Injeksi Cacat V ($y_V = 0$)**: Memotong klausa manfaat (*"sehingga..."*).
* **Injeksi Cacat E ($y_E = 0$)**: Menambahkan kuantifier kabur (*"beberapa item dan lain-lain"*).

### 3.3 Aturan Emas Evaluasi (Test Set Isolation)
* **Train Set (750 stories / 75%)**: Berisi kombinasi Natural + Perturbed + Synthetic.
* **Validation Set (100 stories / 10%)**: **100% Cerita Alami (Natural Stories)**.
* **Test Set (150 stories / 15%)**: **100% Cerita Alami (Natural Stories)** tanpa sampel sintetis atau perturbasi. Evaluasi model dengan demikian mencerminkan performa nyata terhadap teks manusia.
