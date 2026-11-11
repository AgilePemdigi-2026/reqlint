FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
# curl is required by Coolify's container health check (curl -f http://localhost:8000/api/v1/health)
RUN apt-get update && apt-get install -y gcc g++ git curl && rm -rf /var/lib/apt/lists/*

# Copy backend & ai-engine dependencies
COPY backend/requirements.txt /app/requirements.txt
COPY ai-engine/requirements-ai.txt /app/requirements-ai.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-ai.txt
RUN python -m spacy download en_core_web_sm

# Copy source code
COPY backend /app/backend
COPY ai-engine /app/ai-engine

WORKDIR /app/backend

# Pre-create writable directories:
#   ./storage/cache        -> PDF upload temp cache (TEMP_DIR)
#   ./data                 -> optional persistent SQLite (mount a volume here and
#                             set DATABASE_URL=sqlite+aiosqlite:///./data/reqlint.db)
RUN mkdir -p storage/cache data

# Run as non-root; /app is writable for SQLite and the upload cache
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health', timeout=3)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
