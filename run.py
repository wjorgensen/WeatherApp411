import time
import requests
from requests.sessions import Session
from getpass import getpass
from weather_api import get_weather_api_data, get_forecast_api_data, get_history_api_data

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
                print(f"Location with ID {location_id} not found.")
                return None
        else:
            print(f"Failed to fetch favorites: {response.status_code}")
            return None
        
        # Debug logging
        print("\nAPI Request Details:")
        print(f"Location ID: {location_id}")
        print(f"Coordinates: ({location['latitude']}, {location['longitude']})")
        print(f"API Key present: {'Yes' if API_KEY else 'No'}")
        if API_KEY:
            print(f"API Key length: {len(API_KEY)}")
        
        # Calling OpenWeatherMap API 3.0
        url = "https://api.openweathermap.org/data/3.0/onecall"
        params = {
            "lat": location["latitude"],
            "lon": location["longitude"],
            "exclude": "minutely,hourly,daily,alerts",
            "appid": API_KEY,
            "units": "metric"
        }
        
        print("\nMaking API request with parameters:")
        print(f"URL: {url}")
        print(f"Latitude: {params['lat']}")
        print(f"Longitude: {params['lon']}")
        
        response = requests.get(url, params=params)
        print(f"\nResponse Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("\nAPI Error Details:")
            print(f"Status Code: {response.status_code}")
            try:
                error_json = response.json()
                print(f"Error Response: {error_json}")
            except:
                print(f"Raw Response: {response.text}")
            print(f"Full URL: {response.url}")
            return None
            
    except Exception as e:
        print(f"\nError getting weather: {str(e)}")
        return None

def get_forecast_api_data(location_id):
    """
    Fetch weather forecast data from OpenWeatherMap.
    """
    # Get location coordinates (existing code)
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

    # Calling OpenWeatherMap API 3.0
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "exclude": "current,minutely,alerts",  # Only get hourly and daily
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "dt": period.get('dt'),
                "temperature": period.get('temp'),
                "feels_like": period.get('feels_like'),
                "pressure": period.get('pressure'),
                "humidity": period.get('humidity'),
                "wind_speed": period.get('wind_speed'),
                "wind_deg": period.get('wind_deg'),
                "description": period.get('weather', [{}])[0].get('description'),
                "icon": period.get('weather', [{}])[0].get('icon')
            }
            for period in data.get('daily', [])
        ]
    else:
        print(f"Failed to fetch forecast data: {response.status_code}")
        if response.status_code == 401:
            print("Invalid API key or unauthorized access. Please check your OpenWeather API key.")
        return None

def get_history_api_data(location_id):
    """
    Fetch historical weather data from OpenWeatherMap.
    """
    # Get location coordinates (existing code)
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

    # Calling OpenWeatherMap API 3.0
    url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
    params = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "dt": int(time.time()) - 86400,  # 24 hours ago
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "timestamp": hour.get('dt'),
                "temperature": hour.get('temp'),
                "feels_like": hour.get('feels_like'),
                "pressure": hour.get('pressure'),
                "humidity": hour.get('humidity'),
                "wind_speed": hour.get('wind_speed'),
                "wind_deg": hour.get('wind_deg'),
                "description": hour.get('weather', [{}])[0].get('description'),
                "icon": hour.get('weather', [{}])[0].get('icon')
            }
            for hour in data.get('data', [])
        ]
    else:
        print(f"Failed to fetch historical data: {response.status_code}")
        if response.status_code == 401:
            print("Invalid API key or unauthorized access. Please check your OpenWeather API key.")
        return None

def register_user(username, password):
    """
    Register a new user with the application.
    
    Args:
        username (str): Desired username for new account
        password (str): Password for new account
    
    Returns:
        bool: True if registration successful, False otherwise
    
    Side-effects:
        - Makes HTTP POST request to register endpoint
    """
    response = session.post(f"{BASE_URL}/register", 
        json={"username": username, "password": password})
    return response.status_code == 200

def login_user(username, password):
    """
    Log in an existing user.
    
    Args:
        username (str): User's username
        password (str): User's password
    
    Returns:
        bool: True if login successful, False otherwise
    
    Side-effects:
        - Makes HTTP POST request to login endpoint
        - Establishes session if successful
    """
    response = session.post(f"{BASE_URL}/login", 
        json={"username": username, "password": password})
    return response.status_code == 200

def get_favorites(show_weather=False):
    """
    Retrieve user's favorite locations.
    
    Args:
        show_weather (bool): Whether to display current weather for each location
    
    Returns:
        bool: True if favorites retrieved successfully, False otherwise
    
    Side-effects:
        - Makes HTTP GET request to favorites endpoint
        - Prints location information to console
        - Prints weather information if show_weather is True
    """
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
    """
    Add a new favorite location for the current user.
    
    Args:
        location_name (str): Name of the location
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
    
    Returns:
        bool: True if location added successfully, False otherwise
    
    Side-effects:
        - Makes HTTP POST request to favorites endpoint
        - Prints error message if not logged in
    """
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
        return response.status_code == 200
    except:
        return False

def remove_favorite(location_id):
    """
    Remove a favorite location for the current user.
    
    Args:
        location_id (int): ID of the favorite location to remove
    
    Returns:
        bool: True if location removed successfully, False otherwise
    
    Side-effects:
        - Makes HTTP DELETE request to favorites endpoint
        - Prints error message if not logged in
    """
    try:
        response = session.delete(f"{BASE_URL}/favorites/{location_id}")
        if response.status_code == 401:
            print("Please log in first to remove favorites.")
            return False
        return response.status_code == 200
    except:
        return False

def get_current_weather(location_id):
    """
    Get current weather for a favorite location.
    """
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
                        # Display the weather data
                        print("\nCurrent Weather:")
                        print(f"Temperature: {weather_data['temp']}°C")
                        print(f"Feels Like: {weather_data['feels_like']}°C")
                        print(f"Description: {weather_data['weather'][0]['description']}")
                        print(f"Humidity: {weather_data['humidity']}%")
                        print(f"Wind Speed: {weather_data['wind_speed']} m/s")
                        return True
                    else:
                        print(f"\nFailed to store weather data: {store_response.status_code}")
                return False
        return False
    except Exception as e:
        print(f"\nError getting weather: {str(e)}")
        return False

def get_weather_forecast(location_id):
    """
    Get weather forecast for a favorite location.
    
    Args:
        location_id (int): ID of the favorite location
    
    Returns:
        bool: True if forecast data retrieved and displayed successfully,
              False otherwise
    
    Side-effects:
        - Makes HTTP GET request to forecast endpoint
        - Makes API call to OpenWeatherMap if local data not available
        - Prints forecast information to console
    """
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
                    return response.status_code == 200
                return False
        return False
    except Exception as e:
        print(f"\nError getting forecast: {str(e)}")
        return False

def get_weather_history(location_id):
    """
    Get weather history for a favorite location.
    
    Args:
        location_id (int): ID of the favorite location
    
    Returns:
        bool: True if historical data retrieved and displayed successfully,
              False otherwise
    
    Side-effects:
        - Makes HTTP GET request to history endpoint
        - Makes API call to OpenWeatherMap if local data not available
        - Prints historical weather information to console
    """
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
                    return response.status_code == 200
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

