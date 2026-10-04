FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.1 /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

RUN mkdir -p /app/data

CMD ["sh", "-c", "mkdir -p /app/data && exec uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port 8000"]
