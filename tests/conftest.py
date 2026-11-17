import pytest


@pytest.fixture(autouse=True)
def off_peak_time(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fix the journey time at midday so tests do not depend on the clock."""
    monkeypatch.setenv("FARES_TIME", "12:00")
