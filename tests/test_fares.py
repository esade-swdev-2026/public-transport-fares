from dataclasses import FrozenInstanceError

import pytest

from public_transport_fares.config import FareConfig
from public_transport_fares.fares import (
    Recommendation,
    apply_passenger_discount,
    calculate_fare,
    calculate_ticket_price,
    is_valid_passenger_type,
    price_for_zones,
    recommend_ticket,
)


@pytest.fixture
def default_config() -> FareConfig:
    """Provide the default fares without reading a file."""
    return FareConfig(
        fare_prices={1: 2.50, 2: 3.50, 3: 4.50},
        passenger_discounts={
            "adult": 0.0,
            "child": 0.5,
            "student": 0.2,
            "senior": 0.4,
        },
    )


@pytest.fixture
def custom_config() -> FareConfig:
    """Provide alternative fares for testing."""
    return FareConfig(
        fare_prices={1: 3.00, 2: 4.00, 3: 5.00},
        passenger_discounts={
            "adult": 0.0,
            "child": 0.6,
            "student": 0.3,
            "senior": 0.5,
        },
    )


def test_fare_within_same_zone(default_config: FareConfig) -> None:
    assert calculate_fare(1, 1, default_config) == 2.50


def test_fare_between_two_zones(default_config: FareConfig) -> None:
    assert calculate_fare(1, 2, default_config) == 3.50


def test_fare_between_three_zones(default_config: FareConfig) -> None:
    assert calculate_fare(1, 3, default_config) == 4.50


def test_fare_in_reverse_direction(default_config: FareConfig) -> None:
    assert calculate_fare(3, 1, default_config) == 4.50


def test_fare_within_zone_two(default_config: FareConfig) -> None:
    assert calculate_fare(2, 2, default_config) == 2.50


def test_invalid_origin_zone(default_config: FareConfig) -> None:
    with pytest.raises(ValueError, match="Invalid origin zone"):
        calculate_fare(0, 2, default_config)


def test_invalid_destination_zone(default_config: FareConfig) -> None:
    with pytest.raises(ValueError, match="Invalid destination zone"):
        calculate_fare(1, 4, default_config)


@pytest.mark.parametrize(
    "passenger",
    ["adult", "child", "student", "senior"],
)
def test_valid_passenger_types(
    passenger: str,
    default_config: FareConfig,
) -> None:
    assert is_valid_passenger_type(passenger, default_config)


@pytest.mark.parametrize(
    "passenger",
    ["dog", "", "unknown"],
)
def test_invalid_passenger_types(
    passenger: str,
    default_config: FareConfig,
) -> None:
    assert not is_valid_passenger_type(passenger, default_config)


@pytest.mark.parametrize(
    ("passenger", "expected_price"),
    [
        ("adult", 4.50),
        ("child", 2.25),
        ("student", 3.60),
        ("senior", 2.70),
    ],
)
def test_passenger_discount_on_three_zone_fare(
    passenger: str,
    expected_price: float,
    default_config: FareConfig,
) -> None:
    assert apply_passenger_discount(4.50, passenger, default_config) == pytest.approx(
        expected_price
    )


def test_invalid_passenger_discount_raises_error(
    default_config: FareConfig,
) -> None:
    with pytest.raises(
        ValueError,
        match="Invalid passenger type",
    ):
        apply_passenger_discount(4.50, "dog", default_config)


def test_price_for_unknown_number_of_zones_raises_error(
    default_config: FareConfig,
) -> None:
    with pytest.raises(ValueError, match="No fare defined for 4 zones"):
        price_for_zones(4, default_config)


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
def test_ten_trip_price_for_each_zone(
    single_price: float,
    expected_price: float,
) -> None:
    assert calculate_ticket_price(single_price, "10-trip") == pytest.approx(expected_price)


@pytest.mark.parametrize(
    ("single_price", "expected_price"),
    [
        (2.50, 40.00),
        (3.50, 56.00),
        (4.50, 72.00),
    ],
)
def test_monthly_price_for_each_zone(
    single_price: float,
    expected_price: float,
) -> None:
    assert calculate_ticket_price(single_price, "monthly") == pytest.approx(expected_price)


def test_recommend_cheapest_ticket_for_five_journeys() -> None:
    result = recommend_ticket(single_price=2.50, journeys=5)

    assert result == Recommendation(
        ticket_type="single",
        total_price=12.50,
    )


def test_recommend_ten_trip_ticket() -> None:
    result = recommend_ticket(single_price=2.50, journeys=10)

    assert result == Recommendation(
        ticket_type="10-trip",
        total_price=20.00,
    )


def test_recommend_monthly_ticket() -> None:
    result = recommend_ticket(single_price=2.50, journeys=30)

    assert result == Recommendation(
        ticket_type="monthly",
        total_price=40.00,
    )


def test_recommend_ticket_with_zero_journeys() -> None:
    result = recommend_ticket(single_price=2.50, journeys=0)

    assert result == Recommendation(
        ticket_type="single",
        total_price=0.0,
    )


def test_recommend_ticket_with_negative_journeys() -> None:
    with pytest.raises(
        ValueError,
        match="Number of journeys cannot be negative",
    ):
        recommend_ticket(single_price=2.50, journeys=-5)


def test_recommend_ticket_for_two_zones() -> None:
    result = recommend_ticket(single_price=3.50, journeys=30)

    assert result == Recommendation(
        ticket_type="monthly",
        total_price=56.00,
    )


def test_recommend_ticket_with_negative_price() -> None:
    with pytest.raises(
        ValueError,
        match="Single ticket price cannot be negative",
    ):
        recommend_ticket(single_price=-2.50, journeys=10)


def test_recommend_ticket_with_equal_prices() -> None:
    result = recommend_ticket(single_price=2.50, journeys=20)

    assert result == Recommendation(
        ticket_type="10-trip",
        total_price=40.00,
    )


def test_recommendation_is_immutable() -> None:
    result = recommend_ticket(single_price=2.50, journeys=30)

    with pytest.raises(FrozenInstanceError):
        result.total_price = 50.00  # type: ignore[misc]


def test_custom_fare_for_three_zones(
    custom_config: FareConfig,
) -> None:
    assert calculate_fare(1, 3, custom_config) == 5.00


def test_custom_fare_for_two_zones(
    custom_config: FareConfig,
) -> None:
    assert calculate_fare(1, 2, custom_config) == 4.00


def test_custom_passenger_discount(
    custom_config: FareConfig,
) -> None:
    price = apply_passenger_discount(5.00, "student", custom_config)

    assert price == pytest.approx(3.50)


def test_default_and_custom_fares_are_different(
    default_config: FareConfig,
    custom_config: FareConfig,
) -> None:
    default_price = calculate_fare(1, 3, default_config)
    custom_price = calculate_fare(1, 3, custom_config)

    assert default_price == 4.50
    assert custom_price == 5.00
    assert default_price != custom_price
