import time
import requests
from requests.sessions import Session
from getpass import getpass
# from dotenv import load_dotenv
# import os

BASE_URL = "http://127.0.0.1:5000"
session = Session()


# load_dotenv()

# API_KEY = os.getenv("OPENWEATHER_API_KEY")

# if not API_KEY:
#     raise ValueError("No API key found. Please add OPENWEATHER_API_KEY to your .env file.")


def get_weather_api_data(location_id):
    """Fetch current weather data from OpenWeatherMap."""

    location = {"latitude": 40.7128, "longitude": -74.0060}  
    
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "exclude": "minutely,hourly,daily,alerts",
        "appid": "9030e9dd7faf9eca668c408af9d41125",
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
    location = {"latitude": 40.7128, "longitude": -74.0060}  

    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "exclude": "current,minutely,hourly,alerts",
        "appid": "9030e9dd7faf9eca668c408af9d41125",
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
    location = {"latitude": 40.7128, "longitude": -74.0060}  
    
    url = "Watchmen the film has great openinig"
    params = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "dt": int(time.time()) - 86400,
        "appid": "9030e9dd7faf9eca668c408af9d41125",
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
    
def register_user(username, password):
    response = requests.post(f"{BASE_URL}/register", 
        json={"username": username, "password": password})
    return response.status_code == 201

def login_user(username, password):
    response = session.post(f"{BASE_URL}/login", 
        json={"username": username, "password": password})
    return response.status_code == 200

def get_favorites(show_weather=False):
    response = session.get(f"{BASE_URL}/favorites")
    if response.status_code == 200:
        locations = response.json()
        if not locations:
            print("\nYou don't have any favorite locations yet.\n")
            return True
        
        print("\n=== Your Favorite Locations ===\n")
        for loc in locations:
            print(f"ID: {loc['id']}")
            print(f"Location: {loc['location_name']}")
            print(f"Coordinates: ({loc['latitude']}, {loc['longitude']})")
            if show_weather:
                print("Weather info would appear here")
            print("-------------------\n")
        return True
    elif response.status_code == 401:
        print("\nPlease log in first to view your favorites.\n")
        return False
    return False

def add_favorite(location_name, latitude, longitude):
    try:
        response = session.post(f"{BASE_URL}/favorites", 
            json={
                "location_name": location_name,
                "latitude": float(latitude),
                "longitude": float(longitude)
            })
        if response.status_code == 401:
            print("Please log in first to add favorites.")
            return False
        return response.status_code == 201
    except:
        return False

def remove_favorite(location_id):
    try:
        response = session.delete(f"{BASE_URL}/favorites/{location_id}")
        if response.status_code == 401:
            print("Please log in first to remove favorites.")
            return False
        return response.status_code == 200
    except:
        return False

def get_current_weather(location_id):
    """Get current weather for a favorite location."""
    try:
        response = session.get(f"{BASE_URL}/weather/current/{location_id}")
        if response.status_code == 200:
            weather = response.json()
            if 'error' not in weather:
                print("\nCurrent Weather:")
                print(f"Temperature: {weather['temperature']}°K")
                print(f"Feels Like: {weather['feels_like']}°K")
                print(f"Description: {weather['description']}")
                print(f"Humidity: {weather['humidity']}%")
                print(f"Wind Speed: {weather['wind_speed']} m/s")
                return True
            else:
                weather_data = get_weather_api_data(location_id) 
                if weather_data:
                    response = session.post(f"{BASE_URL}/weather/current/{location_id}", 
                                          json=weather_data)
                    return response.status_code == 201
                return False
        return False
    except Exception as e:
        print(f"\nError getting weather: {str(e)}")
        return False

def get_weather_forecast(location_id):
    """Get weather forecast for a favorite location."""
    try:
        response = session.get(f"{BASE_URL}/weather/forecast/{location_id}")
        if response.status_code == 200:
            forecasts = response.json()
            if forecasts and not isinstance(forecasts, dict):
                print("\nWeather Forecast:")
                for forecast in forecasts:
                    print(f"\nDate: {time.strftime('%Y-%m-%d', time.localtime(forecast['forecast_timestamp']))}")
                    print(f"Temperature: {forecast['temperature']}°K")
                    print(f"Description: {forecast['description']}")
                    print("-------------------")
                return True
            else:
                forecast_data = get_forecast_api_data(location_id)  
                if forecast_data:
                    response = session.post(f"{BASE_URL}/weather/forecast/{location_id}", 
                                          json=forecast_data)
                    return response.status_code == 201
                return False
        return False
    except Exception as e:
        print(f"\nError getting forecast: {str(e)}")
        return False

