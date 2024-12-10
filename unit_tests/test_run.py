import unittest
from unittest.mock import patch, MagicMock
from run import (register_user, login_user, get_favorites, 
                add_favorite, remove_favorite, BASE_URL)



class RunTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_user = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.test_location = {
            'location_name': 'Test Location',
            'latitude': 123.456,
            'longitude': 78.90
        }

    @patch('requests.post')
    def test_register_user_success(self, mock_post):
        """Test successful user registration."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        result = register_user(self.test_user['username'], self.test_user['password'])
        
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            f"{BASE_URL}/register",
            json=self.test_user
        )

    @patch('requests.post')
    def test_register_user_failure(self, mock_post):
        """Test failed user registration."""
        mock_response = MagicMock()
        mock_response.status_code = 409  # Conflict - user exists
        mock_post.return_value = mock_response

        result = register_user(self.test_user['username'], self.test_user['password'])
        
        self.assertFalse(result)

    @patch('requests.sessions.Session.post')
    def test_login_user_success(self, mock_post):
        """Test successful user login."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = login_user(self.test_user['username'], self.test_user['password'])
        
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            f"{BASE_URL}/login",
            json=self.test_user
        )

    @patch('requests.sessions.Session.post')
    def test_login_user_failure(self, mock_post):
        """Test failed user login."""
        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        mock_post.return_value = mock_response

        result = login_user(self.test_user['username'], self.test_user['password'])
        
        self.assertFalse(result)

    @patch('requests.sessions.Session.get')
    def test_get_favorites_success(self, mock_get):
        """Test successful retrieval of favorites."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 1,
                'location_name': 'Test Location',
                'latitude': 123.456,
                'longitude': 78.90
            }
        ]
        mock_get.return_value = mock_response

        result = get_favorites()
        
        self.assertTrue(result)
        mock_get.assert_called_once_with(f"{BASE_URL}/favorites")

    @patch('requests.sessions.Session.get')
    def test_get_favorites_unauthorized(self, mock_get):
        """Test unauthorized access to favorites."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = get_favorites()
        
        self.assertFalse(result)

    @patch('requests.sessions.Session.post')
    def test_add_favorite_success(self, mock_post):
        """Test successful addition of favorite location."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        result = add_favorite(
            self.test_location['location_name'],
            self.test_location['latitude'],
            self.test_location['longitude']
        )
        
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            f"{BASE_URL}/favorites",
            json=self.test_location
        )

    @patch('requests.sessions.Session.delete')
    def test_remove_favorite_success(self, mock_delete):
        """Test successful removal of favorite location."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        result = remove_favorite(1)
        
        self.assertTrue(result)
        mock_delete.assert_called_once_with(f"{BASE_URL}/favorites/1")

    @patch('requests.sessions.Session.delete')
    def test_remove_favorite_failure(self, mock_delete):
        """Test failed removal of favorite location."""
        mock_response = MagicMock()
        mock_response.status_code = 404  # Not found
        mock_delete.return_value = mock_response

        result = remove_favorite(999)  # Non-existent ID
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
