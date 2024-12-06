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

# User registration and login flow
register_user "testuser" "password123"
login_user "testuser" "password123"
add_favorite "Paris" 48.8584 2.2945
add_favorite "New York City" 42.3454 10.2945
get_favorites
delete_favorite 1
logout_user

echo "All tests passed successfully!"
