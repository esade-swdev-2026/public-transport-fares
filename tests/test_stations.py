import pytest

from public_transport_fares.stations import get_station_zone


def test_station_in_zone_one() -> None:
    assert get_station_zone("Catalunya") == 1


def test_station_in_zone_two() -> None:
    assert get_station_zone("Sant Cugat") == 2


def test_station_in_zone_three() -> None:
    assert get_station_zone("Terrassa") == 3


def test_station_name_is_case_insensitive() -> None:
    assert get_station_zone("CATALUNYA") == 1


def test_station_name_ignores_extra_spaces() -> None:
    assert get_station_zone("  Catalunya  ") == 1


def test_unknown_station_raises_error() -> None:
    with pytest.raises(KeyError):
        get_station_zone("Madrid")


def test_empty_station_raises_error() -> None:
    with pytest.raises(KeyError):
        get_station_zone("")
