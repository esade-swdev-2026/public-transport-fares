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


def test_save_then_spending_shows_the_month_total(tmp_path: Path) -> None:
    journal = str(tmp_path / "journeys.json")
    for origin, destination in [("Catalunya", "Terrassa"), ("Terrassa", "Catalunya")]:
        result = runner.invoke(
            app, ["save", origin, destination, "--date", "2026-11-03", "--journal", journal]
        )
        assert result.exit_code == 0

    result = runner.invoke(app, ["spending", "--month", "2026-11", "--journal", journal])

    assert result.exit_code == 0
    assert "Journeys in 2026-11: 2" in result.stdout
    assert "Total spending: 9.00 €" in result.stdout


def test_save_applies_passenger_discount(tmp_path: Path) -> None:
    journal = str(tmp_path / "journeys.json")

    result = runner.invoke(
        app,
        ["save", "Catalunya", "Terrassa", "--passenger", "student"]
        + ["--date", "2026-11-03", "--journal", journal],
    )

    assert result.exit_code == 0
    assert "3.60 €" in result.stdout


def test_spending_ignores_other_months(tmp_path: Path) -> None:
    journal = str(tmp_path / "journeys.json")
    runner.invoke(
        app, ["save", "Catalunya", "Terrassa", "--date", "2026-10-31", "--journal", journal]
    )

    result = runner.invoke(app, ["spending", "--month", "2026-11", "--journal", journal])

    assert "Journeys in 2026-11: 0" in result.stdout
    assert "Total spending: 0.00 €" in result.stdout


def test_save_rejects_invalid_date(tmp_path: Path) -> None:
    journal = str(tmp_path / "journeys.json")

    result = runner.invoke(
        app, ["save", "Catalunya", "Terrassa", "--date", "03/11/2026", "--journal", journal]
    )

    assert result.exit_code == 1
    assert "Invalid date" in result.stderr


def test_spending_rejects_invalid_month(tmp_path: Path) -> None:
    journal = str(tmp_path / "journeys.json")

    result = runner.invoke(app, ["spending", "--month", "november", "--journal", journal])

    assert result.exit_code == 1
    assert "Invalid month" in result.stderr


def test_spending_rejects_broken_journeys_file(tmp_path: Path) -> None:
    journal = tmp_path / "journeys.json"
    journal.write_text("not json", encoding="utf-8")

    result = runner.invoke(app, ["spending", "--journal", str(journal)])

    assert result.exit_code == 1
    assert "Invalid journeys file" in result.stderr
    assert "Traceback" not in result.stderr


def test_calculate_adds_peak_surcharge_at_peak_time() -> None:
    result = runner.invoke(app, ["calculate", "Catalunya", "Terrassa", "--time", "08:15"])

    assert result.exit_code == 0
    assert "5.40 €" in result.stdout


def test_calculate_combines_peak_surcharge_and_passenger_discount() -> None:
    result = runner.invoke(
        app,
        ["calculate", "Catalunya", "Terrassa", "--time", "08:15", "--passenger", "child"],
    )

    assert result.exit_code == 0
    assert "2.70 €" in result.stdout


def test_calculate_has_no_peak_surcharge_on_monthly_ticket() -> None:
    result = runner.invoke(
        app,
        ["calculate", "Catalunya", "Terrassa", "--time", "08:15", "--ticket", "monthly"],
    )

    assert result.exit_code == 0
    assert "72.00 €" in result.stdout


def test_calculate_rejects_invalid_time() -> None:
    result = runner.invoke(app, ["calculate", "Catalunya", "Terrassa", "--time", "25:99"])

    assert result.exit_code == 1
    assert "Invalid time" in result.stderr
    assert "Traceback" not in result.stderr


def test_save_adds_peak_surcharge_at_peak_time(tmp_path: Path) -> None:
    journal = tmp_path / "journeys.json"

    result = runner.invoke(
        app,
        ["save", "Catalunya", "Terrassa", "--time", "18:00", "--journal", str(journal)],
    )

    assert result.exit_code == 0
    assert "5.40 €" in result.stdout


