from dataclasses import replace
from datetime import date, datetime, time
from pathlib import Path
from typing import Annotated, NoReturn

import typer

from public_transport_fares.config import FareConfig, load_fare_config
from public_transport_fares.fares import (
    apply_passenger_discount,
    apply_peak_surcharge,
    calculate_fare,
    calculate_ticket_price,
    is_valid_passenger_type,
    is_valid_ticket_type,
    passenger_types,
    recommend_ticket,
)
from public_transport_fares.journeys import (
    Journey,
    is_free_transfer,
    journeys_in_month,
    load_journeys,
    parse_day,
    parse_month,
    parse_time,
    remaining_budget,
    save_journeys,
    spending_by_route,
    total_spending,
)
from public_transport_fares.stations import find_station, get_station_zone, list_stations

app = typer.Typer(help="Calculate public transport fares between stations.")

DEFAULT_JOURNAL = Path("journeys.json")


def stop_with_error(message: str) -> NoReturn:
    """Show an error message and exit with a non-zero code."""
    typer.echo(f"Error: {message}", err=True)
    raise typer.Exit(code=1)


def get_journeys(path: Path) -> list[Journey]:
    """Load saved journeys and handle a broken or unreadable file."""
    try:
        return load_journeys(path)
    except (OSError, ValueError) as error:
        stop_with_error(str(error))


def get_journey_time(value: str | None) -> time:
    """Return the time given as HH:MM, or the current time if none was given."""
    if value is None:
        return datetime.now().time()

    try:
        return parse_time(value)
    except ValueError as error:
        stop_with_error(str(error))


def get_config(path: Path | None) -> FareConfig:
    """Load fare configuration and handle expected errors."""
    try:
        return load_fare_config(path)
    except (OSError, ValueError) as error:
        stop_with_error(str(error))


def check_passenger_type(passenger: str, config: FareConfig) -> None:
    """Stop with an error if the passenger type is not valid."""
    if not is_valid_passenger_type(passenger, config):
        options = ", ".join(passenger_types(config))
        stop_with_error(f"unknown passenger type '{passenger}'. Options: {options}.")


def get_journey_zones(origin: str, destination: str) -> tuple[int, int]:
    """Return the zones of two stations or show a clear error."""
    try:
        origin_zone = get_station_zone(origin)
        destination_zone = get_station_zone(destination)
    except KeyError as error:
        unknown_station = str(error.args[0])
        stop_with_error(
            f"unknown station '{unknown_station}'. Use 'fares stations' to see valid stations."
        )

    return origin_zone, destination_zone


