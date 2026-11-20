from dataclasses import dataclass


@dataclass(frozen=True)
class Station:
    name: str
    zone: int


STATIONS = (
    Station(name="Catalunya", zone=1),
    Station(name="Sagrada Familia", zone=1),
    Station(name="Sants Estacio", zone=1),
    Station(name="Zona Universitaria", zone=1),
    Station(name="Sant Cugat", zone=2),
    Station(name="Rubi", zone=2),
    Station(name="Terrassa", zone=3),
)


def find_station(station_name: str) -> Station:
    normalized_name = station_name.strip().lower()
    for station in STATIONS:
        if station.name.lower() == normalized_name:
            return station
    raise KeyError(normalized_name)


def get_station_zone(station_name: str) -> int:
    return find_station(station_name).zone


def list_stations() -> list[Station]:
    return sorted(STATIONS, key=lambda station: station.name)
