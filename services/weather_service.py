"""
Weather Service for Disaster Intelligence Platform.
Implements modular WeatherProvider with RealWeatherProvider (Open-Meteo live API)
and MockWeatherProvider (deterministic location-aware fallback).
"""
import json
import urllib.request
import urllib.error
from typing import Dict, Any


class WeatherProvider:
    """Base weather provider interface."""
    def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        raise NotImplementedError


class RealWeatherProvider(WeatherProvider):
    """Fetches real-time global weather from Open-Meteo REST API (no API key required)."""

    def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,wind_speed_10m&"
            f"daily=precipitation_sum,precipitation_probability_max&"
            f"timezone=auto"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "DisasterAI-Platform/2.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode("utf-8"))

        current = data.get("current", {})
        daily = data.get("daily", {})

        precip_sums = daily.get("precipitation_sum", [10.0, 15.0])
        forecast_24h = float(precip_sums[0]) if len(precip_sums) > 0 else 12.0
        forecast_48h = float(precip_sums[1]) if len(precip_sums) > 1 else 18.0

        temp = current.get("temperature_2m", 28.0)
        humidity = current.get("relative_humidity_2m", 85)
        wind = current.get("wind_speed_10m", 15.0)
        cur_precip = current.get("precipitation", 0.0)
        w_code = current.get("weather_code", 3)

        # Map WMO weather codes to descriptive human conditions
        if w_code in [65, 67, 82, 95, 96, 99]:
            condition = "Violent Heavy Monsoon Storm / Torrential Rain"
        elif w_code in [61, 63, 80, 81]:
            condition = "Moderate to Heavy Monsoon Rain"
        elif w_code in [51, 53, 55, 60]:
            condition = "Light Rain / Intermittent Showers"
        elif w_code in [1, 2, 3]:
            condition = "Overcast & Threatening Monsoon Cloud"
        else:
            condition = "Cloudy / Humid Atmospheric Pressure"

        return {
            "temperature_c": round(float(temp), 1),
            "humidity_pct": int(humidity),
            "wind_speed_kmh": round(float(wind), 1),
            "current_precipitation_mm": round(float(cur_precip), 1),
            "weather_condition": condition,
            "forecast_24h_mm": round(forecast_24h, 1),
            "forecast_48h_mm": round(forecast_48h, 1),
            "source": "🟢 LIVE OPEN-METEO API"
        }


class MockWeatherProvider(WeatherProvider):
    """Deterministic, location-aware simulated weather when offline or network fails."""

    def get_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        # Deterministic variation based on latitude/longitude hash
        seed = int(abs(lat * 1000 + lon * 100)) % 100

        # Coastal/Gangetic coordinates get higher monsoon rainfall
        is_monsoon_belt = (lat > 20.0 and lat < 28.0 and lon > 80.0 and lon < 95.0) or (lat < 14.0 and lon < 77.0)

        if is_monsoon_belt:
            base_rain = 60.0 + (seed * 1.8)  # 60mm - 240mm
            temp = 26.0 + (seed % 5)
            humidity = 85 + (seed % 14)
            condition = "Heavy Monsoon Squall & Active Cloudband"
        else:
            base_rain = 10.0 + (seed * 0.4)  # 10mm - 50mm
            temp = 32.0 + (seed % 8)
            humidity = 55 + (seed % 25)
            condition = "Scattered Monsoon Showers & Overcast"

        return {
            "temperature_c": round(temp, 1),
            "humidity_pct": int(humidity),
            "wind_speed_kmh": round(20.0 + (seed % 25), 1),
            "current_precipitation_mm": round(base_rain / 12.0, 1),
            "weather_condition": condition,
            "forecast_24h_mm": round(base_rain, 1),
            "forecast_48h_mm": round(base_rain * 1.4, 1),
            "source": "⚪ LOCATION-AWARE SIMULATION"
        }


class WeatherService:
    """Main weather service facade."""

    def __init__(self):
        self.real_provider = RealWeatherProvider()
        self.mock_provider = MockWeatherProvider()

    def get_weather_for_location(self, lat: float, lon: float) -> Dict[str, Any]:
        try:
            return self.real_provider.get_weather(lat, lon)
        except Exception:
            # Graceful fallback to deterministic provider
            return self.mock_provider.get_weather(lat, lon)
