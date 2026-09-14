# Multi-stage con uv: la imagen final no lleva uv ni dependencias de desarrollo.
# Etiquetas: a verificar en https://github.com/astral-sh/uv/pkgs/container/uv
FROM python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations
RUN uv sync --frozen --no-dev

FROM python:3.14-slim
ARG GIT_SHA=dev
ENV __APP_UPPER___VERSION=$GIT_SHA PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
# uid 1000 = camilo-cachy en la torre: así data/ (montado) queda con su dueño.
RUN useradd --uid 1000 --create-home app
WORKDIR /app
COPY --from=builder --chown=app:app /app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"
# Sin migraciones en el arranque: las aplica ~/srv/bin/deploy como paso propio.
CMD ["uvicorn", "__APP__.main:app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
