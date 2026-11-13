import json
import math
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path


@dataclass(frozen=True)
class FareConfig:
    fare_prices: dict[int, float]
    passenger_discounts: dict[str, float]


def parse_fare_config(content: str) -> FareConfig:
    """Convert JSON text into a validated fare configuration."""
    try:
        data = json.loads(content)

        if not isinstance(data, dict):
            raise ValueError("Configuration must be a JSON object.")

        prices = data["fare_prices"]
        discounts = data["passenger_discounts"]

        if not isinstance(prices, dict) or not isinstance(discounts, dict):
            raise ValueError("Prices and discounts must be objects.")

        if set(prices) != {"1", "2", "3"}:
            raise ValueError("Fare prices must define zones 1, 2 and 3.")

        fare_prices = {}
        for zone, price in prices.items():
            if type(price) not in (int, float):
                raise ValueError("Fare prices must be numbers.")
            if not math.isfinite(price) or price <= 0:
                raise ValueError("Fare prices must be positive and finite.")
            fare_prices[int(zone)] = float(price)

        required_passengers = {"adult", "child", "student", "senior"}

        if set(discounts) != required_passengers:
            raise ValueError("Invalid passenger discount configuration.")

        passenger_discounts = {}
        for passenger, discount in discounts.items():
            if type(discount) not in (int, float):
                raise ValueError("Discounts must be numbers.")
            if not math.isfinite(discount) or not 0 <= discount <= 1:
                raise ValueError("Discounts must be between 0 and 1.")
            passenger_discounts[passenger] = float(discount)

        return FareConfig(fare_prices, passenger_discounts)

    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise ValueError(f"Invalid fare configuration: {error}") from error


def load_fare_config(path: Path | None = None) -> FareConfig:
    """Read fare configuration from the default or a custom JSON file."""
    if path is None:
        content = files("public_transport_fares").joinpath("fares.json").read_text(encoding="utf-8")
    else:
        content = path.read_text(encoding="utf-8")

    return parse_fare_config(content)
