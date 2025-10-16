import os
from typing import Optional
import requests

API_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str = "Moscow") -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not api_key:
        return "OpenWeather API key is not configured."
    try:
        resp = requests.get(
            API_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=15,
        )
        if resp.status_code == 401:
            return "OpenWeather API key is invalid."
        resp.raise_for_status()
        data = resp.json()
        name = data.get("name", city)
        main = data.get("weather", [{}])[0].get("description", "N/A").capitalize()
        temp = data.get("main", {}).get("temp", "?")
        feels = data.get("main", {}).get("feels_like", "?")
        humidity = data.get("main", {}).get("humidity", "?")
        wind = data.get("wind", {}).get("speed", "?")
        return f"Weather in {name}: {main}. Temp {temp}°C (feels {feels}°C), humidity {humidity}%, wind {wind} m/s."
    except requests.Timeout:
        return "Weather service timed out."
    except requests.RequestException as e:
        return f"Weather service error: {e}"