@app.command()
def calculate(
    origin: str,
    destination: str,
    passenger: Annotated[
        str,
        typer.Option(help="Passenger type: adult, child, student or senior."),
    ] = "adult",
    ticket: Annotated[
        str,
        typer.Option(help="Ticket type: single, 10-trip or monthly."),
    ] = "single",
    journey_time: Annotated[
        str | None,
        typer.Option(
            "--time",
            envvar="FARES_TIME",
            help="Time of the journey, HH:MM. Default: now.",
        ),
    ] = None,
    fares: Annotated[
        Path | None,
        typer.Option("--fares", help="Path to a custom fares JSON file."),
    ] = None,
) -> None:
    """Calculate the fare between two stations."""
    config = get_config(fares)
    chosen_time = get_journey_time(journey_time)

    check_passenger_type(passenger, config)

    if not is_valid_ticket_type(ticket):
        stop_with_error(f"Invalid ticket type '{ticket}'. Options: single, 10-trip, monthly.")

    origin_zone, destination_zone = get_journey_zones(origin, destination)

    base_price = calculate_fare(origin_zone, destination_zone, config)
    ticket_price = calculate_ticket_price(base_price, ticket)
    ticket_price = apply_peak_surcharge(ticket_price, ticket, chosen_time)
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
    peak_journeys: int = typer.Option(
        0,
        "--peak-journeys",
        help="Number of journeys expected at peak times.",
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
        stop_with_error("number of journeys must be greater than zero.")

    origin_zone, destination_zone = get_journey_zones(origin, destination)

    single_price = calculate_fare(origin_zone, destination_zone, config)

    try:
        recommendation = recommend_ticket(single_price, journeys, peak_journeys=peak_journeys)
    except ValueError as error:
        stop_with_error(str(error))

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


@app.command()
def save(
    origin: str,
    destination: str,
    passenger: Annotated[
        str,
        typer.Option(help="Passenger type: adult, child, student or senior."),
    ] = "adult",
    day: Annotated[
        str | None,
        typer.Option("--date", help="Date of the journey, YYYY-MM-DD. Default: today."),
    ] = None,
    journey_time: Annotated[
        str | None,
        typer.Option(
            "--time",
            envvar="FARES_TIME",
            help="Time of the journey, HH:MM. Default: now.",
        ),
    ] = None,
    journal: Annotated[
        Path,
        typer.Option(envvar="FARES_JOURNAL", help="File where your journeys are saved."),
    ] = DEFAULT_JOURNAL,
    fares: Annotated[
        Path | None,
        typer.Option("--fares", help="Path to a custom fares JSON file."),
    ] = None,
) -> None:
    """Save a journey you made, at its single-ticket price."""
    config = get_config(fares)
    check_passenger_type(passenger, config)
    origin_zone, destination_zone = get_journey_zones(origin, destination)
    origin = find_station(origin).name
    destination = find_station(destination).name

    try:
        journey_day = parse_day(day) if day else date.today().isoformat()
    except ValueError as error:
        stop_with_error(str(error))

    chosen_time = get_journey_time(journey_time)
    single_price = calculate_fare(origin_zone, destination_zone, config)
    single_price = apply_peak_surcharge(single_price, "single", chosen_time)
    price = round(apply_passenger_discount(single_price, passenger, config), 2)
    journey = Journey(
        day=journey_day,
        origin=origin,
        destination=destination,
        price=price,
        start_time=chosen_time.strftime("%H:%M"),
    )

    saved_journeys = get_journeys(journal)
    previous = saved_journeys[-1] if saved_journeys else None
    free_transfer = is_free_transfer(previous, journey)
    if free_transfer:
        journey = replace(journey, price=0.0)

    try:
        save_journeys(journal, [*saved_journeys, journey])
    except OSError as error:
        stop_with_error(f"could not save journeys to {journal}: {error}")

    note = " (free transfer)" if free_transfer else ""
    typer.echo(f"Saved {journey.day}: {origin} -> {destination}, {journey.price:.2f} €{note}")


@app.command()
def spending(
    month: Annotated[
        str | None,
        typer.Option(help="Month to add up, YYYY-MM. Default: this month."),
    ] = None,
    journal: Annotated[
        Path,
        typer.Option(envvar="FARES_JOURNAL", help="File where your journeys are saved."),
    ] = DEFAULT_JOURNAL,
    budget: Annotated[
        float | None,
        typer.Option(help="Monthly budget in euros. Tells you if you went over it."),
    ] = None,
    by_route: Annotated[
        bool,
        typer.Option("--by-route", help="Also show how much you spent on each route."),
    ] = False,
) -> None:
    """List your saved journeys for a month and their total cost."""
    try:
        chosen_month = parse_month(month) if month else date.today().strftime("%Y-%m")
    except ValueError as error:
        stop_with_error(str(error))

    if budget is not None and budget <= 0:
        stop_with_error("budget must be greater than zero.")

    journeys = journeys_in_month(get_journeys(journal), chosen_month)

    for journey in journeys:
        typer.echo(
            f"{journey.day}  {journey.origin} -> {journey.destination}  {journey.price:.2f} €"
        )

    if by_route:
        typer.echo("By route:")
        for route in spending_by_route(journeys):
            word = "journey" if route.journey_count == 1 else "journeys"
            typer.echo(
                f"  {route.origin} -> {route.destination}: "
                f"{route.journey_count} {word}, {route.total:.2f} €"
            )

    spent = total_spending(journeys)
    typer.echo(f"Journeys in {chosen_month}: {len(journeys)}\nTotal spending: {spent:.2f} €")

    if budget is not None:
        left = remaining_budget(spent, budget)
        if left < 0:
            typer.echo(f"You are {-left:.2f} € over your budget of {budget:.2f} €")
        else:
            typer.echo(f"You have {left:.2f} € left of your budget of {budget:.2f} €")
