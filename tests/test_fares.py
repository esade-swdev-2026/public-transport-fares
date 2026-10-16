import pytest

from public_transport_fares.fares import (
    apply_passenger_discount,
    calculate_fare,
    calculate_ticket_price,
    is_valid_passenger_type,
    price_for_zones,
)


def test_fare_within_same_zone() -> None:
    assert calculate_fare(1, 1) == 2.50


def test_fare_between_two_zones() -> None:
    assert calculate_fare(1, 2) == 3.50


def test_fare_between_three_zones() -> None:
    assert calculate_fare(1, 3) == 4.50


def test_fare_in_reverse_direction() -> None:
    assert calculate_fare(3, 1) == 4.50


def test_fare_within_zone_two() -> None:
    assert calculate_fare(2, 2) == 2.50


def test_invalid_origin_zone() -> None:
    with pytest.raises(ValueError, match="Invalid origin zone"):
        calculate_fare(0, 2)


def test_invalid_destination_zone() -> None:
    with pytest.raises(ValueError, match="Invalid destination zone"):
        calculate_fare(1, 4)


@pytest.mark.parametrize(
    "passenger",
    ["adult", "child", "student", "senior"],
)
def test_valid_passenger_types(passenger: str) -> None:
    assert is_valid_passenger_type(passenger)


@pytest.mark.parametrize(
    "passenger",
    ["dog", "", "unknown"],
)
def test_invalid_passenger_types(passenger: str) -> None:
    assert not is_valid_passenger_type(passenger)


@pytest.mark.parametrize(
    ("passenger", "expected_price"),
    [
        ("adult", 4.50),
        ("child", 2.25),
        ("student", 3.60),
        ("senior", 2.70),
    ],
)
def test_passenger_discount_on_three_zone_fare(passenger: str, expected_price: float) -> None:
    assert apply_passenger_discount(4.50, passenger) == pytest.approx(expected_price)


def test_invalid_passenger_discount_raises_error() -> None:
    with pytest.raises(
        ValueError, match="Invalid passenger type. Options: adult, child, student, senior."
    ):
        apply_passenger_discount(4.50, "dog")


def test_price_for_unknown_number_of_zones_raises_error() -> None:
    with pytest.raises(ValueError, match="No fare defined for 4 zones"):
        price_for_zones(4)


def test_ten_trip_ticket_price() -> None:
    assert calculate_ticket_price(2.50, "10-trip") == 20.00


def test_monthly_ticket_price() -> None:
    assert calculate_ticket_price(2.50, "monthly") == 40.00


def test_invalid_ticket_type() -> None:
    with pytest.raises(ValueError, match="Invalid ticket type"):
        calculate_ticket_price(2.50, "weekly")


@pytest.mark.parametrize(
    ("single_price", "expected_price"),
    [
        (2.50, 20.00),
        (3.50, 28.00),
        (4.50, 36.00),
    ],
)
def test_ten_trip_price_for_each_zone(single_price: float, expected_price: float) -> None:
    assert calculate_ticket_price(single_price, "10-trip") == pytest.approx(expected_price)


@pytest.mark.parametrize(
    ("single_price", "expected_price"),
    [
        (2.50, 40.00),
        (3.50, 56.00),
        (4.50, 72.00),
    ],
)
def test_monthly_price_for_each_zone(single_price: float, expected_price: float) -> None:
    assert calculate_ticket_price(single_price, "monthly") == pytest.approx(expected_price)
