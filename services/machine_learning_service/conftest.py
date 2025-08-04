import pytest
import os

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ.update({
        'AWS_REGION': 'us-east-1',
        'SERIES_CAMPAIGN_ARN': 'test-series-campaign-arn',
        'MOVIES_CAMPAIGN_ARN': 'test-movies-campaign-arn',
        'SERIES_DATASET_ARN': 'test-series-dataset-arn',
        'MOVIES_DATASET_ARN': 'test-movies-dataset-arn',
    })