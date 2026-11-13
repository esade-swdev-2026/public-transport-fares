from pathlib import Path

import pytest

from public_transport_fares.config import load_fare_config, parse_fare_config


@pytest.fixture
def valid_config_json() -> str:
    return """
    {
        "fare_prices": {
            "1": 2.50,
            "2": 3.50,
            "3": 4.50
        },
        "passenger_discounts": {
            "adult": 0.0,
            "child": 0.5,
            "student": 0.2,
            "senior": 0.4
        }
    }
    """


def test_load_default_fares() -> None:
    config = load_fare_config()

    assert config.fare_prices[1] == 2.50
    assert config.fare_prices[3] == 4.50
    assert config.passenger_discounts["student"] == 0.20


def test_parse_valid_config(valid_config_json: str) -> None:
    config = parse_fare_config(valid_config_json)

    assert config.fare_prices == {1: 2.50, 2: 3.50, 3: 4.50}
    assert config.passenger_discounts["child"] == 0.5


def test_parse_custom_fares() -> None:
    content = """
    {
        "fare_prices": {"1": 3.0, "2": 4.0, "3": 5.0},
        "passenger_discounts": {
            "adult": 0.0,
            "child": 0.5,
            "student": 0.2,
            "senior": 0.4
        }
    }
    """

    config = parse_fare_config(content)

    assert config.fare_prices[3] == 5.0


def test_reject_negative_price() -> None:
    content = """
    {
        "fare_prices": {"1": -2.5, "2": 3.5, "3": 4.5},
        "passenger_discounts": {
            "adult": 0.0,
            "child": 0.5,
            "student": 0.2,
            "senior": 0.4
        }
    }
    """

    with pytest.raises(ValueError, match="positive"):
        parse_fare_config(content)


def test_reject_invalid_json() -> None:
    with pytest.raises(ValueError, match="Invalid fare configuration"):
        parse_fare_config("{invalid json}")


def test_reject_missing_price_zones() -> None:
    content = """
    {
        "fare_prices": {"1": 2.5, "2": 3.5},
        "passenger_discounts": {
            "adult": 0.0,
            "child": 0.5,
            "student": 0.2,
            "senior": 0.4
        }
    }
    """

    with pytest.raises(ValueError, match="zones 1, 2 and 3"):
        parse_fare_config(content)


def test_reject_invalid_discount() -> None:
    content = """
    {
        "fare_prices": {"1": 2.5, "2": 3.5, "3": 4.5},
        "passenger_discounts": {
            "adult": 0.0,
            "child": 1.5,
            "student": 0.2,
            "senior": 0.4
        }
    }
    """

    with pytest.raises(ValueError, match="between 0 and 1"):
        parse_fare_config(content)


def test_reject_missing_configuration_file(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_fare_config(missing_file)


def test_load_custom_configuration_file(tmp_path: Path, valid_config_json: str) -> None:
    config_file = tmp_path / "custom-fares.json"
    config_file.write_text(valid_config_json, encoding="utf-8")

    config = load_fare_config(config_file)

    assert config.fare_prices[2] == 3.50
    assert config.passenger_discounts["senior"] == 0.4
