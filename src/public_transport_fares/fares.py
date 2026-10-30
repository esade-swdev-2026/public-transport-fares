from dataclasses import dataclass


@dataclass(frozen=True)
class Fare:
    zones: int
    price: float


FARE_PRICES = (
    Fare(zones=1, price=2.50),
    Fare(zones=2, price=3.50),
    Fare(zones=3, price=4.50),
)

VALID_ZONES = {fare.zones for fare in FARE_PRICES}

PASSENGER_DISCOUNTS = {
    "adult": 0.0,
    "child": 0.5,
    "student": 0.2,
    "senior": 0.4,
}

TEN_TRIP_JOURNEYS = 10
TEN_TRIP_DISCOUNT = 0.20
MONTHLY_BASE_PRICE = 40.00
SINGLE_BASE_PRICE = 2.50
TICKET_TYPES = ("single", "10-trip", "monthly")


def price_for_zones(number_of_zones: int) -> float:
    for fare in FARE_PRICES:
        if fare.zones == number_of_zones:
            return fare.price
    raise ValueError(f"No fare defined for {number_of_zones} zones")


def calculate_fare(origin_zone: int, destination_zone: int) -> float:
    if origin_zone not in VALID_ZONES:
        raise ValueError("Invalid origin zone")

    if destination_zone not in VALID_ZONES:
        raise ValueError("Invalid destination zone")

    number_of_zones = abs(destination_zone - origin_zone) + 1

    return price_for_zones(number_of_zones)


def is_valid_passenger_type(passenger: str) -> bool:
    return passenger in PASSENGER_DISCOUNTS


def apply_passenger_discount(price: float, passenger: str) -> float:
    if not is_valid_passenger_type(passenger):
        raise ValueError("Invalid passenger type. Options: adult, child, student, senior.")

    return price * (1 - PASSENGER_DISCOUNTS[passenger])


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


def recommend_ticket(single_price: float, journeys: int) -> tuple[str, float]:
    if single_price < 0:
        raise ValueError("Single ticket price cannot be negative")

    if journeys < 0:
        raise ValueError("Number of journeys cannot be negative.")

    if journeys == 0:
        return ("single", 0.0)

    single_total = single_price * journeys

    ten_trip_price = calculate_ticket_price(single_price, "10-trip")
    ten_trip_packs = (journeys + TEN_TRIP_JOURNEYS - 1) // TEN_TRIP_JOURNEYS
    ten_trip_total = ten_trip_price * ten_trip_packs

    monthly_total = calculate_ticket_price(single_price, "monthly")

    options = {
        "single": single_total,
        "10-trip": ten_trip_total,
        "monthly": monthly_total,
    }

    cheapest_ticket = min(options, key=lambda ticket: options[ticket])

    return cheapest_ticket, options[cheapest_ticket]
