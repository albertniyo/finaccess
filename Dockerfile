# The image needs backend/ and data/processed, so the build context is the repository root:
#   docker build -t finaccess-api .
FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    COMPASS_DATA_DIR=/app/data/processed \
    PORT=8000 \
    WEB_CONCURRENCY=2

COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/app ./app
COPY backend/compass ./compass
RUN uv sync --frozen --no-dev

COPY data/processed ./data/processed
COPY data/provenance ./data/provenance

RUN useradd --create-home --uid 10001 compass
USER compass

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health', timeout=4)"

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"$PORT\" --workers \"$WEB_CONCURRENCY\" --proxy-headers --forwarded-allow-ips='*' --no-server-header"]
