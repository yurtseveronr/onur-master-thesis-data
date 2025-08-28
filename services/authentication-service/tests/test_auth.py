import pytest
import json
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_cognito():
    with patch('app.cognito') as mock:
        yield mock

def create_cognito_error(error_code, message):
    """Helper function to create Cognito errors"""
    error = ClientError(
        error_response={
            'Error': {
                'Code': error_code,
                'Message': message
            }
        },
        operation_name='TestOperation'
    )
    return error

class TestSignup:
    def test_signup_success(self, client, mock_cognito):
        mock_cognito.sign_up.return_value = {
            'UserSub': 'test-user-sub-123'
        }
        mock_cognito.admin_confirm_sign_up.return_value = {}

        response = client.post('/auth/signup',
            json={'email': 'test@example.com', 'password': 'password123'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'Registration successful' in data['message']
        assert data['userSub'] == 'test-user-sub-123'

    def test_signup_missing_fields(self, client, mock_cognito):
        response = client.post('/auth/signup', json={'email': 'test@example.com'})

        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing required fields' in data['error']

    def test_signup_invalid_email(self, client, mock_cognito):
        response = client.post('/auth/signup',
            json={'email': 'invalid-email', 'password': 'password123'})

        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid email format' in data['error']

    def test_signup_short_password(self, client, mock_cognito):
        response = client.post('/auth/signup',
            json={'email': 'test@example.com', 'password': '123'})

        assert response.status_code == 400
        data = response.get_json()
        assert 'Password must be at least 8 characters' in data['error']

    def test_signup_existing_user_unconfirmed(self, client, mock_cognito):
        # sign_up raises UsernameExistsException
        mock_cognito.sign_up.side_effect = create_cognito_error(
            'UsernameExistsException',
            'User already exists'
        )
        
        # admin_get_user returns unconfirmed user
        mock_cognito.admin_get_user.return_value = {
            'UserStatus': 'UNCONFIRMED'
        }
        
        response = client.post('/auth/signup', 
            json={'email': 'existing@example.com', 'password': 'password123'})
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'already registered' in data['error']
        assert data['error_code'] == 'USER_EXISTS_VERIFIED'

    def test_signup_existing_user_confirmed(self, client, mock_cognito):
        # sign_up raises UsernameExistsException
        mock_cognito.sign_up.side_effect = create_cognito_error(
            'UsernameExistsException',
            'User already exists'
        )

        # admin_get_user returns confirmed user
        mock_cognito.admin_get_user.return_value = {
            'UserStatus': 'CONFIRMED'
        }

        response = client.post('/auth/signup',
            json={'email': 'existing@example.com', 'password': 'password123'})

        assert response.status_code == 409
        data = response.get_json()
        assert 'already registered and verified' in data['error']
        assert data['error_code'] == 'USER_EXISTS_VERIFIED'

class TestConfirmSignup:
    def test_confirm_success(self, client, mock_cognito):
        mock_cognito.confirm_sign_up.return_value = {}

        response = client.post('/auth/confirm',
            json={'email': 'test@example.com', 'code': '123456'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'verified successfully' in data['message']

    def test_confirm_invalid_code(self, client, mock_cognito):
        mock_cognito.confirm_sign_up.side_effect = create_cognito_error(
            'CodeMismatchException',
            'Invalid verification code provided'
        )

        response = client.post('/auth/confirm',
            json={'email': 'test@example.com', 'code': '999999'})

        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid verification code' in data['error']

    def test_confirm_expired_code(self, client, mock_cognito):
        mock_cognito.confirm_sign_up.side_effect = create_cognito_error(
            'ExpiredCodeException',
            'Invalid code provided, code has expired'
        )

        response = client.post('/auth/confirm',
            json={'email': 'test@example.com', 'code': '123456'})

        assert response.status_code == 400
        data = response.get_json()
        assert 'Verification code has expired' in data['error']

class TestResendConfirmation:
    def test_resend_success(self, client, mock_cognito):
        mock_cognito.resend_confirmation_code.return_value = {}

        response = client.post('/auth/resend',
            json={'email': 'test@example.com'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'sent again' in data['message']

    def test_resend_user_not_found(self, client, mock_cognito):
        mock_cognito.resend_confirmation_code.side_effect = create_cognito_error(
            'UserNotFoundException',
            'User does not exist'
        )

        response = client.post('/auth/resend',
            json={'email': 'notfound@example.com'})

        assert response.status_code == 404
        data = response.get_json()
        assert 'Email is not registered' in data['error']

class TestLogin:
    def test_login_success(self, client, mock_cognito):
        mock_cognito.initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'test-access-token-123'
            }
        }

        response = client.post('/auth/login',
            json={'email': 'test@example.com', 'password': 'password123'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'Login successful' in data['message']
        assert data['token'] == 'test-access-token-123'
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'

    def test_login_wrong_password(self, client, mock_cognito):
        mock_cognito.initiate_auth.side_effect = create_cognito_error(
            'NotAuthorizedException',
            'Incorrect username or password.'
        )

        response = client.post('/auth/login',
            json={'email': 'test@example.com', 'password': 'wrongpassword'})

        assert response.status_code == 401
        data = response.get_json()
        assert 'Incorrect username or password' in data['error']

    def test_login_unconfirmed_user(self, client, mock_cognito):
        mock_cognito.initiate_auth.side_effect = create_cognito_error(
            'UserNotConfirmedException',
            'User is not confirmed.'
        )

        response = client.post('/auth/login',
            json={'email': 'test@example.com', 'password': 'password123'})

        assert response.status_code == 400
        data = response.get_json()
        assert 'Please verify your email first' in data['error']

    def test_login_user_not_found(self, client, mock_cognito):
        mock_cognito.initiate_auth.side_effect = create_cognito_error(
            'UserNotFoundException',
            'User does not exist.'
        )

        response = client.post('/auth/login',
            json={'email': 'notfound@example.com', 'password': 'password123'})

        assert response.status_code == 404
        data = response.get_json()
        assert 'Email is not registered' in data['error']

class TestLogout:
    def test_logout_success(self, client, mock_cognito):
        mock_cognito.global_sign_out.return_value = {}

        response = client.post('/auth/logout',
            json={'accessToken': 'test-access-token'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'Successfully logged out' in data['message']

    def test_logout_invalid_token(self, client, mock_cognito):
        mock_cognito.global_sign_out.side_effect = create_cognito_error(
            'NotAuthorizedException',
            'Access Token has been revoked'
        )

        response = client.post('/auth/logout',
            json={'accessToken': 'invalid-token'})

        assert response.status_code == 401
        data = response.get_json()
        assert 'Incorrect username or password' in data['error']

class TestHealthCheck:
    def test_health_check_success(self, client, mock_cognito):
        mock_cognito.describe_user_pool.return_value = {
            'UserPool': {
                'Id': 'test-pool-id'
            }
        }

        response = client.get('/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'authentication'
        assert 'timestamp' in data

    def test_health_check_failure(self, client, mock_cognito):
        mock_cognito.describe_user_pool.side_effect = Exception('Cognito connection failed')

        response = client.get('/health')

        assert response.status_code == 500
        data = response.get_json()
        assert data['status'] == 'unhealthy'
        assert 'error' in data

class TestWelcome:
    def test_welcome(self, client):
        response = client.get('/welcome')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 200
        assert data['message'] == 'Authentication Service is running'
        assert data['service'] == 'authentication'

class TestLegacyEndpoints:
    def test_legacy_register(self, client, mock_cognito):
        mock_cognito.sign_up.return_value = {
            'UserSub': 'test-user-sub-123'
        }

        response = client.post('/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'full_name': 'Test User'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'Registration successful' in data['message']
        assert data['userSub'] == 'test-user-sub-123'

    def test_legacy_login(self, client, mock_cognito):
        mock_cognito.initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'test-access-token-123'
            }
        }

        response = client.post('/login', json={
            'username': 'test@example.com',
            'password': 'password123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'Welcome! Login successful' in data['message']
        assert data['token'] == 'test-access-token-123'

class TestErrorHandling:
    def test_invalid_json(self, client):
        response = client.post('/auth/signup', data='invalid json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid request format' in data['error']

    def test_too_many_requests(self, client, mock_cognito):
        mock_cognito.sign_up.side_effect = create_cognito_error(
            'TooManyRequestsException',
            'Too Many Requests'
        )

        response = client.post('/auth/signup',
            json={'email': 'test@example.com', 'password': 'password123'})

        assert response.status_code == 429
        data = response.get_json()
        assert 'Too many attempts' in data['error']

    def test_limit_exceeded(self, client, mock_cognito):
        mock_cognito.sign_up.side_effect = create_cognito_error(
            'LimitExceededException',
            'Attempt limit exceeded'
        )

        response = client.post('/auth/signup',
            json={'email': 'test@example.com', 'password': 'password123'})

        assert response.status_code == 429
        data = response.get_json()
        assert 'Attempt limit exceeded' in data['error']

    def test_404_endpoint(self, client):
        response = client.get('/nonexistent')

        assert response.status_code == 404
        data = response.get_json()
        assert 'Endpoint not found' in data['error']

    def test_405_method_not_allowed(self, client):
        response = client.delete('/auth/signup')

        assert response.status_code == 405
        data = response.get_json()
        assert 'Method not allowed' in data['error']

if __name__ == '__main__':
    pytest.main([__file__, '-v'])