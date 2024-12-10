from flask import Flask, request, jsonify, g, session
from database import get_db, close_db, init_db_command, clear_db_command
from auth import *
import sqlite3
import logging
import sys
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

logging.getLogger('werkzeug').disabled = True
# Set up basic logging to standard output
logging.basicConfig(level=logging.INFO)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)


cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app.teardown_appcontext(close_db)
app.cli.add_command(init_db_command)
app.cli.add_command(clear_db_command)

@app.before_request
def load_logged_in_user():
    """
    Loads the user ID from the session before each request.
    
    Side-effects:
        - Sets g.user_id to the current user's ID from the session
    """
    g.user_id = session.get('user_id')
    app.logger.info(f"\nSession loaded for user ID: {g.user_id}")

@app.route('/register', methods=['POST'])
def register():
    """
    Registers a new user with the provided username and password.
    
    Expected JSON payload:
        {
            "username": str,
            "password": str
        }
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - Success: ({"message": "User registered successfully"}, 200)
            - Error: ({"error": error_message}, error_code)
    
    Raises:
        sqlite3.IntegrityError: If username already exists
        sqlite3.Error: For other database errors
    
    Side-effects:
        - Creates new user record in database
        - Hashes password with salt
    """
    app.logger.info("\nReceived registration request")
    if not request.is_json:
        app.logger.info("\nFailed registration: Content type must be JSON")
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    salt = generate_salt()
    password_hash = hash_password(data['password'], salt)
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
            (data['username'], password_hash, salt)
        )
        db.commit()
        app.logger.info(f"\nUser {data['username']} registered successfully.")
    except sqlite3.IntegrityError:
        app.logger.info("\nRegistration failed: Username already exists.")
        return jsonify({"error": "Username already exists"}), 409
    except sqlite3.Error as e:
        app.logger.info(f"\nRegistration failed: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "User registered successfully"}), 200

@app.route('/login', methods=['POST'])
def login():
    """
    Authenticates a user and creates a new session.
    
    Expected JSON payload:
        {
            "username": str,
            "password": str
        }
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - Success: ({"message": "Login successful"}, 200)
            - Error: ({"error": error_message}, error_code)
    
    Side-effects:
        - Creates new session for authenticated user
        - Sets user_id in session
    """
    app.logger.info("\nAttempting to authenticate a user.")
    if not request.is_json:
        app.logger.info("\nLogin attempt failed due to incorrect content type.")
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        app.logger.info("\nLogin attempt failed due to incomplete data.")
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ?',
        (data['username'],)
    ).fetchone()

    if user is None:
        app.logger.info("\nLogin attempt failed due to invalid credentials.")
        return jsonify({"error": "Invalid username or password"}), 401

    if not verify_password(user['password_hash'], user['salt'], data['password']):
        app.logger.info("\nLogin attempt failed due to invalid credentials.")
        return jsonify({"error": "Invalid username or password"}), 401

    session['user_id'] = user['id']
    app.logger.info(f"\nUser logged in: {data['username']}")
    return jsonify({"message": "Login successful"}), 200

@app.route('/logout', methods=['POST'])
def logout():
    """
    Logs out the current user by removing their session.
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - Success: ({"message": "Logged out successfully"}, 200)
    
    Side-effects:
        - Removes user_id from session
    """
    app.logger.info("\nReceived logout request")
    session.pop('user_id', None)
    app.logger.info("\nUser logged out successfully")
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    """
    Retrieves all favorite locations for the authenticated user.
    """
    app.logger.info(f"\nAttempting to retrieve favorite locations for user ID: {g.user_id}")
    db = get_db()
    try:
        favorites = db.execute(
            'SELECT * FROM favorite_locations WHERE user_id = ?',
            (g.user_id,)
        ).fetchall()
        if not favorites:
            app.logger.info("\nNo favorite locations found for user.")
            return jsonify({"message": "No favorite locations found"}), 200
        app.logger.info(f"\nFound {len(favorites)} favorite locations for user.")
        return jsonify([dict(row) for row in favorites]), 200
    except sqlite3.Error as e:
        app.logger.error(f"\nUnable to fetch favorites: {e}")
        return jsonify({"error": "Unable to fetch favorites"}), 500

