import pytest

from public_transport_fares.stations import STATIONS, get_station_zone, list_stations


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


def test_list_stations_includes_every_station() -> None:
    assert len(list_stations()) == len(STATIONS)


def test_list_stations_is_sorted_by_zone_then_name() -> None:
    names = [station.name for station in list_stations()]

    assert names == [
        "Catalunya",
        "Sagrada Familia",
        "Sants Estacio",
        "Zona Universitaria",
        "Rubi",
        "Sant Cugat",
        "Terrassa",
    ]
