import typer

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


@app.command()
def calculate(
    origin: str,
    destination: str,
    passenger: str = "adult",
    ticket: str = "single",
) -> None:
    """Calculate the fare between two stations."""

    if not is_valid_passenger_type(passenger):
        typer.echo(
            f"Error: unknown passenger type '{passenger}'.",
            err=True,
        )
        raise typer.Exit(code=1)

    if not is_valid_ticket_type(ticket):
        typer.echo(
            f"Error: Invalid ticket type '{ticket}'. Options: single, 10-trip, monthly.",
            err=True,
        )
        raise typer.Exit(code=1)

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

    base_price = calculate_fare(origin_zone, destination_zone)
    ticket_price = calculate_ticket_price(base_price, ticket)
    price = apply_passenger_discount(ticket_price, passenger)

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
) -> None:
    """Recommend the cheapest ticket for a number of monthly journeys."""

    if journeys <= 0:
        typer.echo(
            "Error: number of journeys must be greater than zero.",
            err=True,
        )
        raise typer.Exit(code=1)

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

    single_price = calculate_fare(origin_zone, destination_zone)
    ticket_type, total_price = recommend_ticket(single_price, journeys)

    typer.echo(
        f"Recommended ticket: {ticket_type}\n"
        f"Journeys per month: {journeys}\n"
        f"Total cost: {total_price:.2f} €"
    )
