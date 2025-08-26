import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import streamlit as st

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the streamlit app functions
from streamlit_app import APIClient

class TestAPIClient:
    """Test cases for APIClient class"""
    
    def test_apiclient_class_exists(self):
        """Test that APIClient class exists and can be instantiated"""
        # APIClient is a static class, so we just test it exists
        assert hasattr(APIClient, 'make_request')
        assert hasattr(APIClient, 'login_user')
        assert hasattr(APIClient, 'register_user')
        assert hasattr(APIClient, 'get_movies')
        assert hasattr(APIClient, 'get_series')
        assert hasattr(APIClient, 'search_movies')
        assert hasattr(APIClient, 'search_series')
        assert hasattr(APIClient, 'get_recommendations')
        assert hasattr(APIClient, 'chat_with_bot')
        assert hasattr(APIClient, 'verify_token')
        assert hasattr(APIClient, 'logout_user')
    
    @patch('requests.post')
    def test_login_user_success(self, mock_post):
        """Test successful user login"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "token": "test_token_123",
            "user": {"username": "testuser", "email": "test@example.com"}
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = APIClient.login_user("testuser", "password123")
        
        assert result["success"] is True
        assert result["data"]["token"] == "test_token_123"
        assert result["data"]["user"]["username"] == "testuser"
    
    @patch('requests.post')
    def test_login_user_failure(self, mock_post):
        """Test failed user login"""
        # Mock failed response
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": "Invalid credentials"
        }
        mock_response.status_code = 401
        mock_response.content = b'{"error": "Invalid credentials"}'
        mock_post.return_value = mock_response
        
        result = APIClient.login_user("wronguser", "wrongpass")
        
        assert result["success"] is False
        assert "Invalid credentials" in result["message"]
    
    @patch('requests.post')
    def test_register_user_success(self, mock_post):
        """Test successful user registration"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "User registered successfully"
        }
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        result = APIClient.register_user("newuser", "new@example.com", "password123", "New User")
        
        assert result["success"] is True
        assert result["data"]["message"] == "User registered successfully"
    
    @patch('requests.get')
    def test_get_movies_success(self, mock_get):
        """Test successful movies retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "title": "Test Movie 1", "genre": "Action"},
            {"id": 2, "title": "Test Movie 2", "genre": "Drama"}
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = APIClient.get_movies()
        
        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["data"][0]["title"] == "Test Movie 1"
    
    @patch('requests.get')
    def test_get_series_success(self, mock_get):
        """Test successful series retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "title": "Test Series 1", "genre": "Comedy"},
            {"id": 2, "title": "Test Series 2", "genre": "Drama"}
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = APIClient.get_series()
        
        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["data"][0]["title"] == "Test Series 1"
    
    @patch('requests.get')
    def test_search_movies_success(self, mock_get):
        """Test successful movie search"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "title": "Avengers", "genre": "Action"}
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = APIClient.search_movies("Avengers")
        
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["title"] == "Avengers"
    
    @patch('requests.get')
    def test_search_series_success(self, mock_get):
        """Test successful series search"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "title": "Breaking Bad", "genre": "Drama"}
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = APIClient.search_series("Breaking Bad")
        
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["title"] == "Breaking Bad"
    
    @patch('requests.get')
    def test_get_recommendations_success(self, mock_get):
        """Test successful recommendations retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "title": "Recommended Movie", "genre": "Action"}
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = APIClient.get_recommendations()
        
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["title"] == "Recommended Movie"
    
    @patch('requests.post')
    def test_chat_with_bot_success(self, mock_post):
        """Test successful chatbot interaction"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Hello! How can I help you?"
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = APIClient.chat_with_bot("Hello")
        
        assert result["success"] is True
        assert result["data"]["response"] == "Hello! How can I help you?"
    
   
    
    @patch('requests.post')
    def test_logout_user_success(self, mock_post):
        """Test successful user logout"""
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "Logged out successfully"
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = APIClient.logout_user()
        
        assert result["success"] is True
        assert result["data"]["message"] == "Logged out successfully"
    
    @patch('requests.post')
    def test_make_request_success(self, mock_post):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = APIClient.make_request("POST", "http://test.com", {"test": "data"})
        
        assert result["success"] is True
        assert result["data"] == {"data": "test"}
    
    @patch('requests.post')
    def test_make_request_failure(self, mock_post):
        """Test failed API request"""
        # Mock failed response
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Server error"}
        mock_response.status_code = 500
        mock_response.content = b'{"error": "Server error"}'
        mock_post.return_value = mock_response
        
        result = APIClient.make_request("POST", "http://test.com", {"test": "data"})
        
        assert result["success"] is False
        assert "Server error" in result["message"]
    
    def test_make_request_without_data(self):
        """Test make_request without data parameter"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = APIClient.make_request("GET", "http://test.com")
            
            assert result["success"] is True
            assert result["data"] == {"data": "test"}
    
    def test_make_request_without_headers(self):
        """Test make_request without headers parameter"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            result = APIClient.make_request("POST", "http://test.com", {"test": "data"})
            
            assert result["success"] is True
            assert result["data"] == {"data": "test"}
    
    def test_make_request_with_headers(self):
        """Test make_request with headers parameter"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            headers = {"Authorization": "Bearer token"}
            result = APIClient.make_request("POST", "http://test.com", {"test": "data"}, headers)
            
            assert result["success"] is True
            assert result["data"] == {"data": "test"}
    
    def test_make_request_connection_error(self):
        """Test make_request with connection error"""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Exception("Connection error")
            
            result = APIClient.make_request("POST", "http://test.com", {"test": "data"})
            
            assert result["success"] is False
            assert "Connection error" in result["message"]
    
    def test_make_request_json_error(self):
        """Test make_request with JSON decode error"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.side_effect = Exception("JSON decode error")
            mock_response.status_code = 200
            mock_response.content = b'invalid json'
            mock_post.return_value = mock_response
            
            result = APIClient.make_request("POST", "http://test.com", {"test": "data"})
            
            assert result["success"] is False
            assert "JSON decode error" in result["message"]

class TestStreamlitAppStructure:
    """Test cases for streamlit app structure"""
    
    def test_streamlit_app_imports(self):
        """Test that streamlit app can be imported"""
        try:
            import streamlit_app
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import streamlit_app: {e}")
    
    def test_streamlit_app_has_main_function(self):
        """Test that streamlit app has main function"""
        import streamlit_app
        assert hasattr(streamlit_app, 'main')
    
    def test_streamlit_app_has_apiclient(self):
        """Test that streamlit app has APIClient"""
        import streamlit_app
        assert hasattr(streamlit_app, 'APIClient')
    
    def test_streamlit_app_has_auth_functions(self):
        """Test that streamlit app has authentication functions"""
        import streamlit_app
        assert hasattr(streamlit_app, 'is_logged_in')
        assert hasattr(streamlit_app, 'logout')
        assert hasattr(streamlit_app, 'navigate_to')
    
    def test_streamlit_app_has_page_functions(self):
        """Test that streamlit app has page functions"""
        import streamlit_app
        assert hasattr(streamlit_app, 'show_login_page')
        assert hasattr(streamlit_app, 'show_dashboard')
        assert hasattr(streamlit_app, 'show_movies')
        assert hasattr(streamlit_app, 'show_series')
        assert hasattr(streamlit_app, 'show_personalize')
        assert hasattr(streamlit_app, 'show_chatbot') 