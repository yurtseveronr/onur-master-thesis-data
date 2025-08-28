from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError
from functools import wraps
import json
import traceback
from config import USER_POOL_ID, CLIENT_ID, REGION, DEBUG, PORT

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Cognito client
cognito = boto3.client('cognito-idp', region_name=REGION)

def handle_cognito_error(e: ClientError) -> tuple:
    """Handle specific Cognito errors and return appropriate responses"""
    error_code = e.response['Error']['Code']
    error_message = e.response['Error']['Message']
    
    logger.error(f"Cognito Error: {error_code} - {error_message}")
    
    error_mapping = {
        'UsernameExistsException': ('Email is already registered. If unverified, check your inbox for verification code.', 409),
        'UserNotConfirmedException': ('Please verify your email first', 400),
        'UserNotFoundException': ('Email is not registered', 404),
        'NotAuthorizedException': ('Incorrect username or password', 401),
        'CodeMismatchException': ('Invalid verification code', 400),
        'TooManyRequestsException': ('Too many attempts, please try again later', 429),
        'ExpiredCodeException': ('Verification code has expired', 400),
        'LimitExceededException': ('Attempt limit exceeded, please try again later', 429)
    }

    message, status_code = error_mapping.get(error_code, ('An unexpected error occurred', 500))
    
    return jsonify({
        'error': message,
        'error_code': error_code
    }), status_code