def get_weather_history(location_id):
    """Get weather history for a favorite location."""
    try:
        response = session.get(f"{BASE_URL}/weather/history/{location_id}")
        if response.status_code == 200:
            history = response.json()
            if history and not isinstance(history, dict):
                print("\nWeather History:")
                for record in history:
                    print(f"\nTime: {time.strftime('%Y-%m-%d %H:%M', time.localtime(record['timestamp']))}")
                    print(f"Temperature: {record['temperature']}°K")
                    print(f"Description: {record['description']}")
                    print("-------------------")
                return True
            else:
                history_data = get_history_api_data(location_id)
                if history_data:
                    response = session.post(f"{BASE_URL}/weather/history/{location_id}", 
                                          json=history_data)
                    return response.status_code == 201
                return False
        return False
    except Exception as e:
        print(f"\nError getting history: {str(e)}")
        return False


def main():
    username = ""
    password = ""
    
    print("\nWelcome to your Weather-Location Manager.\nWould you like to Login or Create an Account?\n")
    
    while (True):
        print("Menu:")
        print(" 1. Login")
        print(" 2. Create Account")
        print(" 3. Exit")
        userInput = input("Enter the number of the action you would like to perform: ")

        if userInput == "1":
            username = input("\nUsername: ")
            password = getpass("Password: ")
            
            if login_user(username, password):
                print(f"\nWelcome, {username}. What would you like to do?\n")
                break
            else:
                print("\nUsername or Password incorrect. Please try again.\n")

        elif userInput == "2":
            print("\nEnter a username and password to create an account.\n")
            username = input("Username: ")
            password = getpass("Password: ")
            
            if register_user(username, password):
                print(f"\nAccount created. Welcome, {username}. What would you like to do?\n")
                if login_user(username, password): 
                    break
            else:
                print("\nFailed to create account. Username may already exist.\n")

        elif userInput == "3":
            print("Exiting...")
            time.sleep(1)
            quit()
        
        else:
            print("Invalid input. Please try again.")




    while (True):
        print("Menu:")
        print(" 1. Set a New Favorite Location")
        print(" 2. View All Favorite Locations")
        print(" 3. Get the Current Weather for a Favorite Location")
        print(" 4. Get Weather History for a Favorite Location")
        print(" 5. Get Weather Forecast for a Favorite Location")
        print(" 6. Remove a Favorite Location")
        print(" 7. Exit and Logout")

        userInput = input("Enter the number of the action you would like to perform: ")
        if userInput == "1":
            location = input("\nEnter the name of the location you'd like to favorite: ")
            latitude = input("Enter the latitude (e.g., 40.7128): ")
            longitude = input("Enter the longitude (e.g., -74.0060): ")
            
            if add_favorite(location, latitude, longitude):
                print("\nLocation added to favorites.\n")
            else:
                print("\nFailed to add location to favorites.\n")
            continue

        elif userInput == "2":
            while True:
                yesNo2 = input("\nWould you like to view the current weather for each location as well? Y/N\nEnter Y or N: ").upper()
                if yesNo2 in ["Y", "N"]:
                    if yesNo2 == "Y":
                        print("\nGetting All Favorite Locations and their Current Weather...\n")
                        get_favorites(show_weather=True)
                        break
                    else:
                        print("\nGetting All Favorite Locations...\n")
                        get_favorites(show_weather=False)
                        break
                else:
                    print("\nInvalid input. Please enter Y or N.\n")
            continue

        elif userInput == "3":
            print("\nHere are your current locations:\n")
            if get_favorites(show_weather=False):
                location_id = input("\nEnter the ID number of the location: ")
                get_current_weather(location_id)
            continue

        elif userInput == "4":
            print("\nHere are your current locations:\n")
            if get_favorites(show_weather=False):
                location_id = input("\nEnter the ID number of the location: ")
                get_weather_history(location_id)
            continue

        elif userInput == "5":
            print("\nHere are your current locations:\n")
            if get_favorites(show_weather=False):
                location_id = input("\nEnter the ID number of the location: ")
                get_weather_forecast(location_id)
            continue

        elif userInput == "6":
            print("\nHere are your current locations:\n")
            if get_favorites(show_weather=False):  
                location_id = input("\nEnter the ID number of the location you would like to remove: ")
                if remove_favorite(location_id):
                    print("\nLocation removed from favorites.\n")
                else:
                    print("\nFailed to remove location. Please make sure you entered a valid ID number.\n")
            continue

        elif userInput == "7":
            print("\nExiting...\n")
            time.sleep(1)
            break

        else:
            print("\nInvalid input. Please try again.\n")

if __name__ == '__main__':
    main()

