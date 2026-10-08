import typer

from public_transport_fares.fares import calculate_fare
from public_transport_fares.stations import get_station_zone

app = typer.Typer(help="Calculate public transport fares between stations.")


@app.callback()
def main() -> None:
    """Public transport fare calculator."""
    pass


@app.command()
def calculate(
    origin: str,
    destination: str,
    passenger: str = "adult",
) -> None:
    """Calculate the fare between two stations."""

    valid_passenger_types = ["adult", "child", "student", "senior"]

    if passenger not in valid_passenger_types:
        typer.echo(
            f"Error: unknown passenger type '{passenger}'.",
            err=True,
        )
        raise typer.Exit(code=1)

    try:
        origin_zone = get_station_zone(origin)
        destination_zone = get_station_zone(destination)
    except KeyError:
        typer.echo(
            "Error: unknown station. Use 'fares stations' to see valid stations.",
            err=True,
        )
        raise typer.Exit(code=1) from None

    price = calculate_fare(origin_zone, destination_zone)

    typer.echo(f"Fare from {origin} to {destination} for passenger type {passenger}: {price:.2f} €")


if __name__ == "__main__":
    app()
