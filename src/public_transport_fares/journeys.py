import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Journey:
    day: str
    origin: str
    destination: str
    price: float


def parse_month(month: str) -> str:
    """Return the month as YYYY-MM, or raise ValueError if it is not one."""
    try:
        date.fromisoformat(f"{month}-01")
    except ValueError:
        raise ValueError(f"Invalid month '{month}'. Use YYYY-MM, for example 2026-11.") from None
    return month


def parse_day(day: str) -> str:
    """Return the day as YYYY-MM-DD, or raise ValueError if it is not one."""
    try:
        return date.fromisoformat(day).isoformat()
    except ValueError:
        raise ValueError(f"Invalid date '{day}'. Use YYYY-MM-DD, for example 2026-11-17.") from None


def journeys_from_json(content: str) -> list[Journey]:
    """Convert the text of a journeys file into a list of journeys."""
    try:
        data = json.loads(content)
        return [
            Journey(
                day=str(item["day"]),
                origin=str(item["origin"]),
                destination=str(item["destination"]),
                price=float(item["price"]),
            )
            for item in data
        ]
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Invalid journeys file: {error}") from error


def journeys_to_json(journeys: list[Journey]) -> str:
    """Convert a list of journeys into the text of a journeys file."""
    return json.dumps([asdict(journey) for journey in journeys], indent=2, ensure_ascii=False)


def journeys_in_month(journeys: list[Journey], month: str) -> list[Journey]:
    """Return the journeys made in a month given as YYYY-MM."""
    return [journey for journey in journeys if journey.day.startswith(f"{month}-")]


def total_spending(journeys: list[Journey]) -> float:
    """Return the total price of the journeys, rounded to cents."""
    return round(sum(journey.price for journey in journeys), 2)


def load_journeys(path: Path) -> list[Journey]:
    """Read saved journeys from a file; a missing file means no journeys yet."""
    if not path.exists():
        return []
    return journeys_from_json(path.read_text(encoding="utf-8"))


def save_journeys(path: Path, journeys: list[Journey]) -> None:
    """Write journeys to a file, creating its folder if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(journeys_to_json(journeys) + "\n", encoding="utf-8")
