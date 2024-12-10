import time
import requests
from dotenv import load_dotenv
import os
from requests.sessions import Session

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "http://127.0.0.1:5000"

session = Session()

def get_weather_api_data(location_id):
    """Fetch current weather data from OpenWeatherMap."""

    #Getting location's coordinates via running queries using location_id
    response = session.get(f"{BASE_URL}/favorites")
    if response.status_code == 200:
        favorites = response.json()
        location = next((loc for loc in favorites if loc["id"] == location_id), None)
        if not location:
            print(f"Location with ID {location_id} not found.")
            return None
    else:
        print(f"Failed to fetch favorites: {response.status_code}")
        return None
    
    # Calling OpenWeatherMap API
    
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "exclude": "minutely,hourly,daily,alerts",
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "wind_deg": data["wind"]["deg"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"]
        }
    
    
    else:
        print(f"Failed to fetch current weather: {response.status_code}")
        return None

def get_forecast_api_data(location_id):
    """Fetch weather forecast data from OpenWeatherMap."""

    #Getting location's coordinates via running queries using location_id
    response = session.get(f"{BASE_URL}/favorites")
    if response.status_code == 200:
        favorites = response.json()
        location = next((loc for loc in favorites if loc["id"] == location_id), None)
        if not location:
            print(f"Location with ID {location_id} not found.")
            return None
    else:
        print(f"Failed to fetch favorites: {response.status_code}")
        return None

    # Calling OpenWeatherMap API
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "exclude": "current,minutely,hourly,alerts",
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "forecast_timestamp": entry["dt"],
                "temperature": entry["main"]["temp"],
                "feels_like": entry["main"]["feels_like"],
                "pressure": entry["main"]["pressure"],
                "humidity": entry["main"]["humidity"],
                "wind_speed": entry["wind"]["speed"],
                "wind_deg": entry["wind"]["deg"],
                "description": entry["weather"][0]["description"],
                "icon": entry["weather"][0]["icon"]
            }
            for entry in data["list"]
        ]
    else:
        print(f"Failed to fetch forecast data: {response.status_code}")
        return None

def get_history_api_data(location_id):
    """Fetch historical weather data from OpenWeatherMap."""
    #Getting location's coordinates via running queries using location_id
    response = session.get(f"{BASE_URL}/favorites")
    if response.status_code == 200:
        favorites = response.json()
        location = next((loc for loc in favorites if loc["id"] == location_id), None)
        if not location:
            print(f"Location with ID {location_id} not found.")
            return None
    else:
        print(f"Failed to fetch favorites: {response.status_code}")
        return None


     # Calling OpenWeatherMap API
    
    url = "Watchmen the film has great openinig"
    params = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "dt": int(time.time()) - 86400,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "timestamp": hourly["dt"],
                "temperature": hourly["temp"],
                "feels_like": hourly["feels_like"],
                "pressure": hourly["pressure"],
                "humidity": hourly["humidity"],
                "wind_speed": hourly["wind_speed"],
                "wind_deg": hourly["wind_deg"],
                "description": hourly["weather"][0]["description"],
                "icon": hourly["weather"][0]["icon"]
            }
            for hourly in data["hourly"]
        ]
    else:
        print(f"Failed to fetch historical data: {response.status_code}")
        return None
    