import unittest
from app import app

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        # Creates a test client
        self.app = app.test_client()
        # Propagate the exceptions to the test client
        self.app.testing = True

    def test_get_favorites(self):
        # Sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/favorites')
        
        # Assert the response data
        self.assertEqual(result.status_code, 200)

    def test_add_favorite(self):
        # Sends HTTP POST request to the application
        # on the specified path
        result = self.app.post('/favorites', json={
            'location_name': 'Test Location',
            'latitude': 123.456,
            'longitude': 78.90
        })
        
        # Assert the response data
        self.assertEqual(result.status_code, 201)
        self.assertIn('Location added successfully', str(result.data))

    def test_delete_favorite(self):
        # Assuming there's an ID 1 to delete, this needs to be adjusted based on actual data
        result = self.app.delete('/favorites/1')
        
        # Assert the response data
        self.assertEqual(result.status_code, 200)
        self.assertIn('Location deleted successfully', str(result.data))

if __name__ == '__main__':
    unittest.main()
