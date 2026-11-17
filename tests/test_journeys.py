from datetime import time
from pathlib import Path

import pytest

from public_transport_fares.journeys import (
    Journey,
    journeys_from_json,
    journeys_in_month,
    journeys_to_json,
    load_journeys,
    parse_day,
    parse_month,
    parse_time,
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
