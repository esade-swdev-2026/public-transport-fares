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


def get_station_zone(station_name: str) -> int:
    normalized_name = station_name.strip().lower()
    for station in STATIONS:
        if station.name.lower() == normalized_name:
            return station.zone
    raise KeyError(normalized_name)


def list_stations() -> list[Station]:
    return sorted(STATIONS, key=lambda station: (station.zone, station.name))
