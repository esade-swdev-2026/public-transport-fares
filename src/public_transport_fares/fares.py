FARE_PRICES = {
    1: 2.50,
    2: 3.50,
    3: 4.50,
}

# Discount per passenger type, as agreed by the team for backlog item 3.
PASSENGER_DISCOUNTS = {
    "adult": 0.0,
    "child": 0.5,
    "student": 0.2,
    "senior": 0.4,
}


def calculate_fare(origin_zone: int, destination_zone: int) -> float:
    if origin_zone not in FARE_PRICES:
        raise ValueError("Invalid origin zone")

    if destination_zone not in FARE_PRICES:
        raise ValueError("Invalid destination zone")

    number_of_zones = abs(destination_zone - origin_zone) + 1

    return FARE_PRICES[number_of_zones]


def is_valid_passenger_type(passenger: str) -> bool:
    valid_passenger_types = ["adult", "child", "student", "senior"]
    return passenger in valid_passenger_types


def apply_passenger_discount(price: float, passenger: str) -> float:
    if passenger not in PASSENGER_DISCOUNTS:
        raise ValueError("Invalid passenger type: Options: adult, child, student, senior.")

    return price * (1 - PASSENGER_DISCOUNTS[passenger])
