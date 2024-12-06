# Weather App

## To Run

1. Clone the repository locally
2. Navigate to folder
3. Make sure docker is running

4. ```docker build -t weather-app .```
5. ```docker run -it weather-app```

## To run tests
1. Clone the repository locally
2. Navigate to folde
3. ```python3 -m venv venv```
4. ```source venv/bin/activate```
5. ```pip install ./requirements.txt```
6. ```python -m pytest unit_tests/test_run.py -v```


## API Routes

### Authentication

#### Register User
- **URL:** `/register`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Request Body:**
  json
{
"username": "string",
"password": "string"
}
- **Success Response:**
  - **Code:** 201
  - **Content:** `{"message": "User registered successfully"}`
- **Error Responses:**
  - **Code:** 400 - Missing username/password
  - **Code:** 409 - Username already exists

#### Login
- **URL:** `/login`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Request Body:**
json
{
"username": "string",
"password": "string"
}
- **Success Response:**
  - **Code:** 200
  - **Content:** `{"message": "Login successful"}`
- **Error Response:**
  - **Code:** 401 - Invalid credentials

#### Logout
- **URL:** `/logout`
- **Method:** `POST`
- **Success Response:**
  - **Code:** 200
  - **Content:** `{"message": "Logged out successfully"}`

#### Update Password
- **URL:** `/update-password`
- **Method:** `POST`
- **Authentication:** Required
- **Content-Type:** `application/json`
- **Request Body:**
  ```json
  {
    "current_password": "string",
    "new_password": "string"
  }
  ```
- **Success Response:**
  - **Code:** 200
  - **Content:** `{"message": "Password updated successfully"}`
- **Error Responses:**
  - **Code:** 401 - Current password incorrect or not authenticated
  - **Code:** 400 - Missing required fields

### Favorite Locations

#### Get Favorites
- **URL:** `/favorites`
- **Method:** `GET`
- **Authentication:** Required
- **Success Response:**
  - **Code:** 200
  - **Content:** Array of favorite locations
  json
[
{
"id": "integer",
"location_name": "string",
"latitude": "float",
"longitude": "float"
}
]

- **Error Response:**
  - **Code:** 401 - Authentication required

#### Add Favorite
- **URL:** `/favorites`
- **Method:** `POST`
- **Authentication:** Required
- **Content-Type:** `application/json`
- **Request Body:**
json
{
"location_name": "string",
"latitude": "float",
"longitude": "float"
}
- **Success Response:**
  - **Code:** 201
  - **Content:** `{"message": "Location added successfully"}`
- **Error Response:**
  - **Code:** 401 - Authentication required

#### Delete Favorite
- **URL:** `/favorites/<favorite_id>`
- **Method:** `DELETE`
- **Authentication:** Required
- **Success Response:**
  - **Code:** 200
  - **Content:** `{"message": "Location deleted successfully"}`
- **Error Response:**
  - **Code:** 401 - Authentication required


#### Health Check
- **URL:** `/health`
- **Method:** `GET`
- **Authentication:** Not required
- **Success Response:**
  - **Code:** 200
  - **Content:** `{"status": "healthy", "message": "Service is running"}`
- **Description:** Simple endpoint to verify the API service is up and running

## Database Schema

The application uses SQLite with the following schema:

### Users Table
sql
CREATE TABLE users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
salt TEXT NOT NULL
);

### Favorite Locations Table
sql
CREATE TABLE favorite_locations (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
location_name TEXT NOT NULL,
latitude REAL NOT NULL,
longitude REAL NOT NULL,
FOREIGN KEY (user_id) REFERENCES users (id)
);

## Security Features

- Password hashing with salt
- Session-based authentication
- Login required decorator for protected routes
- 30-minute session lifetime