FARE_PRICES = {
    1: 2.50,
    2: 3.50,
    3: 4.50,
}


def calculate_fare(origin_zone: int, destination_zone: int) -> float:
    if origin_zone not in FARE_PRICES:
        raise ValueError("Invalid origin zone")

    if destination_zone not in FARE_PRICES:
        raise ValueError("Invalid destination zone")

    number_of_zones = abs(destination_zone - origin_zone) + 1

    return FARE_PRICES[number_of_zones]
