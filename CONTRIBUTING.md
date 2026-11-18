# Guidelines Kontribusi & Workflow Kolaborasi Team (4 Orang)

Dokumen ini berisi panduan kolaborasi pengembangan **ReqLint** untuk 4 anggota tim.

---

## 👥 Pembagian Workspace & Peran (Role Allocation)

| Anggota & Peran | Direktori Workspace | Tanggung Jawab Utama |
|---|---|---|
| **Member 1: PM & Architect** | `pm-docs/` | Desain arsitektur, rubrik audit ISO 29148 & INVEST, dokumentasi PM. |
| **Member 2: AI / NLP Engineer** | `ai-engine/` | Rule-matcher (ID/EN), integrasi SLM (Ollama/Llama-3), & benchmark sintaksis. |
| **Member 3: Backend Engineer** | `backend/` | FastAPI REST API, SQLite/PostgreSQL storage, & per-sentence audit endpoints. |
| **Member 4: Frontend + QA Engineer** | `frontend-qa/` | UI Next.js (Tailwind + Lucide icons), Cypress E2E tests, & PDF/JSON export. |

---

## 🌿 Git Branching Strategy

Jangan push langsung ke branch `main`. Selalu gunakan feature branch sesuai dengan peran/modul yang dikerjakan:

- **Member 1 (PM/Architect)**: `pm/<nama-fitur>` (contoh: `pm/update-rubrics`)
- **Member 2 (AI/NLP)**: `ai/<nama-fitur>` (contoh: `ai/indonesian-flaw-matcher`)
- **Member 3 (Backend)**: `backend/<nama-fitur>` (contoh: `backend/audit-endpoint`)
- **Member 4 (Frontend/QA)**: `frontend/<nama-fitur>` (contoh: `frontend/smell-list-ui`)

---

## 🚀 Alur Kerja Pembuatan Fitur (Feature Development Workflow)

1. **Pull Update Terbaru dari `main`**:
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Buat Branch Baru**:
   ```bash
   git checkout -b <role>/<nama-fitur>
   # contoh: git checkout -b backend/add-pdf-exporter
   ```

3. **Kerjakan Perubahan & Commit**:
   Gunakan format **Conventional Commits**:
   - `feat: ...` (Fitur baru)
   - `fix: ...` (Perbaikan bug)
   - `docs: ...` (Perubahan dokumentasi)
   - `test: ...` (Penambahan/perbaikan pengujian)
   - `refactor: ...` (Refactoring kode tanpa mengubah fitur)

   Contoh:
   ```bash
   git add .
   git commit -m "feat(backend): add PDF summary exporter endpoint"
   ```

4. **Push Branch ke Remote GitHub**:
   ```bash
   git push -u origin <role>/<nama-fitur>
   ```

5. **Buat Pull Request (PR) di GitHub**:
   - Buka GitHub repository kanonik `https://github.com/AgilePemdigi-2026/reqlint`
     (URL lama `farhanAkbar91/reqlint` hanya redirect).
   - Buat PR dari branch Anda ke branch `main`.
   - Isi template PR dengan lengkap.
   - Tag anggota tim penanggung jawab untuk peninjauan (Code Review) — branch `main` membutuhkan
     minimal satu approval dari reviewer dengan akses write.
   - Setelah disetujui (Approved) & lolos CI, lakukan **Merge commit** (konvensi riwayat repositori:
     `Merge pull request #NN …`).

---

## 💻 Menjalankan Lingkungan Lokal dengan Docker

Sebelum membuat PR, pastikan aplikasi dapat berjalan tanpa masalah:

```bash
# Jalankan stack (Frontend + Backend + PostgreSQL + Redis; ai-engine bukan service runtime)
docker-compose up --build
```

- **Frontend**: `http://localhost:3000`
- **Backend API Docs**: `http://localhost:8000/docs`

> Catatan: `ai-engine/` adalah workbench Python (korpus & pipeline pelatihan), bukan service
> runtime — backend tidak mengimpornya. Panduan lengkap:
> [docs/getting-started/installation.md](docs/getting-started/installation.md) ·
> [docs/deployment/docker.md](docs/deployment/docker.md).
