FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
	UV_LINK_MODE=copy \
	PATH="/app/.venv/bin:$PATH" \
	PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

COPY pyproject.toml .
RUN uv sync --no-install-project --no-dev

COPY . .
RUN uv sync --no-dev

# Install Chromium and the OS libraries required by the Playwright endpoint.
RUN uv run playwright install --with-deps chromium

RUN adduser --disabled-password --gecos "" appuser \
	&& chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]