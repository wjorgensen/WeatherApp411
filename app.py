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
    app.logger.info(f"Session loaded for user ID: {g.user_id}")

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
            - Success: ({"message": "User registered successfully"}, 201)
            - Error: ({"error": error_message}, error_code)
    
    Raises:
        sqlite3.IntegrityError: If username already exists
        sqlite3.Error: For other database errors
    
    Side-effects:
        - Creates new user record in database
        - Hashes password with salt
    """
    app.logger.info("Received registration request")
    if not request.is_json:
        app.logger.info("Failed registration: Content type must be JSON")
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
        app.logger.info(f"User {data['username']} registered successfully.")
    except sqlite3.IntegrityError:
        app.logger.info("Registration failed: Username already exists.")
        return jsonify({"error": "Username already exists"}), 409
    except sqlite3.Error as e:
        app.logger.info(f"Registration failed: {e}")
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
    app.logger.info("Attempting to authenticate a user.")
    if not request.is_json:
        app.logger.info("Login attempt failed due to incorrect content type.")
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        app.logger.info("Login attempt failed due to incomplete data.")
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ?',
        (data['username'],)
    ).fetchone()

    if user is None:
        app.logger.info("Login attempt failed due to invalid credentials.")
        return jsonify({"error": "Invalid username or password"}), 401

    if not verify_password(user['password_hash'], user['salt'], data['password']):
        app.logger.info("Login attempt failed due to invalid credentials.")
        return jsonify({"error": "Invalid username or password"}), 401

    session['user_id'] = user['id']
    app.logger.info(f"User logged in: {data['username']}")
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
    app.logger.info("Received logout request")
    session.pop('user_id', None)
    app.logger.info("User logged out successfully")
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    """
    Retrieves all favorite locations for the authenticated user.
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - Success: (List of favorite locations, 200)
            - Error: ({"error": "Authentication required"}, 401)
            - Error: ({"message": "No favorite locations found"}, 200)
            - Error: ({"error": "Unable to fetch favorites"}, 500)
    
    Requires:
        - User must be authenticated (@login_required)
    """
    app.logger.info(f"Attempting to retrieve favorite locations for user ID: {g.user_id}")
    db = get_db()
    try:
        favorites = db.execute(
            'SELECT * FROM favorite_locations WHERE user_id = ?',
            (g.user_id,)
        ).fetchall()
        if not favorites:
            app.logger.info("No favorite locations found for user.")
            return jsonify({"message": "No favorite locations found"}), 200
        app.logger.info(f"Found {len(favorites)} favorite locations for user.")
        return jsonify([dict(row) for row in favorites]), 200
    except sqlite3.Error as e:
        app.logger.error(f"Unable to fetch favorites: {e}")
        return jsonify({"error": "Unable to fetch favorites"}), 500

@app.route('/favorites', methods=['POST'])
@login_required
def add_favorite():
    """
    Adds a new favorite location for the authenticated user.
    
    Expected JSON payload:
        {
            "location_name": str,
            "latitude": float,
            "longitude": float
        }
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - Success: ({"message": "Location added successfully"}, 201)
            - Error: ({"error": error_message}, error_code)
    
    Requires:
        - User must be authenticated (@login_required)
    
    Side-effects:
        - Creates new favorite location record in database
    """
    app.logger.info("Adding a new favorite location for user.")
    if not request.is_json:
        app.logger.info("Failed to add favorite location: Content type must be JSON")
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
        app.logger.error(f"Failed to add favorite location: {e}")
        return jsonify({"error": str(e)}), 500
    app.logger.info("Favorite location added successfully.")
    return jsonify({"message": "Location added successfully"}), 200

@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    """
    Deletes a specific favorite location for the authenticated user.
    
    Args:
        favorite_id (int): The ID of the favorite location to delete
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - Success: ({"message": "Location deleted successfully"}, 200)
            - Error: ({"error": "Unable to delete location"}, 500)
    
    Requires:
        - User must be authenticated
        - Favorite location must belong to the authenticated user
    
    Side-effects:
        - Removes favorite location record from database
    """
    app.logger.info(f"Attempting to delete favorite location with ID: {favorite_id} for user ID: {g.user_id}")
    db = get_db()
    try:
        result = db.execute('DELETE FROM favorite_locations WHERE id = ? AND user_id = ?', (favorite_id, g.user_id))
        db.commit()
        if result.rowcount == 0:
            app.logger.info("No location found to delete, or location does not belong to the user.")
            return jsonify({"error": "Location not found or not owned by user"}), 404
        app.logger.info("Favorite location deleted successfully.")
        return jsonify({"message": "Location deleted successfully"}), 200
    except sqlite3.Error as e:
        app.logger.error(f"Unable to delete location")
        return jsonify({"error": "Unable to delete location"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint to verify service status.
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - Success: ({"status": "healthy", "message": "Service is running"}, 200)
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
    
    Expected JSON payload:
        {
            "current_password": str,
            "new_password": str
        }
    
    Returns:
        tuple: (JSON response, HTTP status code)
            - Success: ({"message": "Password updated successfully"}, 200)
            - Error: ({"error": error_message}, error_code)
    
    Requires:
        - User must be authenticated (@login_required)
        - Current password must be correct
    
    Side-effects:
        - Updates password_hash and salt in database
    """
    app.logger.info("Attempting to update password for user.")
    if not request.is_json:
        app.logger.info("Password update failed: Request must be JSON.")
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data.get('current_password') or not data.get('new_password'):
        app.logger.info("Password update failed: Missing required password fields.")
        return jsonify({"error": "Current password and new password are required"}), 400

    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?',
        (g.user_id,)
    ).fetchone()

    if not verify_password(user['password_hash'], user['salt'], data['current_password']):
        app.logger.info("Password update failed: Incorrect current password.")
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
        app.logger.info("Password successfully updated for user.")
    except sqlite3.Error as e:
        app.logger.info(f"Password update failed due to database error: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Password updated successfully"}), 200

