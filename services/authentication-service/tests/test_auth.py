import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

### ────────────── SIGNUP TESTS ──────────────

@patch("app.cognito.sign_up")
def test_signup_success(mock_signup, client):
    # Mock başarılı response
    mock_signup.return_value = {"UserSub": "abc123"}

    response = client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "StrongPass123"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["userSub"] == "abc123"
    assert "Registration successful" in data["message"]


@patch("app.cognito.sign_up")
def test_signup_existing_user(mock_signup, client):
    # ClientError'u doğru şekilde mock'la
    mock_signup.side_effect = ClientError(
        error_response={
            "Error": {
                "Code": "UsernameExistsException",
                "Message": "User already exists"
            }
        },
        operation_name="SignUp"
    )

    response = client.post("/auth/signup", json={
        "email": "exists@example.com",
        "password": "StrongPass123"
    })

    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Email is already registered"


def test_signup_missing_email(client):
    response = client.post("/auth/signup", json={
        "password": "StrongPass123"
    })

    assert response.status_code == 400
    data = response.get_json()
    assert "Missing required fields" in data["error"]


def test_signup_invalid_email(client):
    response = client.post("/auth/signup", json={
        "email": "invalid-email",
        "password": "StrongPass123"
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid email format"


def test_signup_short_password(client):
    response = client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "123"
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Password must be at least 8 characters"


### ────────────── LOGIN TESTS ──────────────

@patch("app.cognito.initiate_auth")
def test_login_success(mock_auth, client):
    mock_auth.return_value = {
        "AuthenticationResult": {
            "AccessToken": "dummy-access-token",
            "IdToken": "dummy-id-token",
            "RefreshToken": "dummy-refresh-token"
        }
    }

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "StrongPass123"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] == True
    assert data["token"] == "dummy-access-token"
    assert data["user"]["email"] == "test@example.com"


@patch("app.cognito.initiate_auth")
def test_login_user_not_found(mock_auth, client):
    mock_auth.side_effect = ClientError(
        error_response={
            "Error": {
                "Code": "UserNotFoundException",
                "Message": "User does not exist"
            }
        },
        operation_name="InitiateAuth"
    )

    response = client.post("/auth/login", json={
        "email": "wrong@example.com",
        "password": "WrongPassword123"
    })

    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Email is not registered"


@patch("app.cognito.initiate_auth")
def test_login_wrong_password(mock_auth, client):
    mock_auth.side_effect = ClientError(
        error_response={
            "Error": {
                "Code": "NotAuthorizedException",
                "Message": "Incorrect username or password"
            }
        },
        operation_name="InitiateAuth"
    )

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPassword"
    })

    assert response.status_code == 401
    data = response.get_json()
    assert data["error"] == "Incorrect username or password"


### ────────────── VERIFY TESTS ──────────────

@patch("app.cognito.confirm_sign_up")
def test_verify_success(mock_verify, client):
    mock_verify.return_value = {}

    response = client.post("/auth/verify", json={
        "email": "test@example.com",
        "code": "123456"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["verified"] == True


@patch("app.cognito.confirm_sign_up")
def test_verify_invalid_code(mock_verify, client):
    mock_verify.side_effect = ClientError(
        error_response={
            "Error": {
                "Code": "CodeMismatchException",
                "Message": "Invalid verification code"
            }
        },
        operation_name="ConfirmSignUp"
    )

    response = client.post("/auth/verify", json={
        "email": "test@example.com",
        "code": "wrong_code"
    })

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid verification code"


### ────────────── LOGOUT TESTS ──────────────

@patch("app.cognito.global_sign_out")
def test_logout_success(mock_logout, client):
    mock_logout.return_value = {}

    response = client.post("/auth/logout", json={
        "accessToken": "dummy-token"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Successfully logged out"


### ────────────── HEALTH & WELCOME ──────────────

@patch("app.cognito.describe_user_pool")
def test_health_check_success(mock_describe, client):
    mock_describe.return_value = {"UserPool": {"Id": "test_pool"}}

    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


@patch("app.cognito.describe_user_pool")
def test_health_check_failure(mock_describe, client):
    mock_describe.side_effect = Exception("AWS connection failed")

    response = client.get('/health')
    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "unhealthy"


def test_welcome(client):
    response = client.get('/welcome')
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Welcome"


### ────────────── ERROR HANDLING TESTS ──────────────

def test_no_json_data(client):
    response = client.post("/auth/signup")
    assert response.status_code == 400


def test_empty_json(client):
    response = client.post("/auth/signup", json={})
    assert response.status_code == 400