import httpx
import asyncio

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


async def get_coordinates(client: httpx.AsyncClient, city: str) -> tuple[float, float, str]:
    response = await client.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
    )
    response.raise_for_status()
    data = response.json()

    if not data.get("results"):
        raise ValueError(f"City '{city}' not found.")

    result = data["results"][0]
    return result["latitude"], result["longitude"], result["name"]


async def get_weather(client: httpx.AsyncClient, lat: float, lon: float) -> dict:
    response = await client.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "hourly": "relative_humidity_2m",
            "forecast_days": 1,
        },
    )
    response.raise_for_status()
    return response.json()


async def fetch_weather(city: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        lat, lon, resolved_name = await get_coordinates(client, city)
        data = await get_weather(client, lat, lon)

    current = data["current_weather"]
    humidity = data["hourly"]["relative_humidity_2m"][0]

    return {
        "city": resolved_name,
        "temperature_c": current["temperature"],
        "wind_speed_kmh": current["windspeed"],
        "weather_code": current["weathercode"],
        "humidity_pct": humidity,
    }
