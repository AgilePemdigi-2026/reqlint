# ReqLint Backend API Workspace

FastAPI backend for ReqLint: two-stage audit pipeline (rule-based Stage 1 + evaluator choice +
Stage-2 advisory generation), JWT auth, SQLite/PostgreSQL via SQLAlchemy async.

## Quickstart

1. **Install Dependencies** (from the repository root; `scikit-learn==1.7.2` is pinned and
   required by the trained model bundle):
   ```bash
   pip install -r backend/requirements.txt
   pip install -r ai-engine/requirements-ai.txt
   python -m spacy download en_core_web_sm
   ```

2. **Run Local Dev Server** (from the repository root, so the ML bundle under `pm-docs/` resolves):
   ```bash
   uvicorn app.main:app --app-dir backend --reload --port 8000
   ```

3. **Interactive Swagger API Docs**: `http://localhost:8000/docs` (OpenAPI at
   `/api/v1/openapi.json`)

4. **Run Tests**:
   ```bash
   python -m pytest backend/tests -q     # 119 tests
   python run_bdd.py                     # pytest-bdd suite (34 scenarios)
   ```

Notes: startup creates the schema via `create_all` (no migration run needed locally); without
`JWT_SECRET`, `ENV=dev` generates an ephemeral secret — production requires an explicit secret.
Reference docs: [../docs/architecture/backend.md](../docs/architecture/backend.md) ·
[../docs/api/api-reference.md](../docs/api/api-reference.md) ·
[../docs/features/traditional-ml.md](../docs/features/traditional-ml.md)
