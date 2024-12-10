import unittest
from unittest.mock import patch, MagicMock
from run import (register_user, login_user, get_favorites, 
                add_favorite, remove_favorite, get_weather_api_data,
                get_forecast_api_data, get_history_api_data, BASE_URL)



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

    @patch('requests.sessions.Session.post')
    def test_register_user_success(self, mock_post):
        """Test successful user registration."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = register_user(self.test_user['username'], self.test_user['password'])
        
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            f"{BASE_URL}/register",
            json=self.test_user
        )

    @patch('requests.sessions.Session.post')
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

    @patch('requests.sessions.Session.get')
    @patch('requests.get')
    def test_get_weather_api_data_success(self, mock_weather_get, mock_favorites_get):
        """Test successful weather data retrieval."""
        # Mock favorites response
        mock_favorites_response = MagicMock()
        mock_favorites_response.status_code = 200
        mock_favorites_response.json.return_value = [{
            'id': 1,
            'location_name': 'Test Location',
            'latitude': 123.456,
            'longitude': 78.90
        }]
        mock_favorites_get.return_value = mock_favorites_response

        # Mock weather API response
        mock_weather_response = MagicMock()
        mock_weather_response.status_code = 200
        mock_weather_response.json.return_value = {
            'current': {
                'temp': 20.5,
                'feels_like': 21.0,
                'pressure': 1013,
                'humidity': 65,
                'wind_speed': 5.2,
                'wind_deg': 180,
                'weather': [{
                    'description': 'clear sky',
                    'icon': '01d'
                }]
            }
        }
        mock_weather_get.return_value = mock_weather_response

        result = get_weather_api_data(1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['temperature'], 20.5)
        self.assertEqual(result['description'], 'clear sky')

    @patch('requests.sessions.Session.get')
    def test_get_weather_api_data_location_not_found(self, mock_get):
        """Test weather data retrieval with invalid location."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = get_weather_api_data(999)
        
        self.assertIsNone(result)

    @patch('requests.sessions.Session.get')
    @patch('requests.get')
    def test_get_forecast_api_data_success(self, mock_weather_get, mock_favorites_get):
        """Test successful forecast data retrieval."""
        # Mock favorites response
        mock_favorites_response = MagicMock()
        mock_favorites_response.status_code = 200
        mock_favorites_response.json.return_value = [{
            'id': 1,
            'location_name': 'Test Location',
            'latitude': 123.456,
            'longitude': 78.90
        }]
        mock_favorites_get.return_value = mock_favorites_response

        # Mock weather API response
        mock_weather_response = MagicMock()
        mock_weather_response.status_code = 200
        mock_weather_response.json.return_value = {
            'list': [{
                'dt': 1234567890,
                'main': {
                    'temp': 22.5,
                    'feels_like': 23.0,
                    'pressure': 1015,
                    'humidity': 70
                },
                'wind': {
                    'speed': 4.1,
                    'deg': 90
                },
                'weather': [{
                    'description': 'scattered clouds',
                    'icon': '03d'
                }]
            }]
        }
        mock_weather_get.return_value = mock_weather_response

        result = get_forecast_api_data(1)
        
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(result[0]['temperature'], 22.5)
        self.assertEqual(result[0]['description'], 'scattered clouds')

    @patch('requests.sessions.Session.get')
    @patch('requests.get')
    def test_get_history_api_data_success(self, mock_weather_get, mock_favorites_get):
        """Test successful historical data retrieval."""
        # Mock favorites response
        mock_favorites_response = MagicMock()
        mock_favorites_response.status_code = 200
        mock_favorites_response.json.return_value = [{
            'id': 1,
            'location_name': 'Test Location',
            'latitude': 123.456,
            'longitude': 78.90
        }]
        mock_favorites_get.return_value = mock_favorites_response

        # Mock weather API response
        mock_weather_response = MagicMock()
        mock_weather_response.status_code = 200
        mock_weather_response.json.return_value = {
            'hourly': [{
                'dt': 1234567890,
                'temp': 18.5,
                'feels_like': 19.0,
                'pressure': 1012,
                'humidity': 75,
                'wind_speed': 3.1,
                'wind_deg': 270,
                'weather': [{
                    'description': 'light rain',
                    'icon': '10n'
                }]
            }]
        }
        mock_weather_get.return_value = mock_weather_response

        result = get_history_api_data(1)
        
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(result[0]['temperature'], 18.5)

if __name__ == '__main__':
    unittest.main()
