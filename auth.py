import hashlib
import os
from functools import wraps
from flask import jsonify, request, g

def generate_salt():
    return os.urandom(16).hex()

def hash_password(password, salt):
    """Hash a password with the given salt using SHA-256"""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(stored_password_hash, stored_salt, provided_password):
    """Verify a password against its hash"""
    return stored_password_hash == hash_password(provided_password, stored_salt)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('user_id'):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function
