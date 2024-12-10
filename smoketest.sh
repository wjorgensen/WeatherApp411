#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000" # Adjust the port as necessary

# Cookie jar file
COOKIE_JAR="session_cookies.txt"

# Flag to control whether to echo JSON output
ECHO_JSON=true

# Function to clear database and cookies on exit or error
cleanup() {
    echo "Clearing the database..."
    flask clear-db
    rm -f $COOKIE_JAR
}

# Trap to run cleanup on exit and on receiving the interrupt signal
# trap cleanup EXIT INT

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
    case $1 in
        --echo-json) ECHO_JSON=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done


###############################################
# Health Check
###############################################
check_health() {
    echo "Checking health status..."
    response=$(curl -s -X GET "$BASE_URL/health")
    if echo "$response" | grep -q '"status":"healthy"'; then
        echo "Service is healthy."
    else
        echo "Health check failed: $(echo $response | jq -r '.message')"
        exit 1
    fi
}

###############################################
# Registration and Login
###############################################

register_user() {
    username=$1
    password=$2

    echo "Registering user ($username)..."
    response=$(curl -s -c $COOKIE_JAR -X POST "$BASE_URL/register" -H "Content-Type: application/json" \
        -d "{\"username\":\"$username\", \"password\":\"$password\"}")
    if echo "$response" | grep -q '"message":"User registered successfully"'; then
        echo "User registered successfully."
    else
        echo "Failed to register user: $(echo $response | jq -r '.error')"
        exit 1
    fi
}

login_user() {
    username=$1
    password=$2

    echo "Logging in user ($username)..."
    response=$(curl -s -c $COOKIE_JAR -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
        -d "{\"username\":\"$username\", \"password\":\"$password\"}")
    if echo "$response" | grep -q '"message":"Login successful"'; then
        echo "Login successful."
    else
        echo "Failed to log in: $(echo $response | jq -r '.error')"
        exit 1
    fi
}

logout_user() {
    echo "Logging out user..."
    response=$(curl -s -b $COOKIE_JAR -X POST "$BASE_URL/logout")
    if echo "$response" | grep -q '"message":"Logged out successfully"'; then
        echo "Logged out successfully."
    else
        echo "Failed to log out: $(echo $response | jq -r '.error')"
        exit 1
    fi
}

update_password() {
    current_password=$1
    new_password=$2
    echo "Updating password..."
    response=$(curl -s -b $COOKIE_JAR -X POST "$BASE_URL/update-password" -H "Content-Type: application/json" \
        -d "{\"current_password\":\"$current_password\", \"new_password\":\"$new_password\"}")
    if echo "$response" | grep -q '"message":"Password updated successfully"'; then
        echo "Password updated successfully."
    else
        echo "Failed to update password: $(echo $response | jq -r '.error')"
        exit 1
    fi
}


###############################################
# Favorites Management
###############################################

add_favorite() {
    location_name=$1
    latitude=$2
    longitude=$3

    echo "Adding favorite location ($location_name)..."
    response=$(curl -s -b $COOKIE_JAR -X POST "$BASE_URL/favorites" -H "Content-Type: application/json" \
        -d "{\"location_name\":\"$location_name\", \"latitude\":$latitude, \"longitude\":$longitude}")
    if echo "$response" | grep -q '"message":"Location added successfully"'; then
        echo "Favorite location added successfully."
    else
        echo "Failed to add favorite location: $(echo $response | jq -r '.error')"
        exit 1
    fi
}

get_favorites() {
    echo "Getting favorite locations..."
    response=$(curl -s -b $COOKIE_JAR -X GET "$BASE_URL/favorites")
    if echo "$response" | jq -e '. | length > 0'; then
        echo "Favorite locations retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "$response" | jq .
        fi
    else
        echo "Failed to get favorite locations or no favorites exist."
        exit 1
    fi
}

delete_favorite() {
    favorite_id=$1

    echo "Deleting favorite location (ID: $favorite_id)..."
    response=$(curl -s -b $COOKIE_JAR -X DELETE "$BASE_URL/favorites/$favorite_id")
    if echo "$response" | grep -q '"message":"Location deleted successfully"'; then
        echo "Favorite location deleted successfully."
    else
        echo "Failed to delete favorite location: $(echo $response | jq -r '.error')"
        exit 1
    fi
}

store_current_weather() {
    location_id=$1
    weather_data="$2"
    echo "Storing current weather for location ID: $location_id..."
    response=$(curl -s -b $COOKIE_JAR -X POST "$BASE_URL/weather/current/$location_id" \
              -H "Content-Type: application/json" \
              -d "$weather_data")
    echo $response
    if echo "$response" | grep -q '"message":"Weather data stored successfully"'; then
        echo "Current weather data stored successfully."
    else
        echo "Failed to store current weather data: $(echo $response | jq -r '.error')"
        exit 1
    fi
}

store_weather_forecast() {
    location_id=$1
    forecast_data="$2"
    echo "Storing weather forecast for location ID: $location_id..."
    response=$(curl -s -b $COOKIE_JAR -X POST "$BASE_URL/weather/forecast/$location_id" \
              -H "Content-Type: application/json" \
              -d "$forecast_data")
    echo $response
    if echo "$response" | grep -q '"message":"Forecast data stored successfully"'; then
        echo "Weather forecast data stored successfully."
    else
        echo "Failed to store weather forecast data: $(echo $response | jq -r '.error')"
        exit 1
    fi
}



