import os
import time
from dotenv import load_dotenv
import requests
from requests.sessions import Session
from getpass import getpass
from dotenv import load_dotenv
import os

BASE_URL = "http://127.0.0.1:5000"
session = Session()


load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather_api_data(location_id):
    """
    Fetch current weather data from OpenWeatherMap.
    """
    try:
        # Get the location coordinates
        response = session.get(f"{BASE_URL}/favorites")
        if response.status_code == 200:
            favorites = response.json()
            location = next((loc for loc in favorites if loc["id"] == location_id), None)
            if not location:
                print(f"\nLocation with ID {location_id} not found.")
                return None
        else:
            print(f"\nFailed to fetch favorites: {response.status_code}")
            return None
        
        # Calling OpenWeatherMap API 3.0
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
            current_time = int(time.time())
            return {
                "current": {
                    "dt": current_time,
                    "temp": data['current']['temp'],
                    "feels_like": data['current']['feels_like'],
                    "pressure": data['current']['pressure'],
                    "humidity": data['current']['humidity'],
                    "wind_speed": data['current']['wind_speed'],
                    "wind_deg": data['current']['wind_deg'],
                    "weather": [
                        {
                            "description": data['current']['weather'][0]['description'],
                            "icon": data['current']['weather'][0]['icon']
                        }
                    ]
                }
            }
        else:
            print(f"\nAPI Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"\nError getting weather: {str(e)}")
        return None

def get_forecast_api_data(location_id):
    """
    Fetch weather forecast data from OpenWeatherMap.
    """
    try:
        response = session.get(f"{BASE_URL}/favorites")
        if response.status_code == 200:
            favorites = response.json()
            location = next((loc for loc in favorites if loc["id"] == location_id), None)
            if not location:
                print(f"\nLocation with ID {location_id} not found.")
                return None
        else:
            print(f"\nFailed to fetch favorites: {response.status_code}")
            return None

        url = "https://api.openweathermap.org/data/3.0/onecall"
        params = {
            "lat": location["latitude"],
            "lon": location["longitude"],
            "exclude": "current,minutely,alerts",
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                "current": {"dt": int(time.time())},
                "daily": data.get('daily', [])
            }
        else:
            print(f"\nFailed to fetch forecast data: {response.status_code}")
            return None

    except Exception as e:
        print(f"\nError getting forecast: {str(e)}")
        return None

def get_history_api_data(location_id):
    """
    Fetch historical weather data from OpenWeatherMap.
    Makes multiple API calls to get data for the last 24 hours.
    """
    try:
        response = session.get(f"{BASE_URL}/favorites")
        if response.status_code == 200:
            favorites = response.json()
            location = next((loc for loc in favorites if loc["id"] == location_id), None)
            if not location:
                print(f"\nLocation with ID {location_id} not found.")
                return None
        else:
            print(f"\nFailed to fetch favorites: {response.status_code}")
            return None

        current_time = int(time.time())
        historical_data = []

        # Make API calls for the last 24 hours in 1-hour intervals
        for hour in range(1, 25):  # 1 to 24 hours ago
            timestamp = current_time - (hour * 3600)  # 3600 seconds = 1 hour
            
            url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
            params = {
                "lat": location["latitude"],
                "lon": location["longitude"],
                "dt": timestamp,
                "appid": API_KEY,
                "units": "metric"
            }

            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    historical_data.append(data['data'][0])
            else:
                print(f"\nFailed to fetch historical data for timestamp {timestamp}: {response.status_code}")

            # Add a small delay between API calls to avoid rate limiting
            time.sleep(0.1)

        if historical_data:
            return {
                "hourly": historical_data
            }
        else:
            print("\nNo historical data retrieved.")
            return None

    except Exception as e:
        print(f"\nError getting history: {str(e)}")
        return None

def register_user(username, password):
    response = session.post(f"{BASE_URL}/register", 
        json={"username": username, "password": password})
    return response.status_code == 200

def login_user(username, password):
    response = session.post(f"{BASE_URL}/login", 
        json={"username": username, "password": password})
    return response.status_code == 200

def get_favorites():
    response = session.get(f"{BASE_URL}/favorites")
    if response.status_code == 200:
        try:
            locations = response.json()
            if not locations:
                print("\nYou don't have any favorite locations yet.\n")
                return True
            
            print("\n=== Your Favorite Locations ===\n")
            for loc in locations:
                if isinstance(loc, dict):
                    print(f"\nID: {loc.get('id', 'N/A')}")
                    print(f"Location: {loc.get('location_name', 'N/A')}")
                    print(f"Coordinates: ({loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')})")
                    print("-------------------\n")
            return True
        except Exception as e:
            print(f"\nError processing favorites: {str(e)}")
            return False
    elif response.status_code == 401:
        print("\nPlease log in first to view your favorites.\n")
        return False
    return False

def add_favorite(location_name, latitude, longitude):
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        response = session.post(f"{BASE_URL}/favorites", 
            json={
                "location_name": location_name,
                "latitude": lat,
                "longitude": lon
            })
        if response.status_code == 401:
            print("\nPlease log in first to add favorites.")
            return False
        return response.status_code == 200
    except ValueError:
        print("\nInvalid coordinates. Please enter valid numbers.")
        return False
    except Exception as e:
        print(f"\nError adding favorite: {str(e)}")
        return False

def remove_favorite(location_id):
    try:
        response = session.delete(f"{BASE_URL}/favorites/{location_id}")
        if response.status_code == 401:
            print("\nPlease log in first to remove favorites.")
            return False
        return response.status_code == 200
    except:
        return False

def get_current_weather(location_id):
    try:
        location_id = int(location_id)
        
        response = session.get(f"{BASE_URL}/weather/current/{location_id}")
        if response.status_code == 200:
            weather = response.json()
            if 'error' not in weather:
                print("\nCurrent Weather:")
                print(f"Temperature: {weather['temperature']}°C")
                print(f"Feels Like: {weather['feels_like']}°C")
                print(f"Description: {weather['description']}")
                print(f"Humidity: {weather['humidity']}%")
                print(f"Wind Speed: {weather['wind_speed']} m/s")
                return True
            else:
                # Get fresh weather data from API
                weather_data = get_weather_api_data(location_id)
                if weather_data:
                    # Store the new weather data
                    store_response = session.post(
                        f"{BASE_URL}/weather/current/{location_id}", 
                        json=weather_data
                    )
                    if store_response.status_code == 200:
                        # Re-fetch the stored weather data
                        fetch_response = session.get(f"{BASE_URL}/weather/current/{location_id}")
                        if fetch_response.status_code == 200:
                            stored_weather = fetch_response.json()
                            print("\nCurrent Weather:")
                            print(f"Temperature: {stored_weather['temperature']}°C")
                            print(f"Feels Like: {stored_weather['feels_like']}°C")
                            print(f"Description: {stored_weather['description']}")
                            print(f"Humidity: {stored_weather['humidity']}%")
                            print(f"Wind Speed: {stored_weather['wind_speed']} m/s")
                            return True
                        else:
                            print(f"\nFailed to fetch stored weather data: {fetch_response.status_code}")
                    else:
                        print(f"\nFailed to store weather data: {store_response.status_code}")
                return False
        return False
    except Exception as e:
        print(f"\nError getting weather: {str(e)}")
        return False

def get_weather_forecast(location_id):
    try:
        location_id = int(location_id)
        
        response = session.get(f"{BASE_URL}/weather/forecast/{location_id}")
        if response.status_code == 200:
            forecasts = response.json()
            if forecasts and not isinstance(forecasts, dict):
                print("\nWeather Forecast:")
                for forecast in forecasts:
                    print(f"\nDate: {time.strftime('%Y-%m-%d', time.localtime(forecast['forecast_timestamp']))}")
                    print(f"Temperature: {forecast['temperature']}°C")
                    print(f"Description: {forecast['description']}")
                    print("-------------------")
                return True
            else:
                # Get fresh forecast data from API
                forecast_data = get_forecast_api_data(location_id)  
                if forecast_data:
                    # Store the new forecast data
                    store_response = session.post(f"{BASE_URL}/weather/forecast/{location_id}", 
                                          json=forecast_data)
                    if store_response.status_code == 200:
                        # Re-fetch the stored forecast data
                        fetch_response = session.get(f"{BASE_URL}/weather/forecast/{location_id}")
                        if fetch_response.status_code == 200:
                            stored_forecasts = fetch_response.json()
                            print("\nWeather Forecast:")
                            for forecast in stored_forecasts:
                                print(f"\nDate: {time.strftime('%Y-%m-%d', time.localtime(forecast['forecast_timestamp']))}")
                                print(f"Temperature: {forecast['temperature']}°C")
                                print(f"Description: {forecast['description']}")
                                print("-------------------")
                            return True
                    return False
                return False
        return False
    except ValueError:
        print("\nInvalid location ID. Please enter a valid number.")
        return False
    except Exception as e:
        print(f"\nError getting forecast: {str(e)}")
        return False

def get_weather_history(location_id):
    try:
        location_id = int(location_id)
        
        response = session.get(f"{BASE_URL}/weather/history/{location_id}")
        if response.status_code == 200:
            history = response.json()
            if history and not isinstance(history, dict):
                print("\nWeather History (Last 24 Hours):")
                for record in history:
                    print(f"\nTime: {time.strftime('%Y-%m-%d %H:%M', time.localtime(record['timestamp']))}")
                    print(f"Temperature: {record['temperature']}°C")
                    print(f"Description: {record['description']}")
                    print("-------------------")
                return True
            else:
                # Get fresh history data from API
                history_data = get_history_api_data(location_id)
                if history_data and 'hourly' in history_data:
                    # Store the new history data
                    store_response = session.post(f"{BASE_URL}/weather/history/{location_id}", 
                                          json=history_data)
                    if store_response.status_code == 200:
                        # Re-fetch the stored history data
                        fetch_response = session.get(f"{BASE_URL}/weather/history/{location_id}")
                        if fetch_response.status_code == 200:
                            stored_history = fetch_response.json()
                            print("\nWeather History (Last 24 Hours):")
                            for record in stored_history:
                                print(f"\nTime: {time.strftime('%Y-%m-%d %H:%M', time.localtime(record['timestamp']))}")
                                print(f"Temperature: {record['temperature']}°C")
                                print(f"Description: {record['description']}")
                                print("-------------------")
                            return True
                    return False
                return False
        return False
    except ValueError:
        print("\nInvalid location ID. Please enter a valid number.")
        return False
    except Exception as e:
        print(f"\nError getting history: {str(e)}")
        return False

def main():
    username = ""
    password = ""
    
    print("\nWelcome to your Weather-Location Manager.\n")
    print("Would you like to Login or Create an Account?\n")
    
    while True:
        print("Menu:")
        print(" 1. Login")
        print(" 2. Create Account")
        print(" 3. Exit")
        userInput = input("Enter the number of the action you would like to perform: ")

        if userInput == "1":
            username = input("\nUsername: ")
            password = getpass("Password: ")
            
            if login_user(username, password):
                print(f"\n\nWelcome, {username}. What would you like to do?\n")
                break
            else:
                print("\nUsername or Password incorrect. Please try again.\n")

        elif userInput == "2":
            print("\nEnter a username and password to create an account.\n")
            username = input("Username: ")
            password = getpass("Password: ")
            
            if register_user(username, password):
                print(f"\n\nAccount created. Welcome, {username}. What would you like to do?\n")
                if login_user(username, password): 
                    break
            else:
                print("\nFailed to create account. Username may already exist.\n")

        elif userInput == "3":
            print("\nExiting...")
            time.sleep(1)
            quit()
        
        else:
            print("\nInvalid input. Please try again.")

    while True:
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
            print("\nGetting All Favorite Locations...\n")
            get_favorites()
            continue

        elif userInput == "3":
            print("\nHere are your current locations:\n")
            if get_favorites():
                location_id = input("\nEnter the ID number of the location: ")
                get_current_weather(location_id)
            continue

        elif userInput == "4":
            print("\nHere are your current locations:\n")
            if get_favorites():
                location_id = input("\nEnter the ID number of the location: ")
                get_weather_history(location_id)
            continue

        elif userInput == "5":
            print("\nHere are your current locations:\n")
            if get_favorites():
                location_id = input("\nEnter the ID number of the location: ")
                get_weather_forecast(location_id)
            continue

        elif userInput == "6":
            print("\nHere are your current locations:\n")
            if get_favorites():  
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
