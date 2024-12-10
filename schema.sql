CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS favorite_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    location_name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS current_weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    temperature REAL,
    feels_like REAL,
    pressure INTEGER,
    humidity INTEGER,
    wind_speed REAL,
    wind_deg INTEGER,
    description TEXT,
    icon TEXT,
    FOREIGN KEY (location_id) REFERENCES favorite_locations (id)
);

CREATE TABLE IF NOT EXISTS weather_forecast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    forecast_timestamp INTEGER NOT NULL,
    temperature REAL,
    feels_like REAL,
    pressure INTEGER,
    humidity INTEGER,
    wind_speed REAL,
    wind_deg INTEGER,
    description TEXT,
    icon TEXT,
    FOREIGN KEY (location_id) REFERENCES favorite_locations (id)
);

CREATE TABLE IF NOT EXISTS weather_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    temperature REAL,
    feels_like REAL,
    pressure INTEGER,
    humidity INTEGER,
    wind_speed REAL,
    wind_deg INTEGER,
    description TEXT,
    icon TEXT,
    FOREIGN KEY (location_id) REFERENCES favorite_locations (id)
); 