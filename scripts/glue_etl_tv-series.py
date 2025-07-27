# --input_path
# --output_path
# --dynamodb_table
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType, StringType
import boto3
import os
import uuid
from decimal import Decimal
import math
import json
import pandas as pd
import numpy as np

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Get job parameters
args = getResolvedOptions(sys.argv, [
    'JOB_NAME', 
    'input_path', 
    'output_path', 
    'dynamodb_table'
])
input_path = args['input_path']
output_path = args['output_path']
dynamodb_table = args['dynamodb_table']

# Parse S3 path
if output_path.startswith('s3://'):
    output_path = output_path[5:]  # Remove s3:// prefix
parts = output_path.split('/', 1)
output_bucket = parts[0]
output_key = parts[1] if len(parts) > 1 else ""

# Read the data directly from S3
print(f"Reading TV Series data from: {input_path}")
df = spark.read.option("header", "true").option("inferSchema", "true").csv(input_path)

# Print the schema and number of records before transformation
print("Original schema:")
df.printSchema()
print(f"Original columns: {df.columns}")
print(f"Number of records: {df.count()}")

# Check if ITEM_ID exists
if "ITEM_ID" in df.columns:
    print("ITEM_ID column already exists in the data")
elif "imdbID" in df.columns:
    # Add ITEM_ID column as a copy of imdbID
    print("Adding ITEM_ID column from imdbID")
    df = df.withColumn("ITEM_ID", F.col("imdbID"))
else:
    # If neither exists, raise an exception
    raise Exception("Neither ITEM_ID nor imdbID column found in the source data. Cannot proceed.")

# Make sure imdbID exists (for DynamoDB primary key)
if "imdbID" not in df.columns:
    print("Adding imdbID column as a copy of ITEM_ID")
    df = df.withColumn("imdbID", F.col("ITEM_ID"))

# Drop completely empty rows
df = df.dropna(how='all')
print(f"Number of records after dropping empty rows: {df.count()}")

# Remove rows with missing or N/A ITEM_ID
print("Filtering out rows with missing or N/A ITEM_ID...")
df = df.filter(
    (F.col("ITEM_ID").isNotNull()) & 
    (F.col("ITEM_ID") != "") &
    (F.col("ITEM_ID") != "N/A") &
    (F.col("ITEM_ID") != "n/a") &
    (F.col("ITEM_ID") != "NA")
)
print(f"Number of records after removing rows with missing/N/A ITEM_ID: {df.count()}")

# Also filter imdbID for DynamoDB consistency
df = df.filter(
    (F.col("imdbID").isNotNull()) & 
    (F.col("imdbID") != "") &
    (F.col("imdbID") != "N/A") &
    (F.col("imdbID") != "n/a") &
    (F.col("imdbID") != "NA")
)
print(f"Number of records after removing rows with missing/N/A imdbID: {df.count()}")

# Keep Year column for DynamoDB, but ensure it's string type
if "Year" in df.columns:
    df = df.withColumn("Year", F.col("Year").cast(StringType()))
    print("Converted Year column to string type for DynamoDB")

# Convert numeric columns to the right type to match schema
if "imdbRating" in df.columns:
    df = df.withColumn("imdbRating", F.col("imdbRating").cast(FloatType()))
if "TotalSeasons" in df.columns:
    df = df.withColumn("TotalSeasons", F.col("TotalSeasons").cast(FloatType()))

# Drop the Error column if it exists
if "Error" in df.columns:
    df = df.drop("Error")
    print("Dropped Error column")

# Fill null values with appropriate defaults to avoid issues in Personalize
string_columns = ["Title", "Year", "Genre", "Director", "Actors", "Plot", "Language", "Country", "imdbVotes"]
for col_name in string_columns:
    if col_name in df.columns:
        df = df.withColumn(col_name, F.coalesce(F.col(col_name), F.lit("")))

# Create a copy for Personalize with ONLY the required schema format (Title, Genre, ITEM_ID)
personalize_df = df.select(
    F.col("ITEM_ID"),
    F.col("Title"),
    F.col("Genre")
)

