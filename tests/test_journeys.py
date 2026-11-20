from datetime import time
from pathlib import Path

import pytest

from public_transport_fares.journeys import (
    Journey,
    is_free_transfer,
    journeys_from_json,
    journeys_in_month,
    journeys_to_json,
    load_journeys,
    minutes_between,
    parse_day,
    parse_month,
    parse_time,
    remaining_budget,
    save_journeys,
    total_spending,
)

NOVEMBER_TRIP = Journey(day="2026-11-03", origin="Catalunya", destination="Terrassa", price=4.50)
NOVEMBER_RETURN = Journey(day="2026-11-03", origin="Terrassa", destination="Catalunya", price=4.50)
DECEMBER_TRIP = Journey(day="2026-12-01", origin="Catalunya", destination="Sants", price=2.50)


def test_journeys_survive_a_round_trip_through_json() -> None:
    journeys = [NOVEMBER_TRIP, DECEMBER_TRIP]

    assert journeys_from_json(journeys_to_json(journeys)) == journeys


def test_journeys_from_json_rejects_broken_text() -> None:
    with pytest.raises(ValueError, match="Invalid journeys file"):
        journeys_from_json("not json")


def test_journeys_from_json_rejects_missing_fields() -> None:
    with pytest.raises(ValueError, match="Invalid journeys file"):
        journeys_from_json('[{"day": "2026-11-03"}]')


def test_journeys_in_month_keeps_only_that_month() -> None:
    journeys = [NOVEMBER_TRIP, DECEMBER_TRIP, NOVEMBER_RETURN]

    assert journeys_in_month(journeys, "2026-11") == [NOVEMBER_TRIP, NOVEMBER_RETURN]


def test_total_spending_adds_the_prices() -> None:
    assert total_spending([NOVEMBER_TRIP, NOVEMBER_RETURN]) == 9.00


def test_total_spending_of_no_journeys_is_zero() -> None:
    assert total_spending([]) == 0.0


def test_total_spending_is_rounded_to_cents() -> None:
    journeys = [Journey("2026-11-01", "A", "B", 0.1), Journey("2026-11-02", "A", "B", 0.2)]

    assert total_spending(journeys) == 0.30


def test_parse_month_accepts_year_and_month() -> None:
    assert parse_month("2026-11") == "2026-11"


@pytest.mark.parametrize("month", ["2026-13", "november", "2026-11-03"])
def test_parse_month_rejects_anything_else(month: str) -> None:
    with pytest.raises(ValueError, match="Invalid month"):
        parse_month(month)


def test_parse_day_accepts_a_date() -> None:
    assert parse_day("2026-11-17") == "2026-11-17"


def test_parse_day_rejects_an_impossible_date() -> None:
    with pytest.raises(ValueError, match="Invalid date"):
        parse_day("2026-02-30")


def test_load_journeys_from_a_missing_file_returns_no_journeys(tmp_path: Path) -> None:
    assert load_journeys(tmp_path / "journeys.json") == []


def test_saved_journeys_can_be_loaded_again(tmp_path: Path) -> None:
    path = tmp_path / "data" / "journeys.json"

    save_journeys(path, [NOVEMBER_TRIP])

    assert load_journeys(path) == [NOVEMBER_TRIP]


def test_parse_time_reads_hours_and_minutes() -> None:
    assert parse_time("08:15") == time(8, 15)


@pytest.mark.parametrize("value", ["25:00", "8h15", "morning"])
def test_parse_time_rejects_invalid_times(value: str) -> None:
    with pytest.raises(ValueError, match="Invalid time"):
        parse_time(value)


def make_journey(origin: str, destination: str, start_time: str, price: float = 3.50) -> Journey:
    return Journey(
        day="2026-11-17",
        origin=origin,
        destination=destination,
        price=price,
        start_time=start_time,
    )


FIRST_LEG = make_journey("Catalunya", "Sant Cugat", "08:00")


def test_journeys_keep_their_start_time_through_json() -> None:
    assert journeys_from_json(journeys_to_json([FIRST_LEG])) == [FIRST_LEG]


def test_old_journeys_without_start_time_still_load() -> None:
    old_file = '[{"day": "2026-11-03", "origin": "A", "destination": "B", "price": 2.5}]'

    assert journeys_from_json(old_file)[0].start_time is None


def test_minutes_between() -> None:
    assert minutes_between(time(8, 0), time(9, 15)) == 75


def test_free_transfer_when_continuing_within_window() -> None:
    next_leg = make_journey("Sant Cugat", "Terrassa", "09:15")

    assert is_free_transfer(FIRST_LEG, next_leg)


@pytest.mark.parametrize(
    "next_leg",
    [
        make_journey("Sant Cugat", "Terrassa", "09:16"),
        make_journey("Rubi", "Terrassa", "08:30"),
        make_journey("Sant Cugat", "Catalunya", "08:30"),
        make_journey("Sant Cugat", "Terrassa", "07:59"),
    ],
    ids=["after-75-minutes", "different-station", "return-trip", "earlier-time"],
)
def test_no_free_transfer(next_leg: Journey) -> None:
    assert not is_free_transfer(FIRST_LEG, next_leg)


def test_no_free_transfer_on_another_day() -> None:
    next_day = Journey("2026-11-18", "Sant Cugat", "Terrassa", 3.50, "08:30")

    assert not is_free_transfer(FIRST_LEG, next_day)


def test_no_free_transfer_after_a_free_transfer() -> None:
    free_leg = make_journey("Sant Cugat", "Terrassa", "08:30", price=0.0)
    third_leg = make_journey("Terrassa", "Rubi", "08:50")

    assert not is_free_transfer(free_leg, third_leg)


def test_no_free_transfer_without_previous_journey_or_time() -> None:
    next_leg = make_journey("Sant Cugat", "Terrassa", "08:30")
    old_journey = Journey("2026-11-17", "Catalunya", "Sant Cugat", 3.50)

    assert not is_free_transfer(None, next_leg)
    assert not is_free_transfer(old_journey, next_leg)


def test_remaining_budget_is_positive_under_budget() -> None:
    assert remaining_budget(spent=43.80, budget=50) == 6.20


def test_remaining_budget_is_negative_over_budget() -> None:
    assert remaining_budget(spent=56.20, budget=50) == -6.20


def test_remaining_budget_is_zero_exactly_at_budget() -> None:
    assert remaining_budget(spent=50, budget=50) == 0
