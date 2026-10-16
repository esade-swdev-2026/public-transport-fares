import pytest
from typer.testing import CliRunner

from public_transport_fares.cli import app

runner = CliRunner()


def test_calculate_rejects_invalid_passenger() -> None:
    result = runner.invoke(
        app,
        ["calculate", "Catalunya", "Terrassa", "--passenger", "dog"],
    )

    assert result.exit_code == 1
    assert "unknown passenger type" in result.stderr


def test_unknown_station_error_message() -> None:
    result = runner.invoke(
        app,
        ["calculate", "Madrid", "Terrassa"],
    )

    assert result.exit_code == 1
    assert "madrid" in result.stderr
    assert "fares stations" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_uses_adult_fare_by_default() -> None:
    result = runner.invoke(app, ["calculate", "Catalunya", "Terrassa"])

    assert result.exit_code == 0
    assert "4.50 €" in result.stdout


@pytest.mark.parametrize(
    ("passenger", "expected_price"),
    [
        ("child", "2.25 €"),
        ("student", "3.60 €"),
        ("senior", "2.70 €"),
    ],
)
def test_calculate_applies_passenger_discount(passenger: str, expected_price: str) -> None:
    result = runner.invoke(app, ["calculate", "Catalunya", "Terrassa", "--passenger", passenger])

    assert result.exit_code == 0
    assert expected_price in result.stdout