def validate_request(required_fields=[]):
    """Decorator for request validation"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                
                if not data:
                    logger.error("No JSON data in request")
                    return jsonify({'error': 'Request must include JSON data'}), 400

                # Check required fields
                missing_fields = [field for field in required_fields if not data.get(field)]
                if missing_fields:
                    logger.error(f"Missing fields: {missing_fields}")
                    return jsonify({
                        'error': 'Missing required fields',
                        'missing_fields': missing_fields
                    }), 400

                # Basic email validation
                if 'email' in required_fields:
                    email = data.get('email', '').strip().lower()
                    if '@' not in email or '.' not in email:
                        logger.error(f"Invalid email: {email}")
                        return jsonify({'error': 'Invalid email format'}), 400
                    data['email'] = email  # Normalize email

                # Basic password validation
                if 'password' in required_fields:
                    password = data.get('password', '')
                    if len(password) < 8:
                        logger.error("Password too short")
                        return jsonify({'error': 'Password must be at least 8 characters'}), 400

                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Request validation error: {str(e)}")
                return jsonify({'error': 'Invalid request format'}), 400
        return wrapper
    return decorator

@app.route('/auth/signup', methods=['POST'])
@validate_request(['email', 'password'])
def signup():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        logger.info(f"Signup attempt: {email}")
        
        # Direkt signup yap - Cognito kendi error handling'ini yapacak
        response = cognito.sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[{'Name': 'email', 'Value': email}]
        )

        logger.info(f"Signup successful: {email}")
        return jsonify({
            'success': True,
            'message': 'Registration successful! Please check your email for verification code.',
            'userSub': response['UserSub'],
            'requires_confirmation': True
        }), 200

    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        # Kullanici zaten varsa detayli kontrol yap
        if error_code == 'UsernameExistsException':
            try:
                # User status kontrol et
                user_info = cognito.admin_get_user(
                    UserPoolId=USER_POOL_ID,
                    Username=email
                )
                
                user_status = user_info['UserStatus']
                logger.warning(f"User exists with status: {user_status} for email: {email}")
                
                if user_status == 'UNCONFIRMED':
                    return jsonify({
                        'success': False,
                        'error': 'Email already registered but not verified. Please check your inbox for verification code.',
                        'error_code': 'USER_UNCONFIRMED',
                        'requires_confirmation': True
                    }), 400
                else:
                    return jsonify({
                        'success': False,
                        'error': 'This email is already registered and verified. Please login instead.',
                        'error_code': 'USER_EXISTS_VERIFIED'
                    }), 409
                    
            except ClientError as get_user_error:
                logger.error(f"Error getting user info: {get_user_error}")
                return handle_cognito_error(e)  # Original error
        
        return handle_cognito_error(e)
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/auth/confirm', methods=['POST'])
@validate_request(['email', 'code'])
def confirm_signup():
    try:
        data = request.get_json()
        email = data['email']
        code = data['code'].strip()

        logger.info(f"Confirmation attempt: {email}")
        
        response = cognito.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=code
        )

        logger.info(f"Confirmation successful: {email}")
        return jsonify({
            'success': True,
            'message': 'Email verified successfully! You can now login.'
        }), 200

    except ClientError as e:
        return handle_cognito_error(e)
    except Exception as e:
        logger.error(f"Confirmation error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/auth/resend', methods=['POST'])
@validate_request(['email'])
def resend_confirmation():
    try:
        data = request.get_json()
        email = data['email']

        logger.info(f"Resend confirmation attempt: {email}")
        
        response = cognito.resend_confirmation_code(
            ClientId=CLIENT_ID,
            Username=email
        )

        logger.info(f"Resend confirmation successful: {email}")
        return jsonify({
            'success': True,
            'message': 'Verification code sent again. Please check your email.'
        }), 200

    except ClientError as e:
        return handle_cognito_error(e)
    except Exception as e:
        logger.error(f"Resend confirmation error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/auth/login', methods=['POST'])
@validate_request(['email', 'password'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        logger.info(f"Login attempt: {email}")

        response = cognito.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )

        logger.info(f"Login successful: {email}")
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'token': response['AuthenticationResult']['AccessToken'],
            'user': {
                'email': email,
                'username': email.split('@')[0],
                'full_name': email.split('@')[0]
            }
        }), 200

    except ClientError as e:
        return handle_cognito_error(e)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/auth/logout', methods=['POST'])
@validate_request(['accessToken'])
def logout():
    try:
        data = request.get_json()
        access_token = data['accessToken']

        logger.info("Logout attempt")
        
        response = cognito.global_sign_out(
            AccessToken=access_token
        )

        logger.info("Logout successful")
        return jsonify({
            'success': True,
            'message': 'Successfully logged out'
        }), 200

    except ClientError as e:
        return handle_cognito_error(e)
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during logout'}), 500

@app.route('/auth/verify', methods=['POST'])
@validate_request(['email', 'code'])
def verify():
    try:
        data = request.get_json()
        email = data['email']
        verification_code = data['code'].strip()

        logger.info(f"Verify attempt: {email}")
        
        response = cognito.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            ConfirmationCode=verification_code
        )

        logger.info(f"Verification successful: {email}")
        return jsonify({
            'success': True,
            'message': 'Email verified successfully. You can now login.',
            'verified': True
        }), 200

    except ClientError as e:
        return handle_cognito_error(e)
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during verification'}), 500

# Legacy endpoints for backward compatibility
@app.route('/register', methods=['POST'])
@validate_request(['username', 'email', 'password', 'full_name'])
def register():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        logger.info(f"Legacy register attempt: {email}")
        
        response = cognito.sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[{'Name': 'email', 'Value': email}]
        )

        logger.info(f"Legacy register successful: {email}")
        return jsonify({
            'message': 'Registration successful! Please check your email for verification code.',
            'userSub': response['UserSub']
        }), 200

    except ClientError as e:
        return handle_cognito_error(e)
    except Exception as e:
        logger.error(f"Legacy register error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/login', methods=['POST'])
@validate_request(['username', 'password'])
def login_root():
    try:
        data = request.get_json()
        username = data['username']  
        password = data['password']

        logger.info(f"Legacy login attempt: {username}")

        response = cognito.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )

        logger.info(f"Legacy login successful: {username}")
        return jsonify({
            'message': 'Welcome! Login successful',
            'token': response['AuthenticationResult']['AccessToken'],
            'user': {'username': username}
        }), 200

    except ClientError as e:
        return handle_cognito_error(e)
    except Exception as e:
        logger.error(f"Legacy login error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test Cognito connection
        cognito.describe_user_pool(UserPoolId=USER_POOL_ID)
        logger.info("Health check: OK")
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'authentication'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/welcome', methods=['GET'])
def welcome():
    """Welcome endpoint"""
    logger.info("Welcome endpoint accessed")
    return jsonify({
        'status': 200,
        'message': 'Authentication Service is running',
        'service': 'authentication'
    }), 200

@app.before_request
def before_request():
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.path} from {request.remote_addr}")

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("="*50)
    logger.info("Starting Flask Authentication Service")
    logger.info(f"Debug: {DEBUG}")
    logger.info(f"Port: {PORT}")
    logger.info(f"Region: {REGION}")
    logger.info("="*50)
    
    app.run(host='0.0.0.0', debug=DEBUG, port=PORT)