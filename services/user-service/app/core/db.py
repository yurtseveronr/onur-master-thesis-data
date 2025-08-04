import boto3

# PROD'da sadece region olacak, endpoint_url'i silersin
dynamodb = boto3.client(
    'dynamodb',
    region_name="us-east-1",
)
