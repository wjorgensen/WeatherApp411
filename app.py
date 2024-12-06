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
    if not request.is_json:
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
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    except sqlite3.Error as e:
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
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ?',
        (data['username'],)
    ).fetchone()

    if user is None:
        return jsonify({"error": "Invalid username or password"}), 401

    if not verify_password(user['password_hash'], user['salt'], data['password']):
        return jsonify({"error": "Invalid username or password"}), 401

    session['user_id'] = user['id']
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
    session.pop('user_id', None)
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
    
    Requires:
        - User must be authenticated (@login_required)
    """
    db = get_db()
    favorites = db.execute(
        'SELECT * FROM favorite_locations WHERE user_id = ?',
        (g.user_id,)
    ).fetchall()
    
    return jsonify([dict(row) for row in favorites]), 200

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
    if not request.is_json:
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
        return jsonify({"error": str(e)}), 500

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
    
    Requires:
        - User must be authenticated
        - Favorite location must belong to the authenticated user
    
    Side-effects:
        - Removes favorite location record from database
    """
    db = get_db()
    db.execute('DELETE FROM favorite_locations WHERE id = ? AND user_id = ?',
               (favorite_id, g.user_id)) 
    db.commit()
    
    return jsonify({"message": "Location deleted successfully"}), 200

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
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({"error": "Current password and new password are required"}), 400

    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?',
        (g.user_id,)
    ).fetchone()

    if not verify_password(user['password_hash'], user['salt'], data['current_password']):
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
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Password updated successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False) 