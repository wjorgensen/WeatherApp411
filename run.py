import time

username = ""
password = ""

print("Welcome to your Weather-Location Manager. Would you like to Login or Create an Account?")

while (True):
    print("Menu:")
    print(" 1. Login")
    print(" 2. Create Account")
    print(" 3. Exit")
    userInput = input("Enter the number of the action you would like to perform: ")

    if (userInput == "1"):
        username = input("Username: ")
        password = input("Password: ")
        
        
        if (username == "user" and password == "password"):# replace with checking the database for existing username and associated password
            print("Welcome, " + username + ". What would you like to do?")
            break
        else:
            print("Username or Password incorrect. Please try again.")

    elif (userInput == "2"):
        "Enter a username and password to create an account."

        username = input("Username: ")
        password = input("Password: ")
        #function call to register user
        print("Account created. Welcome, " + username + ". What would you like to do?")
        break

    elif (userInput == "3"):
        print("Exiting...")
        time.sleep(1)
        break
    
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
    if (userInput == "1"):
        location = input("Enter the name of the location you'd like to favorite: ")
        #function call
        print("Location added to favorites.")
        continue

    elif (userInput == "2"):
        while (True):
            print("Would you like to view the current weather for each location as well? Y/N")
            yesNo2 = input("Enter Y or N: ")
            if (yesNo2 == "Y"):
                print("Getting All Favorite Locations and their Current Weather...")
                #function call
                break
            elif (yesNo2 == "N"): 
                print("Getting All Favorite Locations...")
                #function call
                break
            else:
                print("Invalid input. Please try again.")
        continue


    elif (userInput == "3"):
        print("Getting the Current Weather for a Favorite Location...")
        #function call
        continue

    elif (userInput == "4"):
        print("Getting Weather History for a Favorite Location...")
        #function call
        continue

    elif (userInput == "5"):
        print("Getting Weather Forecast for a Favorite Location...")
        #function call
        continue

    elif (userInput == "6"):
        location = input("Enter the name of the location you would like to remove: ")
        #function call
        print("Location removed from favorites.")
        continue

    elif (userInput == "7"):
        print("Exiting...")
        time.sleep(1)
        break

    else:
        print("Invalid input. Please try again.")

