from pathlib import Path
from typing import Annotated

import typer

from public_transport_fares.config import FareConfig, load_fare_config
from public_transport_fares.fares import (
    apply_passenger_discount,
    calculate_fare,
    calculate_ticket_price,
    is_valid_passenger_type,
    is_valid_ticket_type,
    recommend_ticket,
)
from public_transport_fares.stations import get_station_zone, list_stations

app = typer.Typer(help="Calculate public transport fares between stations.")


def get_config(path: Path | None) -> FareConfig:
    """Load fare configuration and handle expected errors."""
    try:
        return load_fare_config(path)
    except (OSError, ValueError) as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from None


def check_passenger_type(passenger: str, config: FareConfig) -> None:
    """Stop with an error if the passenger type is not valid."""
    if not is_valid_passenger_type(passenger, config):
        typer.echo(
            f"Error: unknown passenger type '{passenger}'. Options: adult, child, student, senior.",
            err=True,
        )
        raise typer.Exit(code=1)


def get_journey_zones(origin: str, destination: str) -> tuple[int, int]:
    """Return the zones of two stations or show a clear error."""
    try:
        origin_zone = get_station_zone(origin)
        destination_zone = get_station_zone(destination)
    except KeyError as error:
        unknown_station = str(error.args[0])
        typer.echo(
            f"Error: unknown station '{unknown_station}'. "
            "Use 'fares stations' to see valid stations.",
            err=True,
        )
        raise typer.Exit(code=1) from None

    return origin_zone, destination_zone


@app.command()
def calculate(
    origin: str,
    destination: str,
    passenger: str = "adult",
    ticket: str = "single",
    fares: Annotated[
        Path | None,
        typer.Option("--fares", help="Path to a custom fares JSON file."),
    ] = None,
) -> None:
    """Calculate the fare between two stations."""
    config = get_config(fares)

    check_passenger_type(passenger, config)

    if not is_valid_ticket_type(ticket):
        typer.echo(
            f"Error: Invalid ticket type '{ticket}'. Options: single, 10-trip, monthly.",
            err=True,
        )
        raise typer.Exit(code=1)

    origin_zone, destination_zone = get_journey_zones(origin, destination)

    base_price = calculate_fare(origin_zone, destination_zone, config)
    ticket_price = calculate_ticket_price(base_price, ticket)
    price = apply_passenger_discount(ticket_price, passenger, config)

    typer.echo(
        f"Fare from {origin} to {destination} for passenger type {passenger} "
        f"and ticket type {ticket}: {price:.2f} €"
    )


@app.command()
def stations() -> None:
    """List all stations and their fare zones."""
    for station in list_stations():
        typer.echo(f"{station.name:<20} Zone {station.zone}")


@app.command()
def recommend(
    origin: str,
    destination: str,
    journeys: int = typer.Option(
        ...,
        "--journeys",
        help="Expected number of journeys per month.",
    ),
    passenger: str = typer.Option(
        "adult",
        "--passenger",
        help="Passenger type: adult, child, student or senior.",
    ),
    fares: Annotated[
        Path | None,
        typer.Option("--fares", help="Path to a custom fares JSON file."),
    ] = None,
) -> None:
    """Recommend the cheapest ticket for a number of monthly journeys."""
    config = get_config(fares)

    check_passenger_type(passenger, config)

    if journeys <= 0:
        typer.echo(
            "Error: number of journeys must be greater than zero.",
            err=True,
        )
        raise typer.Exit(code=1)

    origin_zone, destination_zone = get_journey_zones(origin, destination)

    single_price = calculate_fare(origin_zone, destination_zone, config)

    recommendation = recommend_ticket(single_price, journeys)

    total_price = apply_passenger_discount(
        recommendation.total_price,
        passenger,
        config,
    )

    typer.echo(
        f"Recommended ticket: {recommendation.ticket_type}\n"
        f"Passenger type: {passenger}\n"
        f"Journeys per month: {journeys}\n"
        f"Total cost: {total_price:.2f} €"
    )
