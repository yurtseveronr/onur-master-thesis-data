import boto3
import csv
from datetime import datetime
from botocore.exceptions import ClientError

# DynamoDB client'ı başlat
dynamodb = boto3.client('dynamodb',region_name="us-east-1")

# Tablo ve CSV eşleştirmesi
UPLOAD_MAPPING = {
    "user_movies_favorites.csv": "UserMovies",
    "user_series_favorites.csv": "UserSeries"
}

def check_table_exists(table_name):
    """Check if DynamoDB table exists"""
    try:
        dynamodb.describe_table(TableName=table_name)
        print(f"✅ Table exists: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Table not found: {table_name}")
            return False
        else:
            print(f"❌ Table check error ({table_name}): {e}")
            return False

def batch_write_items(table_name, items, batch_size=25):
    """Write data to DynamoDB in batches"""
    success_count = 0
    error_count = 0
    
    # Process in groups of 25 (DynamoDB batch limit)
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        try:
            # Create batch write request
            request_items = {
                table_name: [
                    {'PutRequest': {'Item': item}} for item in batch
                ]
            }
            
            response = dynamodb.batch_write_item(RequestItems=request_items)
            
            # Retry unprocessed items if any
            unprocessed = response.get('UnprocessedItems', {})
            if unprocessed and table_name in unprocessed:
                print(f"🔄 Retrying... ({len(unprocessed[table_name])} items)")
                dynamodb.batch_write_item(RequestItems=unprocessed)
            
            success_count += len(batch)
            print(f"✅ Batch {i//batch_size + 1} completed ({len(batch)} items)")
            
        except Exception as e:
            print(f"❌ Batch {i//batch_size + 1} error: {e}")
            error_count += len(batch)
    
    return success_count, error_count

def upload_csv_to_dynamodb(csv_file, table_name):
    """Upload CSV file to DynamoDB table"""
    print(f"\n📤 {csv_file} → {table_name}")
    
    # Check table exists
    if not check_table_exists(table_name):
        return False, 0, 0
    
    try:
        items = []
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Convert CSV format to DynamoDB format
                item = {
                    'email': {'S': row['email']},
                    'imdbID': {'S': row['imdbID']},
                    'Title': {'S': row['Title']}
                }
                items.append(item)
        
        if not items:
            print("❌ CSV file is empty!")
            return False, 0, 0
        
        print(f"📊 Found {len(items)} records")
        
        # Upload to DynamoDB
        success_count, error_count = batch_write_items(table_name, items)
        
        print(f"📋 Upload Summary:")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {error_count}")
        print(f"   📊 Total: {len(items)}")
        
        return True, success_count, error_count
        
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_file}")
        return False, 0, 0
    except Exception as e:
        print(f"❌ CSV reading error: {e}")
        return False, 0, 0

def main():
    """Main function - Upload all CSVs"""
    print("🚀 === CSV to DynamoDB Uploader === 📊")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_success = 0
    total_errors = 0
    successful_uploads = 0
    
    print(f"\n" + "="*50)
    print("UPLOAD PROCESS STARTING")
    print("="*50)
    
    # Process each CSV-Table mapping
    for csv_file, table_name in UPLOAD_MAPPING.items():
        success, success_count, error_count = upload_csv_to_dynamodb(csv_file, table_name)
        
        if success:
            successful_uploads += 1
            total_success += success_count
            total_errors += error_count
    
    # Final report
    print(f"\n" + "="*50)
    print("UPLOAD RESULTS")
    print("="*50)
    
    print(f"📊 Overall Statistics:")
    print(f"   📁 Successful Uploads: {successful_uploads}/{len(UPLOAD_MAPPING)}")
    print(f"   ✅ Total Successful Records: {total_success}")
    print(f"   ❌ Total Failed Records: {total_errors}")
    
    if successful_uploads == len(UPLOAD_MAPPING):
        print(f"\n🎉 ALL CSVs UPLOADED SUCCESSFULLY!")
    else:
        print(f"\n⚠️ Some uploads failed!")
    
    print(f"\n💡 Next Steps:")
    print(f"   🔍 Check tables in AWS Console")
    print(f"   📊 Query data with SQL or NoSQL queries")

def upload_movies_only():
    """Upload only movies CSV"""
    print("🎬 Uploading movie favorites only...")
    csv_file = "user_movies_favorites.csv"
    table_name = "UserMovies"
    
    success, success_count, error_count = upload_csv_to_dynamodb(csv_file, table_name)
    
    if success:
        print(f"🎉 Movie favorites uploaded successfully! ({success_count} records)")
    else:
        print(f"❌ Movie favorites upload failed!")

def upload_series_only():
    """Upload only series CSV"""
    print("📺 Uploading series favorites only...")
    csv_file = "user_series_favorites.csv"
    table_name = "UserSeries"
    
    success, success_count, error_count = upload_csv_to_dynamodb(csv_file, table_name)
    
    if success:
        print(f"🎉 Series favorites uploaded successfully! ({success_count} records)")
    else:
        print(f"❌ Series favorites upload failed!")

def verify_uploads():
    """Verify uploaded data"""
    print("🔍 Verifying uploaded data...")
    
    for csv_file, table_name in UPLOAD_MAPPING.items():
        try:
            response = dynamodb.scan(
                TableName=table_name,
                Limit=5
            )
            
            items = response.get('Items', [])
            count = response.get('Count', 0)
            
            print(f"\n📋 {table_name} ({csv_file}):")
            print(f"   📊 Found records: {count}")
            
            if items:
                print(f"   🎬 Sample records:")
                for i, item in enumerate(items, 1):
                    title = item.get('Title', {}).get('S', 'N/A')
                    imdb_id = item.get('imdbID', {}).get('S', 'N/A')
                    print(f"      {i}. {title} ({imdb_id})")
            
        except Exception as e:
            print(f"❌ {table_name} verification error: {e}")

if __name__ == "__main__":
    main()
    
    # Alternatif kullanım:
    # upload_movies_only()    # Sadece filmler
    # upload_series_only()    # Sadece diziler  
    # verify_uploads()        # Doğrulama