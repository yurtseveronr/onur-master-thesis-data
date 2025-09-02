import boto3


dynamodb = boto3.client(
    'dynamodb',
    region_name="us-east-1",
)
