from flask import Flask, request, jsonify, g
from database import get_db, close_db, init_db_command

app = Flask(__name__)

# Register database functions
app.teardown_appcontext(close_db)
app.cli.add_command(init_db_command)

@app.route('/favorites', methods=['GET'])
def get_favorites():
    db = get_db()
    favorites = db.execute(
        'SELECT * FROM favorite_locations WHERE user_id = ?',
        (1,)  # Hardcoded user_id for now
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
            (1, data['location_name'], data['latitude'], data['longitude'])
        )
        db.commit()
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Location added successfully"}), 201

@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    db = get_db()
    db.execute('DELETE FROM favorite_locations WHERE id = ? AND user_id = ?',
               (favorite_id, 1))  # Hardcoded user_id for now
    db.commit()
    
    return jsonify({"message": "Location deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True) 