def test_save_makes_a_connecting_journey_a_free_transfer(tmp_path: Path) -> None:
    journal = str(tmp_path / "journeys.json")
    legs = [
        ("Catalunya", "Sant Cugat", "12:00"),
        ("Sant Cugat", "Terrassa", "12:30"),
        ("Terrassa", "Rubi", "12:50"),
    ]
    outputs = []
    for origin, destination, start in legs:
        result = runner.invoke(
            app,
            ["save", origin, destination, "--time", start]
            + ["--date", "2026-11-17", "--journal", journal],
        )
        assert result.exit_code == 0
        outputs.append(result.stdout)

    assert "3.50 €" in outputs[0]
    assert "0.00 € (free transfer)" in outputs[1]
    assert "3.50 €" in outputs[2]

    result = runner.invoke(app, ["spending", "--month", "2026-11", "--journal", journal])

    assert "Total spending: 7.00 €" in result.stdout


def test_save_rejects_invalid_start_time_in_journal(tmp_path: Path) -> None:
    journal = tmp_path / "journeys.json"
    original = (
        '[{"day": "2026-11-17", "origin": "Catalunya", '
        '"destination": "Sant Cugat", "price": 3.50, "start_time": "25:99"}]'
    )
    journal.write_text(original, encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "save",
            "Sant Cugat",
            "Terrassa",
            "--date",
            "2026-11-17",
            "--time",
            "12:30",
            "--journal",
            str(journal),
        ],
    )

    assert result.exit_code == 1
    assert "Invalid journeys file" in result.stderr
    assert "Invalid time '25:99'" in result.stderr
    assert journal.read_text(encoding="utf-8") == original


@pytest.mark.parametrize(
    ("peak_journeys", "ticket", "total"),
    [
        (0, "single", "17.50"),
        (2, "single", "18.50"),
        (7, "10-trip", "20.00"),
    ],
)
def test_recommend_accounts_for_peak_journeys(peak_journeys: int, ticket: str, total: str) -> None:
    result = runner.invoke(
        app,
        [
            "recommend",
            "Catalunya",
            "Sagrada Familia",
            "--journeys",
            "7",
            f"--peak-journeys={peak_journeys}",
        ],
    )

    assert result.exit_code == 0
    assert f"Recommended ticket: {ticket}" in result.stdout
    assert f"Total cost: {total} €" in result.stdout


@pytest.mark.parametrize("peak_journeys", [-1, 8])
def test_recommend_rejects_peak_journeys_outside_range(peak_journeys: int) -> None:
    result = runner.invoke(
        app,
        [
            "recommend",
            "Catalunya",
            "Sagrada Familia",
            "--journeys",
            "7",
            f"--peak-journeys={peak_journeys}",
        ],
    )

    assert result.exit_code == 1
    assert "Peak journeys must be between 0 and the total number of journeys." in result.stderr


@pytest.mark.parametrize(
    "args",
    [
        ["calculate", "Catalunya", "Terrassa", "--ticket", "weekly"],
        ["calculate", "Catalunya", "Terrassa", "--passenger", "dog"],
        ["calculate", "Madrid", "Terrassa"],
        ["recommend", "Catalunya", "Terrassa", "--journeys", "0"],
        ["spending", "--month", "november"],
    ],
)
def test_every_error_is_one_clear_line_on_stderr(args: list[str]) -> None:
    result = runner.invoke(app, args)

    assert result.exit_code == 1
    assert result.stderr.startswith("Error: ")
    assert result.stdout == ""
    assert "Traceback" not in result.output


def test_unknown_passenger_error_lists_the_valid_types() -> None:
    result = runner.invoke(app, ["calculate", "Catalunya", "Terrassa", "--passenger", "dog"])

    assert result.exit_code == 1
    assert "Options: adult, child, student, senior." in result.stderr
