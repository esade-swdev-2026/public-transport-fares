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
uv run fares calculate "Catalunya" "Terrassa" --time 12:00
```

Calculate a fare for a different passenger type:

```bash
uv run fares calculate "Catalunya" "Terrassa" --passenger child --time 12:00
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
| `single` | Total price of single tickets, including a 20% surcharge for journeys at peak times |
| `10-trip` | Price of the 10-trip passes needed to cover all journeys |
| `monthly` | Fixed monthly price based on the number of fare zones |

Examples
Recommend a ticket for 5 journeys within one fare zone:
```bash
uv run fares recommend "Catalunya" "Sagrada Familia" --journeys 5
```

Expected output:
```text
Recommended ticket: single
Passenger type: adult
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
Passenger type: adult
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
Passenger type: adult
Journeys per month: 30
Total cost: 72.00 €
```

The number of journeys must be a positive integer. Zero or negative values display an error message and exit with a non-zero status code.

Recommend a ticket for a student making 30 journeys between three fare zones:
```bash
uv run fares recommend "Catalunya" "Terrassa" --journeys 30 --passenger student
```

Expected output:
```text
Recommended ticket: monthly
Passenger type: student
Journeys per month: 30
Total cost: 57.60 €
```

If `--passenger` is omitted, the recommendation uses adult fares. Unknown passenger types and unknown station names are handled in the same way as in the calculate command.

The passenger discount is applied to the total cost of the recommended ticket. The recommendation compares the cost of using each ticket type for all journeys. If two options have the same cost, the application selects the first one in the order: single, 10-trip, monthly.

Use `--peak-journeys` to specify how many of your monthly journeys will be at peak times. The value must be an integer between 0 and the total number of journeys. If `--peak-journeys` is omitted, it defaults to 0. Values outside that range display an error message and exit with a non-zero status code.

Recommend a ticket for 7 peak-time journeys within one fare zone:
```bash
uv run fares recommend "Catalunya" "Sagrada Familia" --journeys 7 --peak-journeys 7
```

Expected output:
```text
Recommended ticket: 10-trip
Passenger type: adult
Journeys per month: 7
Total cost: 20.00 €
```

Seven single tickets at peak times would cost €21.00.

### Track Your Monthly Spending

Save each journey you make. Its single-ticket price, with your passenger discount, is stored in `journeys.json`:

```bash
uv run fares save "Catalunya" "Terrassa"
uv run fares save "Terrassa" "Catalunya" --date 2026-11-03 --passenger student
```

See your journeys and total spending for a month (default: this month):

```bash
uv run fares spending --month 2026-11
```

Use `--journal PATH` (or the `FARES_JOURNAL` environment variable) to keep the journeys in another file.


### Peak-Time Surcharge

Single tickets cost 20% more at peak time:

- 07:00 to 09:30
- 17:00 to 19:30

The end time is off-peak (09:30 itself is not peak time). 10-trip and monthly tickets never have a surcharge.

Use `--time HH:MM` with `calculate` or `save`. If `--time` is omitted, the current time is used.

```bash
uv run fares calculate "Catalunya" "Terrassa" --time 08:15
```

Output:

```text
Fare from Catalunya to Terrassa for passenger type adult and ticket type single: 5.40 €
```

The surcharge is applied before the passenger discount, so a child at 08:15 pays 2.70 €. An invalid time, such as `--time 25:99`, prints an error and exits with a non-zero exit code.


### Free Transfers

When you save a journey with `save`, it is free (0.00 €) if it continues your last saved journey:

- it is on the same day and starts at most 75 minutes after the last saved journey started,
- it starts at the station where the last journey ended,
- it does not go back to the station where the last journey started (a return trip is paid), and
- the last journey was paid (only one free transfer in a row).

The 75-minute window follows the transfer time of Barcelona's integrated single-zone tickets.

```bash
uv run fares save "Catalunya" "Sant Cugat" --date 2026-11-17 --time 12:00
uv run fares save "Sant Cugat" "Terrassa" --date 2026-11-17 --time 12:30
```

Output:

```text
Saved 2026-11-17: Catalunya -> Sant Cugat, 3.50 €
Saved 2026-11-17: Sant Cugat -> Terrassa, 0.00 € (free transfer)
```

Each saved journey now records its start time. Journeys saved before this change have no start time and are never counted as transfers.



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


## Run with Docker

### Run the published image

Our CI pipeline publishes the image to GitHub Container Registry on every merge to `main` and on the `v1.0` tag. The package is private, so log in first with a GitHub token that has `read:packages`, then download it:

```bash
docker login ghcr.io -u <your-github-username>
docker pull ghcr.io/esade-swdev-2026/public-transport-fares:v1.0
```

The image is built for `linux/amd64`. On a Mac with an Apple chip, add `--platform linux/amd64` to `docker pull` and `docker run`.

Calculate a fare:

