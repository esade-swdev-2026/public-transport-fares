
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/uv

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Copy the application and install it
COPY README.md LICENSE ./
COPY src ./src
RUN uv sync --locked --no-dev

# Run the application as a non-root user
RUN useradd --create-home app
USER app

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["fares"]
CMD ["--help"]
