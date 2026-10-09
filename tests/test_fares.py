import pytest

from public_transport_fares.fares import calculate_fare, is_valid_passenger_type


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