# Print the final schema and count
print("Transformed schema (for DynamoDB):")
df.printSchema()
print(f"Final columns (for DynamoDB): {df.columns}")
print(f"Final record count: {df.count()}")

# Print Personalize schema
print("Personalize schema (for S3):")
personalize_df.printSchema()
print(f"Personalize columns (for S3): {personalize_df.columns}")

# Show a data sample
print("Sample data (for DynamoDB):")
df.show(5, truncate=False)
print("Personalize sample data (for S3):")
personalize_df.show(5, truncate=False)

# PART 1: Write to S3 as a single CSV file for Personalize (ONLY Title, Genre, ITEM_ID)
# -------------------------------------------------------------------------------------
# Create a temporary folder for the single CSV file
temp_folder = "/tmp/tvseries_data_" + str(uuid.uuid4())
os.makedirs(temp_folder, exist_ok=True)
temp_file = os.path.join(temp_folder, "data.csv")

# Force a single partition and write header
print(f"Writing Personalize data to single CSV file (Title, Genre, ITEM_ID only)...")
personalize_df_single = personalize_df.coalesce(1)
personalize_df_pandas = personalize_df_single.toPandas()
personalize_df_pandas.to_csv(temp_file, index=False)

# Check if the file was created and get its size
if os.path.exists(temp_file):
    file_size = os.path.getsize(temp_file)
    print(f"Created CSV file of size {file_size} bytes")
    
    # Upload the file to S3 with the exact name
    s3_client = boto3.client('s3')
    print(f"Uploading to S3: s3://{output_bucket}/{output_key}")
    s3_client.upload_file(
        Filename=temp_file,
        Bucket=output_bucket,
        Key=output_key
    )
    print(f"Successfully uploaded to s3://{output_bucket}/{output_key}")
else:
    print("ERROR: Failed to create CSV file")

# Convert the full dataframe to pandas for DynamoDB (ALL COLUMNS except Year and Error)
df_pandas = df.toPandas()

# PART 2: Write to DynamoDB (ALL COLUMNS including Year, except Error)
# --------------------------------------------------------------------
print(f"Writing FULL data to DynamoDB table: {dynamodb_table}")

# Helper function to convert pandas DataFrame to DynamoDB items
def prepare_for_dynamodb(df):
    # Replace NaN with None first
    df_clean = df.replace({np.nan: None, np.inf: None, -np.inf: None})
    
    records = df_clean.to_dict('records')
    clean_records = []
    
    for record in records:
        # New clean record
        clean_record = {}
        
        # Process each field
        for key, value in record.items():
            # Skip None values
            if value is None:
                clean_record[key] = ""
            # Convert floats to Decimal
            elif isinstance(value, float):
                # Check for NaN or Infinity
                if math.isnan(value) or math.isinf(value):
                    clean_record[key] = ""
                else:
                    clean_record[key] = Decimal(str(value))
            # Keep other types as is
            else:
                clean_record[key] = value
        
        clean_records.append(clean_record)
    
    return clean_records

# Prepare records for DynamoDB
print("Preparing records for DynamoDB...")
dynamodb_items = prepare_for_dynamodb(df_pandas)
print(f"Prepared {len(dynamodb_items)} records for DynamoDB")

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodb_table)

# Use batch writer to efficiently write items
print(f"Batch writing items to DynamoDB...")
with table.batch_writer() as batch:
    for count, item in enumerate(dynamodb_items):
        try:
            batch.put_item(Item=item)
            # Log progress for every 1000 items
            if (count + 1) % 1000 == 0:
                print(f"Processed {count + 1}/{len(dynamodb_items)} items")
        except Exception as e:
            print(f"Error writing item {count}: {e}")
            print(f"Problematic item: {item}")
            # Continue with the next item

print(f"Successfully written FULL data to DynamoDB table: {dynamodb_table}")
print("Job completed successfully")

job.commit()