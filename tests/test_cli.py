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
