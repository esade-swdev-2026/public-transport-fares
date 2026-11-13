import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from public_transport_fares.cli import app

runner = CliRunner()


@pytest.fixture
def custom_fares_file(tmp_path: Path) -> Path:
    config_file = tmp_path / "custom-fares.json"
    config_file.write_text(
        json.dumps(
            {
                "fare_prices": {
                    "1": 3.0,
                    "2": 4.0,
                    "3": 5.0,
                },
                "passenger_discounts": {
                    "adult": 0.0,
                    "child": 0.5,
                    "student": 0.3,
                    "senior": 0.4,
                },
            }
        ),
        encoding="utf-8",
    )
    return config_file


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
def test_calculate_applies_passenger_discount(
    passenger: str,
    expected_price: str,
) -> None:
    result = runner.invoke(
        app,
        ["calculate", "Catalunya", "Terrassa", "--passenger", passenger],
    )

    assert result.exit_code == 0
    assert expected_price in result.stdout


def test_stations_lists_every_station_with_its_zone() -> None:
    result = runner.invoke(app, ["stations"])

    assert result.exit_code == 0
    assert "Catalunya" in result.stdout
    assert "Sant Cugat" in result.stdout
    assert "Terrassa             Zone 3" in result.stdout
    assert len(result.stdout.strip().splitlines()) == 7


def test_stations_are_listed_alphabetically_by_name() -> None:
    result = runner.invoke(app, ["stations"])

    listed_names = [line.split("Zone")[0].strip() for line in result.stdout.strip().splitlines()]

    assert listed_names == sorted(listed_names)


def test_each_listed_station_name_can_be_used_to_calculate_a_fare() -> None:
    stations_result = runner.invoke(app, ["stations"])

    listed_names = [
        line.split("Zone")[0].strip() for line in stations_result.stdout.strip().splitlines()
    ]

    for name in listed_names:
        calculate_result = runner.invoke(app, ["calculate", name, name])

        assert calculate_result.exit_code == 0


def test_calculate_with_ten_trip_ticket() -> None:
    result = runner.invoke(
        app,
        ["calculate", "Catalunya", "Terrassa", "--ticket", "10-trip"],
    )

    assert result.exit_code == 0
    assert "36.00 €" in result.stdout


def test_calculate_rejects_invalid_ticket() -> None:
    result = runner.invoke(
        app,
        ["calculate", "Catalunya", "Terrassa", "--ticket", "weekly"],
    )

    assert result.exit_code == 1
    assert "Invalid ticket type" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_displays_ticket_type() -> None:
    result = runner.invoke(
        app,
        ["calculate", "Catalunya", "Terrassa", "--ticket", "monthly"],
    )

    assert result.exit_code == 0
    assert "ticket type monthly" in result.stdout
    assert "72.00 €" in result.stdout


def test_recommend_single_ticket() -> None:
    result = runner.invoke(
        app,
        ["recommend", "Catalunya", "Sagrada Familia", "--journeys", "5"],
    )

    assert result.exit_code == 0
    assert "Recommended ticket: single" in result.output
    assert "Total cost: 12.50 €" in result.output


def test_recommend_ten_trip_ticket() -> None:
    result = runner.invoke(
        app,
        ["recommend", "Catalunya", "Sant Cugat", "--journeys", "10"],
    )

    assert result.exit_code == 0
    assert "Recommended ticket: 10-trip" in result.output
    assert "Total cost: 28.00 €" in result.output


def test_recommend_monthly_ticket() -> None:
    result = runner.invoke(
        app,
        ["recommend", "Catalunya", "Terrassa", "--journeys", "30"],
    )

    assert result.exit_code == 0
    assert "Recommended ticket: monthly" in result.output
    assert "Total cost: 72.00 €" in result.output


def test_recommend_negative_journeys() -> None:
    result = runner.invoke(
        app,
        ["recommend", "Catalunya", "Terrassa", "--journeys", "-5"],
    )

    assert result.exit_code == 1
    assert "number of journeys must be greater than zero" in result.output


def test_recommend_unknown_station() -> None:
    result = runner.invoke(
        app,
        ["recommend", "Unknown", "Terrassa", "--journeys", "10"],
    )

    assert result.exit_code == 1
    assert "unknown station" in result.output


def test_recommend_applies_student_discount() -> None:
    result = runner.invoke(
        app,
        [
            "recommend",
            "Catalunya",
            "Terrassa",
            "--journeys",
            "30",
            "--passenger",
            "student",
        ],
    )

    assert result.exit_code == 0
    assert "Recommended ticket: monthly" in result.output
    assert "Passenger type: student" in result.output
    assert "Total cost: 57.60 €" in result.output


def test_recommend_defaults_to_adult_passenger() -> None:
    result = runner.invoke(
        app,
        ["recommend", "Catalunya", "Sagrada Familia", "--journeys", "5"],
    )

    assert result.exit_code == 0
    assert "Passenger type: adult" in result.output
    assert "Total cost: 12.50 €" in result.output


def test_recommend_unknown_passenger_type() -> None:
    result = runner.invoke(
        app,
        [
            "recommend",
            "Catalunya",
            "Terrassa",
            "--journeys",
            "10",
            "--passenger",
            "dog",
        ],
    )

    assert result.exit_code == 1
    assert "unknown passenger type 'dog'" in result.output


def test_calculate_uses_custom_fares(
    custom_fares_file: Path,
) -> None:
    result = runner.invoke(
        app,
        [
            "calculate",
            "Catalunya",
            "Terrassa",
            "--fares",
            str(custom_fares_file),
        ],
    )

    assert result.exit_code == 0
    assert "5.00 €" in result.stdout


def test_calculate_uses_custom_discount(
    custom_fares_file: Path,
) -> None:
    result = runner.invoke(
        app,
        [
            "calculate",
            "Catalunya",
            "Terrassa",
            "--passenger",
            "student",
            "--fares",
            str(custom_fares_file),
        ],
    )

    assert result.exit_code == 0
    assert "3.50 €" in result.stdout


def test_recommend_uses_custom_fares(
    custom_fares_file: Path,
) -> None:
    result = runner.invoke(
        app,
        [
            "recommend",
            "Catalunya",
            "Terrassa",
            "--journeys",
            "5",
            "--fares",
            str(custom_fares_file),
        ],
    )

    assert result.exit_code == 0
    assert "Recommended ticket: single" in result.stdout
    assert "Total cost: 25.00 €" in result.stdout


def test_calculate_rejects_missing_fares_file(
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing.json"

    result = runner.invoke(
        app,
        [
            "calculate",
            "Catalunya",
            "Terrassa",
            "--fares",
            str(missing_file),
        ],
    )

    assert result.exit_code != 0
    assert "Error:" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_rejects_invalid_fares_file(
    tmp_path: Path,
) -> None:
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{invalid json}", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "calculate",
            "Catalunya",
            "Terrassa",
            "--fares",
            str(invalid_file),
        ],
    )

    assert result.exit_code != 0
    assert "Error:" in result.stderr
    assert "Traceback" not in result.stderr
