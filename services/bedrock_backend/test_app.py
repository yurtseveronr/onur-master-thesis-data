from botocore.exceptions import ClientError, ReadTimeoutError
# test_app.py
import pytest
from unittest.mock import Mock, patch
import json

# Mock all AWS clients before importing app
with patch('boto3.client') as mock_boto3:
    # Mock secretsmanager
    mock_secretsmanager = Mock()
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": json.dumps({
            "BEDROCK_AGENT_ID": "arn:aws:bedrock:us-east-1:123456789012:agent/test-agent",
            "BEDROCK_AGENT_ALIAS_ARN": "arn:aws:bedrock:us-east-1:123456789012:agent/test-agent/alias/test-alias"
        })
    }
    
    # Mock bedrock_agent
    mock_bedrock_agent = Mock()
    mock_bedrock_agent.describe_agent_alias.return_value = {
        "AgentAlias": {"Status": "ACTIVE"}
    }
    
    # Mock bedrock_agent_runtime
    mock_agent_rt = Mock()
    
    # Configure boto3.client to return different mocks based on service name
    def mock_client(service_name, **kwargs):
        if service_name == "secretsmanager":
            return mock_secretsmanager
        elif service_name == "bedrock-agent":
            return mock_bedrock_agent
        elif service_name == "bedrock-agent-runtime":
            return mock_agent_rt
        else:
            return Mock()
    
    mock_boto3.side_effect = mock_client
    
    from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data

def test_chat_no_json(client):
    response = client.post('/chat', data='not json')
    assert response.status_code == 400

def test_chat_no_message(client):
    response = client.post('/chat', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'required' in data['error']

def test_chat_empty_message(client):
    response = client.post('/chat', json={'message': ''})
    assert response.status_code == 400

def test_chat_whitespace_message(client):
    response = client.post('/chat', json={'message': '   '})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'empty' in data['error']

def test_chat_non_string_message(client):
    response = client.post('/chat', json={'message': 123})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'string' in data['error']

@patch('app.agent_rt')
@patch('app.AGENT_ID', 'test-agent')
@patch('app.AGENT_ALIAS_ID', 'test-alias')
def test_chat_success(mock_agent, client):
    mock_response = {
        'completion': [{'chunk': {'bytes': b'Hello!'}}]
    }
    mock_agent.invoke_agent.return_value = mock_response
    
    response = client.post('/chat', json={'message': 'Hi'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['reply'] == 'Hello!'



@patch('app.AGENT_ID', None)
def test_chat_no_agent(client):
    response = client.post('/chat', json={'message': 'Hi'})
    assert response.status_code == 503

@patch('app.agent_rt')
@patch('app.AGENT_ID', 'test-agent')
@patch('app.AGENT_ALIAS_ID', 'test-alias')
def test_chat_client_error(mock_agent, client):
    mock_agent.invoke_agent.side_effect = ClientError(
        {"Error": {"Code": "ValidationException", "Message": "Invalid"}},
        "InvokeAgent"
    )
    
    response = client.post('/chat', json={'message': 'Hi'})
    assert response.status_code == 500

@patch('app.agent_rt')
@patch('app.AGENT_ID', 'test-agent')
@patch('app.AGENT_ALIAS_ID', 'test-alias')
def test_chat_multiple_chunks(mock_agent, client):
    mock_response = {
        'completion': [
            {'chunk': {'bytes': b'Hello '}},
            {'chunk': {'bytes': b'World!'}}
        ]
    }
    mock_agent.invoke_agent.return_value = mock_response
    
    response = client.post('/chat', json={'message': 'Hi'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['reply'] == 'Hello World!'

def test_chat_invalid_json(client):
    response = client.post('/chat', 
        data='{"invalid": json}',
        content_type='application/json'
    )
    assert response.status_code == 400

def test_chat_none_message(client):
    response = client.post('/chat', json={'message': None})
    assert response.status_code == 400

def test_chat_list_message(client):
    response = client.post('/chat', json={'message': []})
    assert response.status_code == 400

def test_chat_dict_message(client):
    response = client.post('/chat', json={'message': {}})
    assert response.status_code == 400