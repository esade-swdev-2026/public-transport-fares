#!/usr/bin/env bash
set -euo pipefail

echo "==> Ruff check"
uv run ruff check .

echo "==> Ruff format"
uv run ruff format --check .

echo "==> Mypy"
uv run mypy src tests

echo "==> Pytest"
uv run pytest