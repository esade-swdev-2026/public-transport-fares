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
uv run fares calculate "Catalunya" "Terrassa"
```

Calculate a fare for a different passenger type:

```bash
uv run fares calculate "Catalunya" "Terrassa" --passenger child
```

Valid passenger types are:

- `adult`
- `child`
- `student`
- `senior`


### Unknown Station Errors

Station names are case-insensitive, and extra spaces at the beginning or end are ignored.

If a passenger enters an unknown station, the application displays a clear error message.

For example:

```bash
uv run fares calculate "Madrid" "Terrassa"
```

Output:

```text
Error: unknown station 'madrid'. Use 'fares stations' to see valid stations.
```

The application exits with a non-zero exit code and does not display a Python traceback.

Note: The `fares stations` command is planned for a future version and is not yet implemented.


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


### Current Assumptions and Limitations

The initial version of Public Transport Fares uses a simplified simulation of Barcelona's fare system.

- The default passenger is an adult, and no passenger discounts are currently applied.
- Only single-journey tickets are supported.
- The simulation is limited to metro travel, seven predefined stations, and three fare zones.
- Each station belongs to exactly one zone.
- Ticket prices are fixed at €2.50, €3.50, and €4.50 for one, two, and three zones respectively.
- Fare zones are calculated using the absolute difference between zone numbers plus one.
- Journeys within the same zone count as one zone, and fares are identical in both directions.
- Actual routes, distances, stops, transfers, and travel times are not considered.
- Prices do not change based on time or day.
- Stations and fares are defined directly in the code.
- The application does not yet store journeys, calculate monthly spending, or access live transport information.
- The application runs exclusively through the command line.

These assumptions are intentional simplifications for the first version. Additional functionality will be introduced incrementally through the Product Backlog.