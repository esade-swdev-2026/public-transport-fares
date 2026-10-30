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

List all stations and their fare zones:

```bash
uv run fares stations
```

Output:

```text
Catalunya            Zone 1
Rubi                 Zone 2
Sagrada Familia      Zone 1
Sant Cugat           Zone 2
Sants Estacio        Zone 1
Terrassa             Zone 3
Zona Universitaria   Zone 1
```

Stations are listed alphabetically by name, so a name shown here can be passed directly to `fares calculate`.

Valid passenger types are:

- `adult`
- `child`
- `student`
- `senior`

Each passenger type pays a percentage of the adult fare:

| Passenger type | Discount |
| --- | --- |
| `adult` | 0% (default) |
| `child` | 50% |
| `student` | 20% |
| `senior` | 40% |

For example, a child travelling from Catalunya to Terrassa (three zones) pays half of €4.50:

```text
Fare from Catalunya to Terrassa for passenger type child and ticket type single: 2.25 €
```

An unknown passenger type, such as `--passenger dog`, prints an error and exits with a non-zero exit code.

### Ticket Types

Passengers can choose between three ticket types using the `--ticket` option:

| Ticket type | Description |
|---|---|
| `single` | One journey (default option) |
| `10-trip` | Ten journeys with a 20% discount |
| `monthly` | Monthly pass for the selected fare zones |

The application uses simulated prices based on the number of fare zones:

| Zones | Single | 10-trip | Monthly |
|---|---|---|---|
| 1 | €2.50 | €20.00 | €40.00 |
| 2 | €3.50 | €28.00 | €56.00 |
| 3 | €4.50 | €36.00 | €72.00 |

**Examples**

Calculate the price of a 10-trip ticket:

```bash
uv run fares calculate "Catalunya" "Terrassa" --ticket 10-trip
```

Expected price: €36.00.

Calculate the price of a monthly ticket:

```bash
uv run fares calculate "Catalunya" "Terrassa" --ticket monthly
```

Expected price: €72.00.

Apply a student discount to a 10-trip ticket:

```bash
uv run fares calculate "Catalunya" "Terrassa" --ticket 10-trip --passenger student
```

Expected price: €28.80.

If `--ticket` is omitted, the application calculates a single ticket by default.

Invalid ticket types display an error message and exit with a non-zero status code. The prices and discounts are simulated for this academic project and do not represent official public transport fares.

### Ticket Recommendation

Passengers can use the recommend command to find the cheapest ticket type based on the number of journeys they expect to make in a month.

The application compares the total cost of single tickets, 10-trip tickets, and monthly tickets using the existing simulated fare prices.

| Ticket type | Calculation |
|---|---|
|  `single`   |   Single ticket price multiplied by the number of journeys |
|  `10-trip`  |   Price of the 10-trip passes needed to cover all journeys |
|  `monthly`  |   Fixed monthly price based on the number of fare zones |

Examples
Recommend a ticket for 5 journeys within one fare zone:
```bash
uv run fares recommend "Catalunya" "Sagrada Familia" --journeys 5
```

Expected output:
```text
Recommended ticket: single
Journeys per month: 5
Total cost: 12.50 €
```

Recommend a ticket for 10 journeys between two fare zones:
```bash
uv run fares recommend "Catalunya" "Sant Cugat" --journeys 10
```

Expected output:
```text
Recommended ticket: 10-trip
Journeys per month: 10
Total cost: 28.00 €
```

Recommend a ticket for 30 journeys between three fare zones:
```bash
uv run fares recommend "Catalunya" "Terrassa" --journeys 30
```

Expected output:
```text
Recommended ticket: monthly
Journeys per month: 30
Total cost: 72.00 €
```

The number of journeys must be a positive integer. Zero or negative values display an error message and exit with a non-zero status code.

Unknown station names are handled in the same way as in the calculate command.

The recommendation uses adult fares and compares each ticket type separately. It does not combine different ticket types or apply passenger discounts. If two options have the same cost, the application selects the first one in the order: single, 10-trip, monthly.

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


## Develop

Run the project checks with:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

These checks verify code quality, formatting, type correctness, and automated tests.

### Running the Project Checks

To run all project checks from the repository root:

```bash
./scripts/check.sh
```

This script checks code quality with Ruff, verifies formatting, checks type annotations with Mypy, and runs the automated tests with Pytest.

## Layout

```text
public-transport-fares/
├── src/
│   └── public_transport_fares/
│       ├── __main__.py
│       ├── cli.py
│       ├── fares.py
│       └── stations.py
├── tests/
│   ├── test_cli.py
│   ├── test_fares.py
│   └── test_stations.py
├── scripts/
│   └── check.sh
├── pyproject.toml
└── uv.lock
```

- `cli.py`: command-line interface built with Typer.
- `fares.py`: fare calculations, ticket prices, and passenger discounts.
- `stations.py`: station information and fare zones.
- `tests/`: automated tests.
- `scripts/check.sh`: runs the project quality checks.

### Current Assumptions and Limitations

The initial version of Public Transport Fares uses a simplified simulation of Barcelona's fare system.

- The default passenger is an adult. Child, student and senior passengers receive a fixed percentage discount on the adult fare.
- Three ticket types are supported: single, 10-trip, and monthly.
- The application recommends the cheapest ticket type based on the expected number of monthly journeys, using adult fares without combining different ticket types.
- Ticket prices and passenger discounts are simulated and do not represent official Barcelona public transport fares.
- The simulation is limited to metro travel, seven predefined stations, and three fare zones.
- Each station belongs to exactly one zone.
- Single-ticket prices are €2.50, €3.50, and €4.50 for one, two, and three zones respectively. The prices of 10-trip and monthly tickets are calculated from these base fares.
- Fare zones are calculated using the absolute difference between zone numbers plus one.
- Journeys within the same zone count as one zone, and fares are identical in both directions.
- Actual routes, distances, stops, transfers, and travel times are not considered.
- Prices do not change based on time or day.
- Stations and fares are defined directly in the code.
- The application does not yet store journeys, calculate monthly spending, or access live transport information.
- The application runs exclusively through the command line.

These assumptions are intentional simplifications for the first version. Additional functionality will be introduced incrementally through the Product Backlog.

## Use of AI Tools

We used ChatGPT and Claude to support us during the development of this project, mainly for understanding programming concepts, planning features, debugging, and reviewing code.

Our team made the decisions about the project's functionality and requirements. We reviewed the suggestions, tested the application, and took responsibility for the final implementation.

AI tools were used as support throughout the process, but the final decisions and responsibility for the project remain with our team.