store_weather_history() {
    location_id=$1
    history_data=$2
    echo "Storing weather history for location ID: $location_id..."
    response=$(curl -s -b $COOKIE_JAR -X POST "$BASE_URL/weather/history/$location_id" -H "Content-Type: application/json" \
        -d "$history_data")
    if echo "$response" | grep -q '"message":"Historical data stored successfully"'; then
        echo "Weather history stored successfully."
    else
        echo "Failed to store weather history: $(echo $response | jq -r '.error')"
        exit 1
    fi
}

get_current_weather() {
    location_id=$1
    echo "Retrieving current weather for location ID: $location_id..."
    response=$(curl -s -b $COOKIE_JAR -X GET "$BASE_URL/weather/current/$location_id")
    if echo "$response" | grep -q '"error"'; then
        echo "Failed to retrieve current weather data: $(echo $response | jq -r '.error')"
        exit 1
    else
        echo "Current weather data retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "$response" | jq .
        fi
    fi
}

get_weather_forecast() {
    location_id=$1
    echo "Retrieving weather forecast for location ID: $location_id..."
    response=$(curl -s -b $COOKIE_JAR -X GET "$BASE_URL/weather/forecast/$location_id")
    if echo "$response" | grep -q '"error"'; then
        echo "Failed to retrieve weather forecast data: $(echo $response | jq -r '.error')"
        exit 1
    else
        echo "Weather forecast data retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "$response" | jq .
        fi
    fi
}

get_weather_history() {
    location_id=$1
    echo "Retrieving weather history for location ID: $location_id..."
    response=$(curl -s -b $COOKIE_JAR -X GET "$BASE_URL/weather/history/$location_id")
    if echo "$response" | grep -q '"error"'; then
        echo "Failed to retrieve weather history data: $(echo $response | jq -r '.error')"
        exit 1
    else
        echo "Weather history data retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "$response" | jq .
        fi
    fi
}

###############################################
# Clear the database
###############################################
echo "Clearing the database..."
rm weather.db
flask init-db
echo "Database cleared successfully and reinitialized."
###############################################
# Execute Tests
###############################################
check_health

###############################################
# simulated response openweather api call for testing purposes
###############################################
# Current weather data
paris_current_weather_data='{
    "current": {
        "dt": 1609502400,
        "temp": 20.5,
        "feels_like": 21.0,
        "pressure": 1013,
        "humidity": 65,
        "wind_speed": 5.2,
        "wind_deg": 180,
        "weather": [{
            "description": "clear sky",
            "icon": "01d"
        }]
    }
}'
#2 days of forecast data
paris_forecast_weather_data='{
    "current": {
        "dt": 1609502400
    },
    "daily": [
        {
            "dt": 1609598800,
            "temp": {"day": 298},
            "feels_like": {"day": 297},
            "pressure": 1015,
            "humidity": 50,
            "wind_speed": 5,
            "wind_deg": 200,
            "weather": [{"description": "partly cloudy", "icon": "03d"}]
        },
        {
            "dt": 1609685200,
            "temp": {"day": 300},
            "feels_like": {"day": 299},
            "pressure": 1016,
            "humidity": 45,
            "wind_speed": 6,
            "wind_deg": 210,
            "weather": [{"description": "sunny", "icon": "01d"}]
        }
    ]
}' 
#3 hours of historical data
paris_historical_weather_data='{
    "hourly": [
        {
            "dt": 1684926000,
            "temp": 292.01,
            "feels_like": 292.33,
            "pressure": 1014,
            "humidity": 91,
            "dew_point": 290.51,
            "wind_speed": 2.58,
            "wind_deg": 86,
            "weather": [
                {
                    "description": "broken clouds",
                    "icon": "04n"
                }
            ],
            "clouds": 54,
            "visibility": 10000
        },
        {
            "dt": 1684933200,
            "temp": 291.55,
            "feels_like": 291.87,
            "pressure": 1013,
            "humidity": 89,
            "dew_point": 289.69,
            "wind_speed": 3.13,
            "wind_deg": 93,
            "weather": [
                {
                    "description": "overcast clouds",
                    "icon": "04d"
                }
            ],
            "clouds": 78,
            "visibility": 10000
        },
        {
            "dt": 1684940400,
            "temp": 293.01,
            "feels_like": 293.33,
            "pressure": 1012,
            "humidity": 85,
            "dew_point": 290.51,
            "wind_speed": 3.58,
            "wind_deg": 90,
            "weather": [
                {
                    "description": "light rain",
                    "icon": "10d"
                }
            ],
            "clouds": 60,
            "visibility": 10000
        }
    ]
}
'

register_user "testuser" "password123"
login_user "testuser" "password123"

add_favorite "Paris" 48.8575 2.3514
add_favorite "New York City" 40.7128 74.0060
get_favorites
store_current_weather 1 "$paris_current_weather_data"
store_weather_forecast 1 "$paris_forecast_weather_data"
store_weather_history 1 "$paris_historical_weather_data"
get_current_weather 1
get_weather_forecast 1
get_weather_history 1
delete_favorite 2
get_favorites
add_favorite "Boston" 42.3601 71.0589
get_favorites
update_password "password123" "newpassword123"
logout_user

login_user "testuser" "newpassword123"
get_favorites
logout_user

echo "All tests passed successfully!"
