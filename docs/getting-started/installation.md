# Installation

Verified against the repository at commit `bfe72aa`. Commands are written for Git Bash /
Linux / macOS; on Windows adjust path separators as noted.

## Prerequisites

| Tool | Version | Used for |
|---|---|---|
| Python | 3.11+ (tested on 3.14 locally, CI pins 3.10 for syntax checks) | backend, ai-engine workbench, BDD suites |
| Node.js | 18+ | frontend build, frontend tests |
| Docker | 24+ (optional) | containerized runs / deployment |

The frontend uses `npm ci --legacy-peer-deps` (a pinned `vitest@5` peer-dependency conflict makes a
plain `npm ci` fail with `ERESOLVE` — this matches CI, see `.github/workflows/ci.yml`).

## 1. Get the repository

```bash
git clone https://github.com/AgilePemdigi-2026/reqlint.git
cd reqlint
```

`AgilePemdigi-2026/reqlint` is the canonical repository (the older `farhanAkbar91/reqlint` URL
redirects there).

## 2. Backend (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

pip install -r backend/requirements.txt
pip install -r ai-engine/requirements-ai.txt
python -m spacy download en_core_web_sm
```

Notes:

- `backend/requirements.txt` pins `scikit-learn==1.7.2` — this exact version is required to
  unpickle the trained INVEST model bundle (see [../features/traditional-ml.md](../features/traditional-ml.md)).
- `ai-engine/requirements-ai.txt` adds spaCy, `langdetect`, `langchain-groq`, and `pytest`. Only
  **spaCy** is imported by backend runtime code; the other entries serve the ai-engine workbench.
- Indonesian spaCy model (`id_core_news_sm`, installed by `ai-engine/setup_models.py` for
  workbench experiments) is **not** used by the backend; Indonesian analysis relies on the
  lexicon/regex rules in `backend/app/lexicon/`.

## 3. Frontend (Next.js)

```bash
cd frontend-qa
npm ci --legacy-peer-deps
```

## 4. (Optional) ai-engine workbench

The `ai-engine/` directory is a Python workbench (corpus building, training pipelines,
experiments) — it is **not** a runtime service and the backend never imports it. To use it:

```bash
pip install -r ai-engine/requirements-ai.txt
python ai-engine/setup_models.py     # downloads en_core_web_sm and id_core_news_sm
```

## 5. Verify the installation

```bash
# Terminal 1 — backend (from the repository root)
uvicorn app.main:app --app-dir backend --port 8000
curl http://localhost:8000/api/v1/health
# → {"status":"success","message":"OK","data":{"db":"up",...}}

# Terminal 2 — frontend
cd frontend-qa && npm run dev
# → http://localhost:3000 (landing page)
```

On startup the backend prints one of these security notices, depending on configuration
(see [configuration.md](configuration.md#security-guard)):

- `ENV=dev` without `JWT_SECRET` → an ephemeral secret is generated (development only).
- Any other `ENV` without `JWT_SECRET` → the process exits with a `RuntimeError`.

Next step: [local-development.md](local-development.md).