@app.route('/favorites', methods=['POST'])
@login_required
def add_favorite():
    """
    Adds a new favorite location for the authenticated user.
    """
    app.logger.info("\nAdding a new favorite location for user.")
    if not request.is_json:
        app.logger.info("\nFailed to add favorite location: Content type must be JSON")
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    try:
        db = get_db()
        db.execute(
            'INSERT INTO favorite_locations (user_id, location_name, latitude, longitude)'
            ' VALUES (?, ?, ?, ?)',
            (g.user_id, data['location_name'], data['latitude'], data['longitude'])
        )
        db.commit()
    except Exception as e:
        app.logger.error(f"\nFailed to add favorite location: {e}")
        return jsonify({"error": str(e)}), 500
    app.logger.info("\nFavorite location added successfully.")
    return jsonify({"message": "Location added successfully"}), 200

@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    """
    Deletes a specific favorite location for the authenticated user.
    """
    app.logger.info(f"\nAttempting to delete favorite location with ID: {favorite_id} for user ID: {g.user_id}")
    db = get_db()
    try:
        result = db.execute('DELETE FROM favorite_locations WHERE id = ? AND user_id = ?', (favorite_id, g.user_id))
        db.commit()
        if result.rowcount == 0:
            app.logger.info("\nNo location found to delete, or location does not belong to the user.")
            return jsonify({"error": "Location not found or not owned by user"}), 404
        app.logger.info("\nFavorite location deleted successfully.")
        return jsonify({"message": "Location deleted successfully"}), 200
    except sqlite3.Error as e:
        app.logger.error(f"\nUnable to delete location")
        return jsonify({"error": "Unable to delete location"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint to verify service status.
    """
    return jsonify({
        "status": "healthy",
        "message": "Service is running"
    }), 200

@app.route('/update-password', methods=['POST'])
@login_required
def update_password():
    """
    Updates the password for the currently authenticated user.
    """
    app.logger.info("\nAttempting to update password for user.")
    if not request.is_json:
        app.logger.info("\nPassword update failed: Request must be JSON.")
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data.get('current_password') or not data.get('new_password'):
        app.logger.info("\nPassword update failed: Missing required password fields.")
        return jsonify({"error": "Current password and new password are required"}), 400

    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?',
        (g.user_id,)
    ).fetchone()

    if not verify_password(user['password_hash'], user['salt'], data['current_password']):
        app.logger.info("\nPassword update failed: Incorrect current password.")
        return jsonify({"error": "Current password is incorrect"}), 401

    # Generate new salt and hash for the new password
    new_salt = generate_salt()
    new_password_hash = hash_password(data['new_password'], new_salt)

    try:
        db.execute(
            'UPDATE users SET password_hash = ?, salt = ? WHERE id = ?',
            (new_password_hash, new_salt, g.user_id)
        )
        db.commit()
        app.logger.info("\nPassword successfully updated for user.")
    except sqlite3.Error as e:
        app.logger.info(f"\nPassword update failed due to database error: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Password updated successfully"}), 200

@app.route('/weather/current/<int:location_id>', methods=['GET', 'POST'])
@login_required
def current_weather(location_id):
    """
    Get or store current weather for a location.
    """
    app.logger.info(f"\nRetrieving or storing current weather for location ID: {location_id}")
    db = get_db()
    location = db.execute(
        'SELECT * FROM favorite_locations WHERE id = ? AND user_id = ?',
        (location_id, g.user_id)
    ).fetchone()
    
    if not location:
        app.logger.info("\nError: Location not found.")
        return jsonify({"error": "Location not found"}), 404

    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        app.logger.info("\nReceived current weather data.")
        app.logger.info(data)
        current = data.get('current', {})
        
        try:
            app.logger.info("\nStoring current weather data.")
            db.execute('''
                INSERT INTO current_weather 
                (location_id, timestamp, temperature, feels_like, pressure, 
                humidity, wind_speed, wind_deg, description, icon)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                location_id,
                current.get('dt'),
                current.get('temp'),
                current.get('feels_like'),
                current.get('pressure'),
                current.get('humidity'),
                current.get('wind_speed'),
                current.get('wind_deg'),
                current.get('weather', [{}])[0].get('description'),
                current.get('weather', [{}])[0].get('icon')
            ))
            db.commit()
            app.logger.info("\nWeather data stored successfully.")
            return jsonify({"message": "Weather data stored successfully"}), 200
        except sqlite3.Error as e:
            app.logger.error(f"\nError storing weather data: {e}")
            return jsonify({"error": str(e)}), 500
    # GET request - retrieve latest weather data
    weather = db.execute('''
        SELECT * FROM current_weather 
        WHERE location_id = ? 
        ORDER BY timestamp DESC LIMIT 1
    ''', (location_id,)).fetchone()
    app.logger.info("\nWeather data retrieved successfully.")
    return jsonify(dict(weather) if weather else {"error": "No weather data found"}), 200

@app.route('/weather/forecast/<int:location_id>', methods=['GET', 'POST'])
@login_required
def weather_forecast(location_id):
    """
    Get or store weather forecast for a location.
    """
    app.logger.info(f"\nRetrieving or storing weather forecast for location ID: {location_id}")
    db = get_db()
    location = db.execute(
        'SELECT * FROM favorite_locations WHERE id = ? AND user_id = ?',
        (location_id, g.user_id)
    ).fetchone()
    
    if not location:
        app.logger.info("\nError: Location not found.")
        return jsonify({"error": "Location not found"}), 404

    if request.method == 'POST':
        if not request.is_json:
            app.logger.info("\nFailed to store forecast data: Content type must be JSON")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        app.logger.info("\nReceived forecast data.")
        app.logger.info(data)
        current_time = data.get('current', {}).get('dt')
        
        try:
            app.logger.info("\nStoring forecast data.")
            for daily in data.get('daily', []):
                db.execute('''
                    INSERT INTO weather_forecast 
                    (location_id, timestamp, forecast_timestamp, temperature, 
                    feels_like, pressure, humidity, wind_speed, wind_deg, 
                    description, icon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    location_id,
                    current_time,
                    daily.get('dt'),
                    daily.get('temp', {}).get('day'),
                    daily.get('feels_like', {}).get('day'),
                    daily.get('pressure'),
                    daily.get('humidity'),
                    daily.get('wind_speed'),
                    daily.get('wind_deg'),
                    daily.get('weather', [{}])[0].get('description'),
                    daily.get('weather', [{}])[0].get('icon')
                ))
            db.commit()
            app.logger.info("\nForecast data stored successfully.")
            return jsonify({"message": "Forecast data stored successfully"}), 200
        except sqlite3.Error as e:
            app.logger.info(f"\nError storing forecast data: {e}")
            return jsonify({"error": str(e)}), 500
    
    # GET request - retrieve latest forecast
    app.logger.info("\nRetrieving forecast data.")
    forecasts = db.execute('''
        SELECT * FROM weather_forecast 
        WHERE location_id = ? 
        ORDER BY timestamp DESC, forecast_timestamp ASC
        LIMIT 7
    ''', (location_id,)).fetchall()
    app.logger.info("\nForecast data retrieved successfully.")
    return jsonify([dict(f) for f in forecasts]), 200

@app.route('/weather/history/<int:location_id>', methods=['GET', 'POST'])
@login_required
def weather_history(location_id):
    """
    Get or store weather history for a location.
    """
    app.logger.info(f"\nRetrieving or storing weather history for location ID: {location_id}")
    db = get_db()
    location = db.execute(
        'SELECT * FROM favorite_locations WHERE id = ? AND user_id = ?',
        (location_id, g.user_id)
    ).fetchone()
    
    if not location:
        app.logger.info("\nError: Location not found.")
        return jsonify({"error": "Location not found"}), 404

    if request.method == 'POST':
        app.logger.info("\nStoring historical data.")
        if not request.is_json:
            app.logger.info("\nFailed to store historical data: Content type must be JSON")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        app.logger.info("\nReceived historical data.")
        app.logger.info(data)
        
        try:
            for hourly in data.get('hourly', []):
                db.execute('''
                    INSERT INTO weather_history 
                    (location_id, timestamp, temperature, feels_like, 
                    pressure, humidity, wind_speed, wind_deg, description, icon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    location_id,
                    hourly.get('dt'),
                    hourly.get('temp'),
                    hourly.get('feels_like'),
                    hourly.get('pressure'),
                    hourly.get('humidity'),
                    hourly.get('wind_speed'),
                    hourly.get('wind_deg'),
                    hourly.get('weather', [{}])[0].get('description'),
                    hourly.get('weather', [{}])[0].get('icon')
                ))
            db.commit()
            app.logger.info("\nHistorical data stored successfully.")
            return jsonify({"message": "Historical data stored successfully"}), 200
        except sqlite3.Error as e:
            app.logger.info(f"\nError storing historical data: {e}")
            return jsonify({"error": str(e)}), 500
    
    app.logger.info("\nRetrieving historical data.")
    history = db.execute('''
        SELECT * FROM weather_history 
        WHERE location_id = ? 
        ORDER BY timestamp DESC
        LIMIT 24
    ''', (location_id,)).fetchall()
    app.logger.info("\nHistorical data retrieved successfully.")
    return jsonify([dict(h) for h in history]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False) 
