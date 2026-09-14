FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
	UV_LINK_MODE=copy \
	PATH="/app/.venv/bin:$PATH"

RUN apt-get update \
	&& apt-get install -y --no-install-recommends libglib2.0-0 libgl1 libxcb1 \
	&& rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN uv sync --no-install-project --no-dev

COPY . .
RUN uv sync --no-dev

RUN adduser --disabled-password --gecos "" appuser \
	&& chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]