@app.route('/weather/current/<int:location_id>', methods=['GET', 'POST'])
@login_required
def current_weather(location_id):
    """
    Get or store current weather for a location.
    """
    db = get_db()
    location = db.execute(
        'SELECT * FROM favorite_locations WHERE id = ? AND user_id = ?',
        (location_id, g.user_id)
    ).fetchone()
    
    if not location:
        return jsonify({"error": "Location not found"}), 404

    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        current = data.get('current', {})
        
        try:
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
            return jsonify({"message": "Weather data stored successfully"}), 201
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500
    
    # GET request - retrieve latest weather data
    weather = db.execute('''
        SELECT * FROM current_weather 
        WHERE location_id = ? 
        ORDER BY timestamp DESC LIMIT 1
    ''', (location_id,)).fetchone()
    
    return jsonify(dict(weather) if weather else {"error": "No weather data found"}), 200

@app.route('/weather/forecast/<int:location_id>', methods=['GET', 'POST'])
@login_required
def weather_forecast(location_id):
    """
    Get or store weather forecast for a location.
    """
    db = get_db()
    location = db.execute(
        'SELECT * FROM favorite_locations WHERE id = ? AND user_id = ?',
        (location_id, g.user_id)
    ).fetchone()
    
    if not location:
        return jsonify({"error": "Location not found"}), 404

    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        current_time = data.get('current', {}).get('dt')
        
        try:
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
            return jsonify({"message": "Forecast data stored successfully"}), 201
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500
    
    # GET request - retrieve latest forecast
    forecasts = db.execute('''
        SELECT * FROM weather_forecast 
        WHERE location_id = ? 
        ORDER BY timestamp DESC, forecast_timestamp ASC
        LIMIT 7
    ''', (location_id,)).fetchall()
    
    return jsonify([dict(f) for f in forecasts]), 200

@app.route('/weather/history/<int:location_id>', methods=['GET', 'POST'])
@login_required
def weather_history(location_id):
    """
    Get or store weather history for a location.
    """
    db = get_db()
    location = db.execute(
        'SELECT * FROM favorite_locations WHERE id = ? AND user_id = ?',
        (location_id, g.user_id)
    ).fetchone()
    
    if not location:
        return jsonify({"error": "Location not found"}), 404

    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        
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
            return jsonify({"message": "Historical data stored successfully"}), 201
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500
    
    history = db.execute('''
        SELECT * FROM weather_history 
        WHERE location_id = ? 
        ORDER BY timestamp DESC
        LIMIT 24
    ''', (location_id,)).fetchall()
    
    return jsonify([dict(h) for h in history]), 200

@app.route('/weather/current/<int:location_id>', methods=['POST'])
@login_required
def store_current_weather(location_id):
    """Store current weather data for a location."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    
    try:
        db = get_db()
        db.execute('''
            INSERT INTO current_weather 
            (location_id, timestamp, temperature, feels_like, pressure, 
            humidity, wind_speed, wind_deg, description, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            location_id,
            data.get('dt'),
            data.get('temp'),
            data.get('feels_like'),
            data.get('pressure'),
            data.get('humidity'),
            data.get('wind_speed'),
            data.get('wind_deg'),
            data.get('weather', [{}])[0].get('description'),
            data.get('weather', [{}])[0].get('icon')
        ))
        db.commit()
        return jsonify({"message": "Weather data stored successfully"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/weather/forecast/<int:location_id>', methods=['POST'])
@login_required
def store_weather_forecast(location_id):
    """Store weather forecast data for a location."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    db = get_db()
    
    try:
        for daily in data.get('daily', []):
            db.execute('''
                INSERT INTO weather_forecast 
                (location_id, timestamp, forecast_timestamp, temperature, 
                feels_like, pressure, humidity, wind_speed, wind_deg, 
                description, icon)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                location_id,
                data.get('current', {}).get('dt'),
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
        return jsonify({"message": "Forecast data stored successfully"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/weather/history/<int:location_id>', methods=['POST'])
@login_required
def store_weather_history(location_id):
    """Store weather history data for a location."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    db = get_db()
    
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
        return jsonify({"message": "Historical data stored successfully"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False) 