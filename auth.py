import hashlib
import os
from functools import wraps
from flask import jsonify, g

def generate_salt():
    """
    Generates a random salt for password hashing.
    
    Returns:
        str: A 32-character hexadecimal string representing 16 random bytes.
    
    Side-effects:
        - Uses system's secure random number generator
    """
    return os.urandom(16).hex()

def hash_password(password, salt):
    """
    Hash a password with the given salt using SHA-256.
    
    Args:
        password (str): The plain-text password to hash
        salt (str): The salt to use in the hashing process
    
    Returns:
        str: The hexadecimal representation of the hashed password
    
    Note:
        The function concatenates the password and salt before hashing
    """
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(stored_password_hash, stored_salt, provided_password):
    """
    Verify a password against its hash.
    
    Args:
        stored_password_hash (str): The previously hashed password from the database
        stored_salt (str): The salt used in the original hash
        provided_password (str): The password to verify
    
    Returns:
        bool: True if the password matches, False otherwise
    
    Note:
        Verifies by hashing the provided password with the stored salt
        and comparing with the stored hash
    """
    return stored_password_hash == hash_password(provided_password, stored_salt)

def login_required(f):
    """
    Decorator to require authentication for Flask routes.
    
    Args:
        f (function): The Flask route function to wrap
    
    Returns:
        function: The decorated function that checks for authentication
    
    Side-effects:
        - Checks g.user_id for current user session
        - Returns 401 error if user is not authenticated
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('user_id'):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function
