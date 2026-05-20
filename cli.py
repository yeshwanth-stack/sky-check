import argparse
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from weather_api import fetch_weather

console = Console()

WMO_DESCRIPTIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 99: "Thunderstorm with hail",
}


def build_table(weather: dict) -> Table:
    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    table.add_column("Field", style="bold cyan", min_width=20)
    table.add_column("Value", style="white")

    condition = WMO_DESCRIPTIONS.get(weather["weather_code"], "Unknown")

    table.add_row("Location", weather["city"])
    table.add_row("Temperature", f"[bold yellow]{weather['temperature_c']} °C[/bold yellow]")
    table.add_row("Wind Speed", f"{weather['wind_speed_kmh']} km/h")
    table.add_row("Humidity", f"{weather['humidity_pct']} %")
    table.add_row("Condition", condition)
    return table


async def main():
    parser = argparse.ArgumentParser(
        prog="sky-check",
        description="Fetch current weather for any city using Open-Meteo.",
    )
    parser.add_argument("--city", required=True, help="City name to look up (e.g. 'London')")
    args = parser.parse_args()

    with console.status(f"[bold green]Fetching weather for {args.city}…"):
        try:
            weather = await fetch_weather(args.city)
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise SystemExit(1)
        except Exception as e:
            console.print(f"[bold red]Request failed:[/bold red] {e}")
            raise SystemExit(1)

    table = build_table(weather)
    console.print(Panel(table, title="[bold blue]Sky Check[/bold blue]", border_style="blue"))


if __name__ == "__main__":
    asyncio.run(main())
