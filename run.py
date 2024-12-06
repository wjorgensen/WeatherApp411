import time
import requests
from requests.sessions import Session
from getpass import getpass

BASE_URL = "http://127.0.0.1:5000"
session = Session()

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
                if login_user(username, password):  # Log them in automatically
                    break
            else:
                print("\nFailed to create account. Username may already exist.\n")

    elif (userInput == "3"):
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
            print("\nGetting the Current Weather for a Favorite Location...\n")
            #function call
            continue

        elif userInput == "4":
            print("\nGetting Weather History for a Favorite Location...\n")
            #function call
            continue

        elif userInput == "5":
            print("\nGetting Weather Forecast for a Favorite Location...\n")
            #function call
            continue

        elif userInput == "6":
            print("\nHere are your current locations:\n")
            if get_favorites(show_weather=False):  # Show all locations first
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

