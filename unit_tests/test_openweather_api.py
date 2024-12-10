import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
LAT = 42.3601  
LON = -71.0589   #Latitude, Longtitude for Boston hehe

url = "https://api.openweathermap.org/data/3.0/onecall"
params = {
    "lat": LAT,
    "lon": LON,
    "exclude": "minutely,hourly,daily,alerts",
    "units": "metric",
    "appid": API_KEY
}

response = requests.get(url, params=params)

if response.status_code == 200:
    print("API Call Successful!")
    print(response.json()) 
else:
    print(f"Failed API Call. Status Code: {response.status_code}")
    print(response.json())  
