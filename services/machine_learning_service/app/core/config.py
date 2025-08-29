from pydantic_settings import BaseSettings
from typing import Optional
import os
#CONFIG
class Settings(BaseSettings):
    # App settings
    app_name: str = "Machine Learning API"
    debug: bool = True
    
    
    aws_region: str = os.getenv('AWS_REGION', 'us-east-1')
    series_campaign_arn: str = os.getenv('SERIES_CAMPAIGN_ARN', '')
    movies_campaign_arn: str = os.getenv('MOVIES_CAMPAIGN_ARN', '')
    series_dataset_arn: str = os.getenv('SERIES_DATASET_ARN', '')
    movies_dataset_arn: str = os.getenv('MOVIES_DATASET_ARN', '')
    
    # .env file'ı opsiyonel yap
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # .env yoksa hata vermesin
        validate_default = True

settings = Settings()