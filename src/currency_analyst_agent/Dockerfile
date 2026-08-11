FROM python:3.10-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.9.21 /uv /uvx /usr/local/bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY setup.py ./
COPY src ./src

RUN uv sync --frozen --no-dev

# application code (api, ui, utilities).
COPY api ./api
COPY frontend ./frontend
COPY utils ./utils
COPY main.py ./

# ensure crew output directory exists at runtime.
RUN mkdir -p /app/output /app/src/output

EXPOSE 8000 8501

# Default process: API. Compose overrides this for the Streamlit service.
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]