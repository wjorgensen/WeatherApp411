from flask import Flask, request, jsonify, g, session
from database import get_db, close_db, init_db_command
from auth import generate_salt, hash_password, verify_password, login_required
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

app.teardown_appcontext(close_db)
app.cli.add_command(init_db_command)

@app.before_request
def load_logged_in_user():
    g.user_id = session.get('user_id')

@app.route('/register', methods=['POST'])
def register():
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

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
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
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    db = get_db()
    favorites = db.execute(
        'SELECT * FROM favorite_locations WHERE user_id = ?',
        (g.user_id,)
    ).fetchall()
    
    return jsonify([dict(row) for row in favorites])

@app.route('/favorites', methods=['POST'])
def add_favorite():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    required_fields = ['location_name', 'latitude', 'longitude']
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    db = get_db()
    try:
        db.execute(
            'INSERT INTO favorite_locations (user_id, location_name, latitude, longitude)'
            ' VALUES (?, ?, ?, ?)',
            (g.user_id, data['location_name'], data['latitude'], data['longitude'])
        )
        db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Location added successfully"}), 201

@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    db = get_db()
    db.execute('DELETE FROM favorite_locations WHERE id = ? AND user_id = ?',
               (favorite_id, g.user_id)) 
    db.commit()
    
    return jsonify({"message": "Location deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True) 