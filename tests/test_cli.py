from typer.testing import CliRunner

from public_transport_fares.cli import app

runner = CliRunner()


def test_calculate_uses_adult_by_default() -> None:
    result = runner.invoke(app, ["calculate", "Catalunya", "Terrassa"])

    assert result.exit_code == 0
    assert "Catalunya" in result.stdout
    assert "Terrassa" in result.stdout
    assert "4.50" in result.stdout


def test_calculate_accepts_passenger_option() -> None:
    result = runner.invoke(
        app,
        ["calculate", "Catalunya", "Terrassa", "--passenger", "child"],
    )

    assert result.exit_code == 0
    assert "child" in result.stdout


def test_calculate_rejects_invalid_passenger() -> None:
    result = runner.invoke(
        app,
        ["calculate", "Catalunya", "Terrassa", "--passenger", "dog"],
    )

    assert result.exit_code == 1
    assert "unknown passenger type" in result.stderr
