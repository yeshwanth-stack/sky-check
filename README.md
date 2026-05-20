# sky-check

A CLI tool that fetches real-time weather for any city using the [Open-Meteo](https://open-meteo.com/) API — no API key required.

## Features

- Live temperature, wind speed, humidity, and conditions
- Async HTTP requests via `httpx`
- Rich terminal output with styled panels
- Full unit test suite (no network calls)

## Installation

```bash
git clone https://github.com/yeshwanth-stack/sky-check.git
cd sky-check
pip install -r requirements.txt
```

## Usage

```bash
python cli.py --city "London"
python cli.py --city "Tokyo"
python cli.py --city "New York"
```

### Example output

```
+--------------------------------- Sky Check ---------------------------------+
| +----------------------------------+                                        |
| | Location             | New York  |                                        |
| | Temperature          | 30.6 °C   |                                        |
| | Wind Speed           | 19.1 km/h |                                        |
| | Humidity             | 32 %      |                                        |
| | Condition            | Clear sky |                                        |
| +----------------------------------+                                        |
+-----------------------------------------------------------------------------+
```

## Running Tests

```bash
pytest tests/ -v
```

## Dependencies

| Package | Purpose |
|---|---|
| `httpx` | Async HTTP client |
| `rich` | Terminal formatting |
| `pytest` + `pytest-asyncio` | Test suite |
