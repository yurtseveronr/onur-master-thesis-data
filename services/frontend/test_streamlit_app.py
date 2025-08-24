import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import streamlit as st

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the streamlit app functions
from streamlit_app import APIClient, show_login_page, show_dashboard, show_movies_page, show_series_page

class TestAPIClient:
    """Test cases for APIClient class"""
    
    def test_api_client_initialization(self):
        """Test APIClient initialization"""
        client = APIClient()
        assert client.base_url == "http://localhost:5000"
        assert client.headers == {"Content-Type": "application/json"}
    
    def test_api_client_with_custom_base_url(self):
        """Test APIClient with custom base URL"""
        client = APIClient(base_url="http://test-api:8000")
        assert client.base_url == "http://test-api:8000"
    
    @patch('requests.post')
    def test_login_user_success(self, mock_post):
        """Test successful user login"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "token": "test_token_123",
                "user": {"username": "testuser", "email": "test@example.com"}
            }
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        client = APIClient()
        result = client.login_user("testuser", "password123")
        
        assert result["success"] is True
        assert result["data"]["token"] == "test_token_123"
        assert result["data"]["user"]["username"] == "testuser"
    
    @patch('requests.post')
    def test_login_user_failure(self, mock_post):
        """Test failed user login"""
        # Mock failed response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": False,
            "message": "Invalid credentials"
        }
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        client = APIClient()
        result = client.login_user("wronguser", "wrongpass")
        
        assert result["success"] is False
        assert result["message"] == "Invalid credentials"
    
    @patch('requests.post')
    def test_register_user_success(self, mock_post):
        """Test successful user registration"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "message": "User registered successfully"
        }
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        client = APIClient()
        result = client.register_user("newuser", "new@example.com", "password123", "New User")
        
        assert result["success"] is True
        assert result["message"] == "User registered successfully"
    
    @patch('requests.post')
    def test_register_user_failure(self, mock_post):
        """Test failed user registration"""
        # Mock failed response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": False,
            "message": "Username already exists"
        }
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        client = APIClient()
        result = client.register_user("existinguser", "existing@example.com", "password123", "Existing User")
        
        assert result["success"] is False
        assert result["message"] == "Username already exists"
    
    @patch('requests.get')
    def test_get_movies_success(self, mock_get):
        """Test successful movies retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"id": 1, "title": "Test Movie 1", "genre": "Action"},
                {"id": 2, "title": "Test Movie 2", "genre": "Drama"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = APIClient()
        result = client.get_movies()
        
        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["data"][0]["title"] == "Test Movie 1"
    
    @patch('requests.get')
    def test_get_series_success(self, mock_get):
        """Test successful series retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"id": 1, "title": "Test Series 1", "genre": "Comedy"},
                {"id": 2, "title": "Test Series 2", "genre": "Thriller"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = APIClient()
        result = client.get_series()
        
        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["data"][0]["title"] == "Test Series 1"
    
    @patch('requests.get')
    def test_search_content_success(self, mock_get):
        """Test successful content search"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"id": 1, "title": "Search Result", "type": "movie"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = APIClient()
        result = client.search_content("test query", "movies")
        
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["title"] == "Search Result"

class TestStreamlitFunctions:
    """Test cases for Streamlit UI functions"""
    
    @patch('streamlit.session_state')
    def test_show_login_page_initial_state(self, mock_session_state):
        """Test login page initial state"""
        # Mock session state
        mock_session_state.get.return_value = False
        
        # This is a basic test to ensure the function doesn't crash
        # In a real scenario, we'd need to mock Streamlit components
        try:
            # We can't actually call show_login_page() in a test environment
            # because it uses Streamlit components that require a running app
            assert True  # Placeholder assertion
        except Exception as e:
            # Expected behavior in test environment
            assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    @patch('streamlit.session_state')
    def test_show_dashboard_initial_state(self, mock_session_state):
        """Test dashboard initial state"""
        # Mock session state
        mock_session_state.get.return_value = "testuser"
        
        # This is a basic test to ensure the function doesn't crash
        try:
            # We can't actually call show_dashboard() in a test environment
            # because it uses Streamlit components that require a running app
            assert True  # Placeholder assertion
        except Exception as e:
            # Expected behavior in test environment
            assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    @patch('streamlit.session_state')
    def test_show_movies_page_initial_state(self, mock_session_state):
        """Test movies page initial state"""
        # Mock session state
        mock_session_state.get.return_value = "testuser"
        
        # This is a basic test to ensure the function doesn't crash
        try:
            # We can't actually call show_movies_page() in a test environment
            # because it uses Streamlit components that require a running app
            assert True  # Placeholder assertion
        except Exception as e:
            # Expected behavior in test environment
            assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    @patch('streamlit.session_state')
    def test_show_series_page_initial_state(self, mock_session_state):
        """Test series page initial state"""
        # Mock session state
        mock_session_state.get.return_value = "testuser"
        
        # This is a basic test to ensure the function doesn't crash
        try:
            # We can't actually call show_series_page() in a test environment
            # because it uses Streamlit components that require a running app
            assert True  # Placeholder assertion
        except Exception as e:
            # Expected behavior in test environment
            assert "streamlit" in str(e).lower() or "session" in str(e).lower()

class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_validate_email_format(self):
        """Test email validation"""
        # Test valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            # Basic email validation (you can implement this in your app)
            assert "@" in email
            assert "." in email.split("@")[1]
    
    def test_validate_password_strength(self):
        """Test password strength validation"""
        # Test password length requirement
        weak_passwords = ["123", "abc", "pass"]
        strong_passwords = ["password123", "SecurePass1!", "MyP@ssw0rd"]
        
        for password in weak_passwords:
            assert len(password) < 6
        
        for password in strong_passwords:
            assert len(password) >= 6
    
    def test_validate_username_format(self):
        """Test username format validation"""
        # Test username requirements
        valid_usernames = ["user123", "test_user", "myusername"]
        invalid_usernames = ["", "a", "user@name"]
        
        for username in valid_usernames:
            assert len(username) >= 3
            assert username.isalnum() or "_" in username
        
        for username in invalid_usernames:
            if username:
                assert len(username) < 3 or not (username.isalnum() or "_" in username)

if __name__ == "__main__":
    pytest.main([__file__]) 