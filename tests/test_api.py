import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from weather_api import fetch_weather, get_coordinates, get_weather
from cli import build_table

GEO_RESPONSE = {
    "results": [{"latitude": 40.71427, "longitude": -74.00597, "name": "New York"}]
}

FORECAST_RESPONSE = {
    "current_weather": {
        "temperature": 22.5,
        "windspeed": 15.3,
        "weathercode": 1,
    },
    "hourly": {
        "relative_humidity_2m": [55]
    },
}


def make_mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status_code
    mock.json.return_value = json_data
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        mock.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock
        )
    return mock


# --- Success case ---

async def test_fetch_weather_success():
    geo_mock = make_mock_response(GEO_RESPONSE)
    forecast_mock = make_mock_response(FORECAST_RESPONSE)

    with patch("weather_api.httpx.AsyncClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.get = AsyncMock(side_effect=[geo_mock, forecast_mock])

        result = await fetch_weather("New York")

    assert result["city"] == "New York"
    assert result["temperature_c"] == 22.5
    assert result["wind_speed_kmh"] == 15.3
    assert result["weather_code"] == 1
    assert result["humidity_pct"] == 55


# --- Invalid city case ---

async def test_fetch_weather_invalid_city():
    geo_mock = make_mock_response({"results": []})

    with patch("weather_api.httpx.AsyncClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.get = AsyncMock(return_value=geo_mock)

        with pytest.raises(ValueError, match="not found"):
            await fetch_weather("ZZZNotARealCity999")


# --- Network error case ---

async def test_fetch_weather_network_error():
    with patch("weather_api.httpx.AsyncClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.get = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

        with pytest.raises(httpx.ConnectError):
            await fetch_weather("London")


# --- HTTP error from forecast endpoint ---

async def test_fetch_weather_http_error_on_forecast():
    geo_mock = make_mock_response(GEO_RESPONSE)
    forecast_mock = make_mock_response({}, status_code=500)

    with patch("weather_api.httpx.AsyncClient") as MockClient:
        instance = MockClient.return_value.__aenter__.return_value
        instance.get = AsyncMock(side_effect=[geo_mock, forecast_mock])

        with pytest.raises(httpx.HTTPStatusError):
            await fetch_weather("New York")


# --- --unit F flag: Fahrenheit conversion ---

def test_build_table_celsius():
    weather = {"city": "Tokyo", "temperature_c": 20.0, "wind_speed_kmh": 5.0, "weather_code": 0, "humidity_pct": 60}
    table = build_table(weather, unit="C")
    cell = table.columns[1]._cells[1]  # Temperature row value
    assert "°C" in cell
    assert "20.0" in cell

def test_build_table_fahrenheit_conversion():
    weather = {"city": "Tokyo", "temperature_c": 0.0, "wind_speed_kmh": 5.0, "weather_code": 0, "humidity_pct": 60}
    table = build_table(weather, unit="F")
    cell = table.columns[1]._cells[1]  # Temperature row value
    assert "°F" in cell
    assert "32.0" in cell  # 0°C == 32°F

def test_build_table_fahrenheit_negative():
    weather = {"city": "Reykjavik", "temperature_c": -10.0, "wind_speed_kmh": 20.0, "weather_code": 71, "humidity_pct": 80}
    table = build_table(weather, unit="F")
    cell = table.columns[1]._cells[1]
    assert "14.0" in cell  # -10°C == 14°F

# --- get_coordinates parses correctly ---

async def test_get_coordinates_returns_correct_values():
    mock_response = make_mock_response(GEO_RESPONSE)
    async with httpx.AsyncClient() as client:
        with patch.object(client, "get", AsyncMock(return_value=mock_response)):
            lat, lon, name = await get_coordinates(client, "New York")

    assert lat == 40.71427
    assert lon == -74.00597
    assert name == "New York"
