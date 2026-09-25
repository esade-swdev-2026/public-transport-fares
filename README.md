# Public Transport Fares

A command-line application that helps passengers calculate public transport fares between stations.

The project is designed to provide clear fare information based on the journey and passenger type.

## Install

Install the project and its dependencies with:

```bash
uv sync
```

This creates a virtual environment and installs the dependencies specified in `pyproject.toml` using the exact versions recorded in `uv.lock`.

## Run

Show the available commands:

```bash
uv run fares --help
```

Calculate a fare using the default adult passenger type:

```bash
uv run fares calculate "Sol" "Airport"
```

Calculate a fare for a different passenger type:

```bash
uv run fares calculate "Sol" "Airport" --passenger child
```

Valid passenger types are:

- `adult`
- `child`
- `student`
- `senior`

## Develop

Run the project checks with:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

These checks verify code quality, formatting, type correctness, and automated tests.

## Layout

```text
src/public_transport_fares/
    cli.py          Typer command-line interface
    __main__.py     allows the package to be run as a Python module
tests/
    test_cli.py     automated CLI tests
pyproject.toml      project configuration and dependencies
uv.lock             exact dependency versions
```