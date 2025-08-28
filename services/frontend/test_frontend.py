import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the frontend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import APIClient, show_custom_message

class TestAPIClient:
    """Test APIClient class"""
    
    @patch('streamlit_app.requests.post')
    def test_register_user_success(self, mock_post):
        """Test successful user registration"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'message': 'Registration successful! You can now login.',
            'userSub': 'test-user-sub'
        }
        mock_post.return_value = mock_response
        
        result = APIClient.register_user('test@example.com', 'password123')
        
        assert result['success'] == True
        assert 'Registration successful' in result['data']['message']
        assert result['data']['userSub'] == 'test-user-sub'
    
    @patch('streamlit_app.requests.post')
    def test_register_user_exists(self, mock_post):
        """Test registration with existing user"""
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_response.json.return_value = {
            'error': 'This email is already registered and verified. Please login instead.',
            'error_code': 'USER_EXISTS_VERIFIED'
        }
        mock_post.return_value = mock_response
        
        result = APIClient.register_user('existing@example.com', 'password123')
        
        assert result['success'] == False
        assert 'already registered' in result['message']
        assert result['error_code'] == 'USER_EXISTS_VERIFIED'
    
    @patch('streamlit_app.requests.post')
    def test_login_user_success(self, mock_post):
        """Test successful user login"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'message': 'Login successful!',
            'token': 'test-token',
            'user': {
                'email': 'test@example.com',
                'username': 'test',
                'full_name': 'test'
            }
        }
        mock_post.return_value = mock_response
        
        result = APIClient.login_user('test@example.com', 'password123')
        
        assert result['success'] == True
        assert result['data']['token'] == 'test-token'
        assert result['data']['user']['email'] == 'test@example.com'
    
    @patch('streamlit_app.requests.post')
    def test_login_user_failed(self, mock_post):
        """Test failed user login"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'error': 'Incorrect username or password',
            'error_code': 'NotAuthorizedException'
        }
        mock_post.return_value = mock_response
        
        result = APIClient.login_user('test@example.com', 'wrongpassword')
        
        assert result['success'] == False
        assert 'Incorrect username or password' in result['message']
        assert result['error_code'] == 'NotAuthorizedException'

class TestMessageDisplay:
    """Test message display functions"""
    
    def test_show_custom_message_success(self):
        """Test success message display"""
        # This is a visual test, just ensure function doesn't crash
        try:
            show_custom_message("success", "Test success message")
            assert True
        except Exception as e:
            assert False, f"show_custom_message failed: {e}"
    
    def test_show_custom_message_error(self):
        """Test error message display"""
        try:
            show_custom_message("error", "Test error message")
            assert True
        except Exception as e:
            assert False, f"show_custom_message failed: {e}"
    
    def test_show_custom_message_warning(self):
        """Test warning message display"""
        try:
            show_custom_message("warning", "Test warning message")
            assert True
        except Exception as e:
            assert False, f"show_custom_message failed: {e}"
    
    def test_show_custom_message_info(self):
        """Test info message display"""
        try:
            show_custom_message("info", "Test info message")
            assert True
        except Exception as e:
            assert False, f"show_custom_message failed: {e}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 