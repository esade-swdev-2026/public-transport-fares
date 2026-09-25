import typer

app = typer.Typer(help="Calculate public transport fares between stations.")


@app.callback()
def main() -> None:
    """Public transport fare calculator."""
    pass


@app.command()
def calculate(
    origin: str,
    destination: str,
    passenger: str = "adult",
) -> None:
    """Calculate the fare between two stations."""

    valid_passenger_types = ["adult", "child", "student", "senior"]

    if passenger not in valid_passenger_types:
        typer.echo(
            f"Error: unknown passenger type '{passenger}'.",
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo(f"Calculating fare from {origin} to {destination} for passenger type: {passenger}.")


if __name__ == "__main__":
    app()
