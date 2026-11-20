from dataclasses import dataclass
from datetime import time

from public_transport_fares.config import FareConfig


@dataclass(frozen=True)
class Fare:
    zones: int
    price: float


@dataclass(frozen=True)
class Recommendation:
    ticket_type: str
    total_price: float


TEN_TRIP_JOURNEYS = 10
TEN_TRIP_DISCOUNT = 0.20
MONTHLY_BASE_PRICE = 40.00
SINGLE_BASE_PRICE = 2.50
TICKET_TYPES = ("single", "10-trip", "monthly")

PEAK_SURCHARGE = 0.20
PEAK_PERIODS = (
    (time(7, 0), time(9, 30)),
    (time(17, 0), time(19, 30)),
)


def price_for_zones(
    number_of_zones: int,
    config: FareConfig,
) -> float:
    if number_of_zones not in config.fare_prices:
        raise ValueError(f"No fare defined for {number_of_zones} zones")

    return config.fare_prices[number_of_zones]


def calculate_fare(
    origin_zone: int,
    destination_zone: int,
    config: FareConfig,
) -> float:
    valid_zones = set(config.fare_prices)

    if origin_zone not in valid_zones:
        raise ValueError("Invalid origin zone")

    if destination_zone not in valid_zones:
        raise ValueError("Invalid destination zone")

    number_of_zones = abs(destination_zone - origin_zone) + 1

    return price_for_zones(number_of_zones, config)


def is_valid_passenger_type(
    passenger: str,
    config: FareConfig,
) -> bool:
    return passenger in config.passenger_discounts


def passenger_types(config: FareConfig) -> list[str]:
    """Return the passenger types the fare configuration defines, in file order."""
    return list(config.passenger_discounts)


def apply_passenger_discount(
    price: float,
    passenger: str,
    config: FareConfig,
) -> float:
    if not is_valid_passenger_type(passenger, config):
        options = ", ".join(passenger_types(config))
        raise ValueError(f"Invalid passenger type. Options: {options}.")

    return price * (1 - config.passenger_discounts[passenger])


def calculate_ticket_price(single_price: float, ticket_type: str) -> float:
    if ticket_type == "single":
        return single_price

    if ticket_type == "10-trip":
        return single_price * TEN_TRIP_JOURNEYS * (1 - TEN_TRIP_DISCOUNT)

    if ticket_type == "monthly":
        return MONTHLY_BASE_PRICE * (single_price / SINGLE_BASE_PRICE)

    raise ValueError("Invalid ticket type. Options: single, 10-trip, monthly.")


def is_valid_ticket_type(ticket_type: str) -> bool:
    return ticket_type in TICKET_TYPES


def recommend_ticket(single_price: float, journeys: int, peak_journeys: int = 0) -> Recommendation:
    if single_price < 0:
        raise ValueError("Single ticket price cannot be negative")

    if journeys < 0:
        raise ValueError("Number of journeys cannot be negative.")

    if not 0 <= peak_journeys <= journeys:
        raise ValueError("Peak journeys must be between 0 and the total number of journeys.")

    if journeys == 0:
        return Recommendation(ticket_type="single", total_price=0.0)

    off_peak_journeys = journeys - peak_journeys
    peak_single_price = single_price * (1 + PEAK_SURCHARGE)
    single_total = single_price * off_peak_journeys + peak_single_price * peak_journeys

    ten_trip_price = calculate_ticket_price(single_price, "10-trip")
    ten_trip_packs = (journeys + TEN_TRIP_JOURNEYS - 1) // TEN_TRIP_JOURNEYS
    ten_trip_total = ten_trip_price * ten_trip_packs

    monthly_total = calculate_ticket_price(single_price, "monthly")

    options = {
        "single": single_total,
        "10-trip": ten_trip_total,
        "monthly": monthly_total,
    }

    # On a tie, min keeps the first option in the dict: single, then 10-trip, then monthly.
    cheapest_ticket = min(options, key=lambda ticket: options[ticket])

    return Recommendation(ticket_type=cheapest_ticket, total_price=options[cheapest_ticket])


def is_peak_time(journey_time: time) -> bool:
    """Return True if the time falls inside a peak period (the end time is off-peak)."""
    return any(start <= journey_time < end for start, end in PEAK_PERIODS)


def apply_peak_surcharge(price: float, ticket_type: str, journey_time: time) -> float:
    """Add the peak-time surcharge to single tickets; other tickets keep their price."""
    if ticket_type != "single" or not is_peak_time(journey_time):
        return price

    return price * (1 + PEAK_SURCHARGE)
