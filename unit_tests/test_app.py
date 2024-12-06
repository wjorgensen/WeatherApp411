import unittest
from app import app
from database import init_db

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        # Creates a test client
        self.app = app.test_client()
        # Propagate the exceptions to the test client
        self.app.testing = True
        # Initialize test database
        with app.app_context():
            init_db()
        
        # Test user credentials
        self.test_user = {
            'username': 'testuser',
            'password': 'testpass123'
        }

    def register_and_login(self):
        # Register a test user
        self.app.post('/register', json=self.test_user)
        # Login the test user
        return self.app.post('/login', json=self.test_user)

    def test_register(self):
        # Test registration with valid data
        result = self.app.post('/register', json=self.test_user)
        self.assertEqual(result.status_code, 201)
        self.assertIn('User registered successfully', str(result.data))

        # Test registration with duplicate username
        result = self.app.post('/register', json=self.test_user)
        self.assertEqual(result.status_code, 409)
        self.assertIn('Username already exists', str(result.data))

    def test_login(self):
        # Register first
        self.app.post('/register', json=self.test_user)
        
        # Test login with valid credentials
        result = self.app.post('/login', json=self.test_user)
        self.assertEqual(result.status_code, 200)
        self.assertIn('Login successful', str(result.data))

        # Test login with invalid password
        result = self.app.post('/login', json={
            'username': self.test_user['username'],
            'password': 'wrongpassword'
        })
        self.assertEqual(result.status_code, 401)
        self.assertIn('Invalid username or password', str(result.data))

    def test_get_favorites(self):
        # Login first
        self.register_and_login()
        
        # Test getting favorites
        result = self.app.get('/favorites')
        self.assertEqual(result.status_code, 200)

    def test_add_favorite(self):
        # Login first
        self.register_and_login()
        
        # Test adding a favorite
        result = self.app.post('/favorites', json={
            'location_name': 'Test Location',
            'latitude': 123.456,
            'longitude': 78.90
        })
        self.assertEqual(result.status_code, 201)
        self.assertIn('Location added successfully', str(result.data))

    def test_delete_favorite(self):
        # Login first
        self.register_and_login()
        
        # Add a favorite first
        self.app.post('/favorites', json={
            'location_name': 'Test Location',
            'latitude': 123.456,
            'longitude': 78.90
        })
        
        # Test deleting the favorite
        result = self.app.delete('/favorites/1')
        self.assertEqual(result.status_code, 200)
        self.assertIn('Location deleted successfully', str(result.data))

if __name__ == '__main__':
    unittest.main()