```bash
docker run --rm ghcr.io/esade-swdev-2026/public-transport-fares:v1.0 \
  calculate "Catalunya" "Terrassa" --time 12:00
```

Expected fare: 4.50 €.

### Build the image locally

Build the Docker image:

```bash
docker build -t fares .
```

Display command-line help:

```bash
docker run --rm fares --help
```

Calculate a fare:

```bash
docker run --rm fares calculate "Catalunya" "Terrassa" --time 12:00
```

Recommend a ticket:

```bash
docker run --rm fares recommend "Catalunya" "Terrassa" --journeys 5
```

Verify that the container runs as a non-root user:

```bash
docker run --rm --entrypoint id fares
```

### Saved journeys with Docker

Journeys are saved in `/data` inside the container. Mount a named volume there, and they survive `docker rm`:

```bash
docker run --rm -v fares-journeys:/data fares save "Catalunya" "Terrassa" --date 2026-11-03 --time 12:00
docker run --rm -v fares-journeys:/data fares save "Terrassa" "Catalunya" --date 2026-11-03 --time 12:00
docker run --rm -v fares-journeys:/data fares spending --month 2026-11
```

Each container is removed after it runs, but the last command still shows `Total spending: 9.00 €`.


### Custom fares with Docker

Fare prices and passenger discounts can be loaded from an external JSON
file using a read-only bind mount.

Build the image:

```bash
docker build -t fares .
```

Calculate a fare with the default configuration:

```bash
docker run --rm fares calculate "Catalunya" "Terrassa" --time 12:00
```

Expected fare: 4.50 €.

Use the external configuration file:

```bash
docker run --rm \
  --mount type=bind,source="$(pwd)/my-fares.json",target=/config/fares.json,readonly \
  fares calculate "Catalunya" "Terrassa" \
  --fares /config/fares.json --time 12:00
```

Expected fare: 5.00 €.

To verify that the external configuration works without rebuilding
the image, change the zone 3 price in `my-fares.json` from 5.00 to 6.00
and run the same Docker command again.

The result changes to 6.00 € without running `docker build` again.

The configuration remains on the host computer and is mounted
read-only inside the container.


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
│       ├── config.py
│       ├── fares.json
│       ├── fares.py
│       ├── journeys.py
│       └── stations.py
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_fares.py
│   ├── test_journeys.py
│   └── test_stations.py
├── scripts/
│   └── check.sh
├── .github/workflows/check.yml
├── Dockerfile
├── .dockerignore
├── my-fares.json
├── pyproject.toml
└── uv.lock
```

- `cli.py`: command-line interface built with Typer: reads input, prints results.
- `config.py`: loads and validates fare prices and passenger discounts from JSON.
- `fares.json`: the default fare prices and passenger discounts.
- `fares.py`: fare calculations, ticket prices, peak-time surcharge, and ticket recommendations.
- `journeys.py`: saved journeys, free transfers, and monthly spending.
- `stations.py`: station information and fare zones.
- `tests/`: automated tests.
- `scripts/check.sh`: runs the project quality checks.
- `.github/workflows/check.yml`: CI that runs the checks, builds the image, and publishes it to GHCR.
- `Dockerfile`, `.dockerignore`: how the container image is built.
- `my-fares.json`: an example of custom fares, used in *Custom fares with Docker*.

### Current Assumptions and Limitations

Public Transport Fares uses a simplified simulation of Barcelona's fare system.

- The default passenger is an adult. Child, student and senior passengers receive a fixed percentage discount on the adult fare.
- Three ticket types are supported: single, 10-trip, and monthly.
- The application recommends the cheapest ticket type based on the expected number of monthly journeys and the passenger type, without combining different ticket types.
- Ticket prices and passenger discounts are simulated and do not represent official Barcelona public transport fares.
- The simulation is limited to metro travel, seven predefined stations, and three fare zones.
- Each station belongs to exactly one zone.
- Single-ticket prices are €2.50, €3.50, and €4.50 for one, two, and three zones respectively. The prices of 10-trip and monthly tickets are calculated from these base fares.
- Fare zones are calculated using the absolute difference between zone numbers plus one.
- Journeys within the same zone count as one zone, and fares are identical in both directions.
- Fare calculations use zones. The application uses saved journeys to check for free transfers.
- Single-ticket prices include a 20% surcharge at peak time; prices do not change by day of the week.
- Stations are defined in the code. Default fare prices and passenger discounts are included in the application and can be overridden with a JSON file.
- The application does not access live transport information.
- The application runs exclusively through the command line.

These assumptions are intentional simplifications for an academic project.

## Use of AI Tools

We used ChatGPT and Claude to support us during the development of this project, mainly for understanding programming concepts, planning features, debugging, and reviewing code.

Our team made the decisions about the project's functionality and requirements. We reviewed the suggestions, tested the application, and took responsibility for the final implementation.

AI tools were used as support throughout the process, but the final decisions and responsibility for the project remain with our team.