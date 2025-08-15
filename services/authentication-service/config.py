import boto3
import json
import os
from botocore.exceptions import ClientError

def get_secret():
    """
    Get secret values from AWS Secrets Manager
    """
    secret_name = os.environ.get('SECRET_NAME', 'auth-app-config')
    region_name = os.environ.get('AWS_REGION', 'us-east-1')

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print(f"Error getting secret: {e}")
        # Fallback to environment variables for local development
        return {
            'USER_POOL_ID': os.environ.get('USER_POOL_ID', 'us-east-1_DUMMY'),
            'CLIENT_ID': os.environ.get('CLIENT_ID', 'dummy-client-id'),
            'REGION': os.environ.get('AWS_REGION', 'us-east-1'),
            'DEBUG': os.environ.get('DEBUG', 'True'),
            'PORT': os.environ.get('PORT', '5000')
        }
    else:
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        raise ValueError("Secret string not found in the response")

# Load configuration from AWS Secrets Manager
try:
    config = get_secret()
    
    # AWS Cognito Configuration
    USER_POOL_ID = config['USER_POOL_ID']
    CLIENT_ID = config['CLIENT_ID']
    REGION = config['REGION']

    # Flask Configuration
    DEBUG = config['DEBUG'] == 'True'
    PORT = int(config['PORT'])
    
    print(f"✅ Config loaded successfully")
    print(f"   USER_POOL_ID: {USER_POOL_ID}")
    print(f"   REGION: {REGION}")
    print(f"   DEBUG: {DEBUG}")
    print(f"   PORT: {PORT}")
    
except Exception as e:
    print(f"❌ Failed to load configuration: {e}")
    raise