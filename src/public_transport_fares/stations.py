STATIONS = {
    "catalunya": 1,
    "sagrada familia": 1,
    "sants estacio": 1,
    "zona universitaria": 1,
    "sant cugat": 2,
    "rubi": 2,
    "terrassa": 3,
}


def get_station_zone(station_name: str) -> int:
    """Return the fare zone of a station."""
    normalized_name = station_name.strip().lower()
    return STATIONS[normalized_name]
