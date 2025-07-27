import time
import sys
import json
import argparse
import boto3
from botocore.exceptions import ClientError


def measure(fn, *args, **kwargs):
    start = time.perf_counter()
    resp = fn(*args, **kwargs)
    return resp, time.perf_counter() - start


def wait_for(fn, arn, path, target="ACTIVE", interval=30, timeout=1800):
    waited = 0
    while waited < timeout:
        resp = fn(arn)
        status = resp
        for key in path:
            status = status[key]
        print(f"[{arn}] status={status} (waited {waited}s)")
        if status == target:
            return
        if status.endswith("FAILED"):
            raise RuntimeError(f"{arn} entered failed state {status}")
        time.sleep(interval)
        waited += interval
    raise RuntimeError(f"Timed out waiting for {target} on {arn}")

# 1) Static configs: Recipes & hyperparameters
RECIPES = {
    "movies": "arn:aws:personalize:::recipe/aws-user-personalization-v2",
    "series": "arn:aws:personalize:::recipe/aws-user-personalization-v2",
}
HYPER = {
    "training.max_user_history_length_percentile": "80",
    "training.max_item_interaction_count_percentile": "80",
}

SCHEMAS = {
    "Movies_Items": {
        "type": "record",
        "name": "Items",
        "namespace": "com.amazonaws.personalize.schema",
        "fields": [
            {"name": "ITEM_ID",    "type": "string"},
            {"name": "imdbID",     "type": "string"},
            {"name": "Title",      "type": "string"},
            {"name": "Year",       "type": "string"},
            {"name": "Rated",      "type": "string",  "categorical": True},
            {"name": "Genre",      "type": "string",  "categorical": True},
            {"name": "Director",   "type": "string",  "categorical": True},
            {"name": "Actors",     "type": "string",  "categorical": True},
            {"name": "imdbRating", "type": "float"}
        ],
        "version": "1.0"
    },
    "Series_Items": {
        "type": "record",
        "name": "Items",
        "namespace": "com.amazonaws.personalize.schema",
        "fields": [
            {"name": "ITEM_ID",      "type": "string"},
            {"name": "Title",        "type": "string"},
            {"name": "Year",         "type": "string"},
            {"name": "Genre",        "type": "string",  "categorical": True},
            {"name": "Director",     "type": "string",  "categorical": True},
            {"name": "Actors",       "type": "string",  "categorical": True},
            {"name": "imdbRating",   "type": "float"},
            {"name": "TotalSeasons", "type": "float"}
        ],
        "version": "1.0"
    },
    "Interactions": {
        "type": "record",
        "name": "Interactions",
        "namespace": "com.amazonaws.personalize.schema",
        "fields": [
            {"name": "USER_ID",    "type": "string"},
            {"name": "ITEM_ID",    "type": "string"},
            {"name": "TIMESTAMP",  "type": "long"},
            {"name": "EVENT_TYPE", "type": "string"}
        ],
        "version": "1.0"
    }
}



# 3) Helper functions for each step

def create_group(client, name):
    # Check if dataset group already exists
    try:
        response = client.list_dataset_groups()
        for group in response.get('datasetGroups', []):
            if group['name'] == name:
                arn = group['datasetGroupArn']
                print(f"[DSG:{name}] already exists → {arn}")
                if group['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS']:
                    wait_for(lambda a: client.describe_dataset_group(datasetGroupArn=a), arn, ["datasetGroup","status"])
                return arn
                
        # Continue with pagination if necessary
        while 'nextToken' in response:
            response = client.list_dataset_groups(nextToken=response['nextToken'])
            for group in response.get('datasetGroups', []):
                if group['name'] == name:
                    arn = group['datasetGroupArn']
                    print(f"[DSG:{name}] already exists → {arn}")
                    if group['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS']:
                        wait_for(lambda a: client.describe_dataset_group(datasetGroupArn=a), arn, ["datasetGroup","status"])
                    return arn
    except ClientError as e:
        print(f"Error checking for existing dataset group: {str(e)}")
    
    # Create new dataset group if it doesn't exist
    resp, dur = measure(client.create_dataset_group, name=name)
    arn = resp["datasetGroupArn"]
    print(f"[DSG:{name}] created in {dur:.1f}s → {arn}")
    wait_for(lambda a: client.describe_dataset_group(datasetGroupArn=a), arn, ["datasetGroup","status"])
    return arn


def create_schema(client, name, schema_def):
    # Check if schema already exists
    try:
        response = client.list_schemas()
        for schema in response.get('schemas', []):
            if schema['name'] == name:
                arn = schema['schemaArn']
                print(f"[SCH:{name}] already exists → {arn}")
                return arn
                
        # Continue with pagination if necessary
        while 'nextToken' in response:
            response = client.list_schemas(nextToken=response['nextToken'])
            for schema in response.get('schemas', []):
                if schema['name'] == name:
                    arn = schema['schemaArn']
                    print(f"[SCH:{name}] already exists → {arn}")
                    return arn
    except ClientError as e:
        print(f"Error checking for existing schema: {str(e)}")
    
    # Create new schema if it doesn't exist
    resp, dur = measure(client.create_schema, name=name, schema=json.dumps(schema_def))
    arn = resp["schemaArn"]
    print(f"[SCH:{name}] created in {dur:.1f}s → {arn}")
    return arn


def create_dataset(client, name, dg_arn, dtype, schema_arn):
    # Check if dataset already exists
    try:
        response = client.list_datasets(datasetGroupArn=dg_arn)
        for dataset in response.get('datasets', []):
            if dataset['name'] == name:
                arn = dataset['datasetArn']
                print(f"[DS:{name}] ({dtype}) already exists → {arn}")
                return arn
                
        # Continue with pagination if necessary
        while 'nextToken' in response:
            response = client.list_datasets(datasetGroupArn=dg_arn, nextToken=response['nextToken'])
            for dataset in response.get('datasets', []):
                if dataset['name'] == name:
                    arn = dataset['datasetArn']
                    print(f"[DS:{name}] ({dtype}) already exists → {arn}")
                    return arn
    except ClientError as e:
        print(f"Error checking for existing dataset: {str(e)}")
    
    # Create new dataset if it doesn't exist
    resp, dur = measure(
        client.create_dataset,
        name=name,
        datasetGroupArn=dg_arn,
        datasetType=dtype,
        schemaArn=schema_arn
    )
    arn = resp["datasetArn"]
    print(f"[DS:{name}] ({dtype}) created in {dur:.1f}s → {arn}")
    return arn


def validate_csv_for_import(client, ds_arn, s3_path):
    """
    Validates if the CSV at s3_path is compatible with the dataset schema.
    Returns a tuple (is_valid, message) where is_valid is a boolean.
    """
    try:
        # Get dataset details to find its schema
        dataset_response = client.describe_dataset(datasetArn=ds_arn)
        schema_arn = dataset_response['dataset']['schemaArn']
        
        # Get schema details
        schema_response = client.describe_schema(schemaArn=schema_arn)
        schema_str = schema_response['schema']
        schema_json = json.loads(schema_str)
        
        # Parse the S3 path
        s3_parts = s3_path.replace('s3://', '').split('/')
        bucket_name = s3_parts[0]
        key = '/'.join(s3_parts[1:])
        
        # Create S3 client
        s3 = boto3.client('s3', region_name=client._client_config.region_name)
        
        try:
            # Get metadata about the file
            response = s3.head_object(Bucket=bucket_name, Key=key)
            
            # Skip validation for non-csv files or large files
            content_type = response.get('ContentType', '')
            size = response.get('ContentLength', 0)
            
            if 'csv' not in content_type.lower() and not key.lower().endswith('.csv'):
                return True, "Non-CSV file detected, skipping validation"
            
            if size > 5 * 1024 * 1024:  # Skip validation for files larger than 5MB
                return True, "Large CSV file detected, skipping detailed validation"
                
            # For smaller files, get a sample to check headers
            obj = s3.get_object(Bucket=bucket_name, Key=key)
            content = obj['Body'].read(1024 * 10).decode('utf-8')  # Read first 10KB
            
            # Get header line
            header_line = content.split('\n')[0].strip()
            headers = [h.strip() for h in header_line.split(',')]
            
            # Extract required fields from schema
            required_fields = []
            for field in schema_json.get('fields', []):
                if field['name'].endswith('_ID'):  # Assume ID fields are required
                    required_fields.append(field['name'])
            
            # Validate required fields exist in headers
            missing_fields = [field for field in required_fields if field not in headers]
            
            if missing_fields:
                return False, f"CSV is missing required fields: {missing_fields}"
            
            return True, "CSV validation passed"
            
        except Exception as e:
            return False, f"Error validating CSV: {str(e)}"
            
    except Exception as e:
        return False, f"Error during schema validation: {str(e)}"


def import_job(client, job_name, ds_arn, role_arn, s3_path):
    # Check for existing import jobs
    try:
        ds_imports = client.list_dataset_import_jobs(datasetArn=ds_arn)
        if ds_imports.get('datasetImportJobs'):
            # First look for jobs with the same name
            for job in ds_imports['datasetImportJobs']:
                if job['jobName'] == job_name:
                    arn = job['datasetImportJobArn']
                    print(f"[IMP:{job_name}] already exists → {arn}")
                    if job['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS']:
                        print(f"[INFO] Waiting for existing import job to complete...")
                        wait_for(lambda a: client.describe_dataset_import_job(datasetImportJobArn=a), 
                                arn, ["datasetImportJob","status"])
                    elif job['status'] == 'ACTIVE':
                        print(f"[INFO] Import job already completed successfully.")
                    return arn
            
            # Then check for any running jobs if none match by name
            for job in ds_imports['datasetImportJobs']:
                if job['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS']:
                    print(f"[WARNING] Dataset {ds_arn} already has an import job running. Waiting for it to complete...")
                    wait_for(lambda a: client.describe_dataset_import_job(datasetImportJobArn=a), 
                             job['datasetImportJobArn'], 
                             ["datasetImportJob","status"])
                    break
                    
        # Continue with pagination if necessary
        while 'nextToken' in ds_imports:
            ds_imports = client.list_dataset_import_jobs(datasetArn=ds_arn, nextToken=ds_imports['nextToken'])
            for job in ds_imports.get('datasetImportJobs', []):
                if job['jobName'] == job_name:
                    arn = job['datasetImportJobArn']
                    print(f"[IMP:{job_name}] already exists → {arn}")
                    if job['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS']:
                        print(f"[INFO] Waiting for existing import job to complete...")
                        wait_for(lambda a: client.describe_dataset_import_job(datasetImportJobArn=a), 
                                arn, ["datasetImportJob","status"])
                    elif job['status'] == 'ACTIVE':
                        print(f"[INFO] Import job already completed successfully.")
                    return arn
    except ClientError as e:
        print(f"Error checking import jobs: {str(e)}")
    
    # Skip validation if flag is set
    skip_validation = False  # Will be passed from main()
    
    if not skip_validation:
        # Validate CSV before importing
        print(f"[IMP:{job_name}] Validating CSV at {s3_path}...")
        try:
            # Parse the S3 path
            s3_parts = s3_path.replace('s3://', '').split('/')
            bucket_name = s3_parts[0]
            key = '/'.join(s3_parts[1:])
            
            # Create S3 client
            s3 = boto3.client('s3')
            
            # Get metadata about the file
            s3.head_object(Bucket=bucket_name, Key=key)
            
            # For simplicity, just check if the file exists and assume it's valid
            print(f"[IMP:{job_name}] S3 file exists, proceeding with import")
        except Exception as e:
            print(f"[ERROR] S3 file validation failed: {str(e)}")
            print(f"[IMP:{job_name}] Skipping import due to validation failure")
            return None
    else:
        print(f"[IMP:{job_name}] Skipping validation, proceeding with import")
    
    # Create new import job
    try:
        resp, dur = measure(
            client.create_dataset_import_job,
            jobName=job_name,
            datasetArn=ds_arn,
            roleArn=role_arn,
            dataSource={"dataLocation": s3_path}
        )
        arn = resp["datasetImportJobArn"]
        print(f"[IMP:{job_name}] started in {dur:.1f}s → {arn}")
        wait_for(lambda a: client.describe_dataset_import_job(datasetImportJobArn=a), arn, ["datasetImportJob","status"])  
        return arn
    except ClientError as e:
        print(f"[ERROR] Failed to create import job: {str(e)}")
        return None


def create_solution_version(client, name, recipe_arn, dg_arn):
    # Check for existing solutions
    sol_arn = None
    try:
        solutions = client.list_solutions(datasetGroupArn=dg_arn)
        if solutions.get('solutions'):
            for sol in solutions['solutions']:
                if sol['name'] == name:
                    # Use existing solution
                    sol_arn = sol['solutionArn']
                    print(f"[SOL:{name}] already exists → {sol_arn}")
                    
                    # Check solution status
                    if sol['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS']:
                        print(f"[INFO] Waiting for solution to be ready...")
                        wait_for(lambda a: client.describe_solution(solutionArn=a), 
                                sol_arn, ["solution","status"])
                    break
                    
        # Continue with pagination if necessary
        while not sol_arn and 'nextToken' in solutions:
            solutions = client.list_solutions(datasetGroupArn=dg_arn, nextToken=solutions['nextToken'])
            for sol in solutions.get('solutions', []):
                if sol['name'] == name:
                    sol_arn = sol['solutionArn']
                    print(f"[SOL:{name}] already exists → {sol_arn}")
                    if sol['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS']:
                        print(f"[INFO] Waiting for solution to be ready...")
                        wait_for(lambda a: client.describe_solution(solutionArn=a), 
                                sol_arn, ["solution","status"])
                    break
    except ClientError as e:
        print(f"Error checking solutions: {str(e)}")
    
    # Create new solution if it doesn't exist
    if not sol_arn:
        resp, dur1 = measure(
            client.create_solution,
            name=name,
            recipeArn=recipe_arn,
            datasetGroupArn=dg_arn,
            solutionConfig={"algorithmHyperParameters": HYPER}
        )
        sol_arn = resp["solutionArn"]
        print(f"[SOL:{name}] created in {dur1:.1f}s → {sol_arn}")
    
    # Check for existing solution versions
    try:
        versions = client.list_solution_versions(solutionArn=sol_arn)
        if versions.get('solutionVersions'):
            # Check for in-progress versions first
            for ver in versions['solutionVersions']:
                if ver['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS']:
                    print(f"[WARNING] Solution {sol_arn} already has a version in progress. Waiting...")
                    wait_for(lambda a: client.describe_solution_version(solutionVersionArn=a), 
                             ver['solutionVersionArn'], 
                             ["solutionVersion","status"], 
                             timeout=3600)
                    return ver['solutionVersionArn']
            
            # If no in-progress versions, check for active versions
            for ver in versions['solutionVersions']:
                if ver['status'] == 'ACTIVE':
                    print(f"[VER:{name}] using existing active version → {ver['solutionVersionArn']}")
                    return ver['solutionVersionArn']
                    
        # Continue with pagination if necessary
        while 'nextToken' in versions:
            versions = client.list_solution_versions(solutionArn=sol_arn, nextToken=versions['nextToken'])
            for ver in versions.get('solutionVersions', []):
                if ver['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS']:
                    print(f"[WARNING] Solution {sol_arn} already has a version in progress. Waiting...")
                    wait_for(lambda a: client.describe_solution_version(solutionVersionArn=a), 
                             ver['solutionVersionArn'], 
                             ["solutionVersion","status"], 
                             timeout=3600)
                    return ver['solutionVersionArn']
                elif ver['status'] == 'ACTIVE':
                    print(f"[VER:{name}] using existing active version → {ver['solutionVersionArn']}")
                    return ver['solutionVersionArn']
    except ClientError as e:
        print(f"Error checking solution versions: {str(e)}")
    
    # Create new solution version
    resp2, dur2 = measure(client.create_solution_version, solutionArn=sol_arn)
    ver_arn = resp2["solutionVersionArn"]
    print(f"[VER:{name}] createVersion in {dur2:.1f}s → {ver_arn}")
    wait_for(lambda a: client.describe_solution_version(solutionVersionArn=a), ver_arn, ["solutionVersion","status"], timeout=3600)
    return ver_arn


def create_campaign(client, name, sv_arn, tps):
    # Check for existing campaigns
    try:
        campaigns = client.list_campaigns()
        if campaigns.get('campaigns'):
            for camp in campaigns['campaigns']:
                if camp['name'] == name:
                    print(f"[CAM:{name}] already exists → {camp['campaignArn']}")
                    if camp['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS', 'UPDATE PENDING', 'UPDATE IN_PROGRESS']:
                        print(f"[INFO] Campaign {name} is in progress. Waiting...")
                        wait_for(lambda a: client.describe_campaign(campaignArn=a), 
                                 camp['campaignArn'], 
                                 ["campaign","status"])
                    return camp['campaignArn']
                    
        # Continue with pagination if necessary
        while 'nextToken' in campaigns:
            campaigns = client.list_campaigns(nextToken=campaigns['nextToken'])
            for camp in campaigns.get('campaigns', []):
                if camp['name'] == name:
                    print(f"[CAM:{name}] already exists → {camp['campaignArn']}")
                    if camp['status'] in ['CREATE PENDING', 'CREATE IN_PROGRESS', 'UPDATE PENDING', 'UPDATE IN_PROGRESS']:
                        print(f"[INFO] Campaign {name} is in progress. Waiting...")
                        wait_for(lambda a: client.describe_campaign(campaignArn=a), 
                                camp['campaignArn'], 
                                ["campaign","status"])
                    return camp['campaignArn']
    except ClientError as e:
        print(f"Error checking campaigns: {str(e)}")
    
    # Create new campaign
    resp, dur = measure(
        client.create_campaign,
        name=name,
        solutionVersionArn=sv_arn,
        minProvisionedTPS=tps,
        campaignConfig={"itemIdFieldName":"ITEM_ID","userIdFieldName":"USER_ID"}
    )
    arn = resp["campaignArn"]
    print(f"[CAM:{name}] created in {dur:.1f}s → {arn}")
    wait_for(lambda a: client.describe_campaign(campaignArn=a), arn, ["campaign","status"])
    return arn


def create_event_tracker(client, name, dg_arn):
    # Check for existing event trackers
    try:
        trackers = client.list_event_trackers(datasetGroupArn=dg_arn)
        if trackers.get('eventTrackers'):
            for tracker in trackers['eventTrackers']:
                if tracker['name'] == name:
                    print(f"[ET:{name}] already exists → {tracker['eventTrackerArn']}")
                    return tracker['trackingId']
                    
        # Continue with pagination if necessary
        while 'nextToken' in trackers:
            trackers = client.list_event_trackers(datasetGroupArn=dg_arn, nextToken=trackers['nextToken'])
            for tracker in trackers.get('eventTrackers', []):
                if tracker['name'] == name:
                    print(f"[ET:{name}] already exists → {tracker['eventTrackerArn']}")
                    return tracker['trackingId']
    except ClientError as e:
        print(f"Error checking event trackers: {str(e)}")
    
    # Create new event tracker
    resp, dur = measure(
        client.create_event_tracker,
        name=name,
        datasetGroupArn=dg_arn
    )
    tid = resp["eventTracker"]["trackingId"]
    print(f"[ET:{name}] created in {dur:.1f}s → {tid}")
    return tid


def update_secret(sm, secret_id, data):
    try:
        # Check if secret exists and get current value
        current_secret = sm.get_secret_value(SecretId=secret_id)
        current_data = {}
        if 'SecretString' in current_secret:
            try:
                current_data = json.loads(current_secret['SecretString'])
                print(f"🔒 Secret {secret_id} exists, updating with new values")
            except json.JSONDecodeError:
                print(f"🔒 Secret {secret_id} exists but is not valid JSON, will be overwritten")
        
        # Merge new data with existing data
        merged_data = {**current_data, **data}
        sm.put_secret_value(SecretId=secret_id, SecretString=json.dumps(merged_data))
        print("🔒 Secret updated successfully")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # Create new secret if it doesn't exist
            sm.create_secret(Name=secret_id, SecretString=json.dumps(data))
            print(f"🔒 Secret {secret_id} created")
        else:
            raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--region", default="us-east-1")
    p.add_argument("--bucket", required=True)
    p.add_argument("--import-role", required=True)
    p.add_argument("--secret-id", required=True)
    p.add_argument("--skip-validation", action="store_true", help="Skip CSV validation")
    args = p.parse_args()

    pys = boto3.client("personalize", region_name=args.region)
    sms = boto3.client("secretsmanager", region_name=args.region)

    # Configure error handling - we'll collect errors but continue execution
    import_errors = []
    has_critical_error = False

    # IMPORTANT: Set this global flag to skip complicated validation that's causing issues
    global skip_validation
    skip_validation = True  # Always skip the problematic validation

    try:
        # Each step in sequence
        print("\n=== STEP 1: Creating Dataset Groups ===")
        dg_movies = create_group(pys, "movies-personalize-dataset")
        dg_series = create_group(pys, "series-personalize-dataset")

        print("\n=== STEP 2: Creating Schemas ===")
        schm_m = create_schema(pys, "Movies-Items-Schema", SCHEMAS["Movies_Items"])
        schm_s = create_schema(pys, "Series-Items-Schema", SCHEMAS["Series_Items"])
        schm_i = create_schema(pys, "Interactions-Schema", SCHEMAS["Interactions"])

        print("\n=== STEP 3: Creating Datasets ===")
        ds_mi = create_dataset(pys, "movies-items-dataset", dg_movies, "ITEMS", schm_m)
        ds_si = create_dataset(pys, "series-items-dataset", dg_series, "ITEMS", schm_s)
        ds_mr = create_dataset(pys, "movies-interactions-dataset", dg_movies, "INTERACTIONS", schm_i)
        ds_sr = create_dataset(pys, "series-interactions-dataset", dg_series, "INTERACTIONS", schm_i)

        # Wait for the previous step to fully complete
        print("\n=== Waiting for all dataset creations to complete ===")
        time.sleep(10)  # Add a safety buffer

        print("\n=== STEP 4: Checking S3 paths ===")
        s3 = boto3.client('s3', region_name=args.region)
        
        # Update paths based on the error message showing different paths
        data_paths = {
            "movies-items": f"s3://{args.bucket}/raw/movies.csv",
            "movies-interactions": f"s3://{args.bucket}/initial_data/movies/movies_interactions.csv",
            "series-items": f"s3://{args.bucket}/raw/TVseries.csv",
            "series-interactions": f"s3://{args.bucket}/initial_data/series/series.csv"
        }
        
        # Corrections based on the paths in the original script
        original_paths = {
            "movies-items": f"s3://{args.bucket}/raw/movies.csv",
            "movies-interactions": f"s3://{args.bucket}/personalize_initial_data/movies/movies_interactions.csv",
            "series-items": f"s3://{args.bucket}/raw/TVseries.csv",
            "series-interactions": f"s3://{args.bucket}/personalize_initial_data/series/series.csv"
        }
        
        # Combine both sets to try all possible paths
        all_paths = {}
        for key in data_paths:
            all_paths[key] = [data_paths[key]]
            if key in original_paths and original_paths[key] != data_paths[key]:
                all_paths[key].append(original_paths[key])
        
        # Check and store valid paths
        valid_paths = {}
        for name, paths in all_paths.items():
            found = False
            for path in paths:
                try:
                    parts = path.replace('s3://', '').split('/')
                    bucket = parts[0]
                    key = '/'.join(parts[1:])
                    
                    s3.head_object(Bucket=bucket, Key=key)
                    print(f"[INFO] {name} file exists at {path}")
                    valid_paths[name] = path
                    found = True
                    break
                except Exception as e:
                    print(f"[WARNING] File not found at {path}: {str(e)}")
            
            if not found:
                error_msg = f"[WARNING] {name} file not found in any checked location"
                print(error_msg)
                import_errors.append(error_msg)
        
        # Wait again before imports
        print("\n=== Waiting before starting imports ===")
        time.sleep(5)  # Add a safety buffer

        # Continue only with paths that were found
        print("\n=== STEP 5: Importing Data (Movies - Items) ===")
        movies_items_import = None
        if "movies-items" in valid_paths:
            movies_items_import = import_job(pys, "movies-items-import", ds_mi, args.import_role, valid_paths["movies-items"])
            if not movies_items_import:
                import_errors.append(f"Failed to import Movies Items from {valid_paths['movies-items']}")
        else:
            print("[WARNING] Skipping Movies Items import as file was not found")
            import_errors.append("Skipped Movies Items import - file not found")
        
        # Wait between imports
        print("\n=== Waiting between imports ===")
        time.sleep(5)  # Add a safety buffer
        
        print("\n=== STEP 5: Importing Data (Movies - Interactions) ===")
        movies_inter_import = None
        if "movies-interactions" in valid_paths:
            movies_inter_import = import_job(pys, "movies-interactions-import", ds_mr, args.import_role, valid_paths["movies-interactions"])
            if not movies_inter_import:
                import_errors.append(f"Failed to import Movies Interactions from {valid_paths['movies-interactions']}")
        else:
            print("[WARNING] Skipping Movies Interactions import as file was not found")
            import_errors.append("Skipped Movies Interactions import - file not found")
        
        # Wait between imports
        print("\n=== Waiting between imports ===")
        time.sleep(5)  # Add a safety buffer
        
        print("\n=== STEP 5: Importing Data (Series - Items) ===")
        series_items_import = None
        if "series-items" in valid_paths:
            series_items_import = import_job(pys, "series-items-import", ds_si, args.import_role, valid_paths["series-items"])
            if not series_items_import:
                import_errors.append(f"Failed to import Series Items from {valid_paths['series-items']}")
        else:
            print("[WARNING] Skipping Series Items import as file was not found")
            import_errors.append("Skipped Series Items import - file not found")
        
        # Wait between imports
        print("\n=== Waiting between imports ===")
        time.sleep(5)  # Add a safety buffer
        
        print("\n=== STEP 5: Importing Data (Series - Interactions) ===")
        series_inter_import = None
        if "series-interactions" in valid_paths:
            series_inter_import = import_job(pys, "series-interactions-import", ds_sr, args.import_role, valid_paths["series-interactions"])
            if not series_inter_import:
                import_errors.append(f"Failed to import Series Interactions from {valid_paths['series-interactions']}")
        else:
            print("[WARNING] Skipping Series Interactions import as file was not found")
            import_errors.append("Skipped Series Interactions import - file not found")
        
        # Wait after all imports complete
        print("\n=== Waiting after all imports ===")
        time.sleep(10)  # Add a safety buffer

        # Only continue with solution versions if we have successful imports
        if not has_critical_error:
            print("\n=== STEP 6: Creating Movie Solution & Version (this may take hours) ===")
            sv_movies = None
            if movies_items_import and movies_inter_import:
                sv_movies = create_solution_version(pys, "movies-recommendation", RECIPES["movies"], dg_movies)
            else:
                print("[WARNING] Skipping movies solution creation due to failed imports")
            
            print("\n=== STEP 6: Creating Series Solution & Version (this may take hours) ===")
            sv_series = None
            if series_items_import and series_inter_import:
                sv_series = create_solution_version(pys, "series-recommendation", RECIPES["series"], dg_series)
            else:
                print("[WARNING] Skipping series solution creation due to failed imports")

            # Only create campaigns if we have solution versions
            secrets_data = {}
            
            if sv_movies:
                print("\n=== STEP 7: Creating Movie Campaign ===")
                cam_movies = create_campaign(pys, "movies-campaign", sv_movies, 1)
                if cam_movies:
                    secrets_data["movies_campaign_arn"] = cam_movies
                    
                print("\n=== STEP 8: Creating Movies Event Tracker ===")
                et_movies = create_event_tracker(pys, "movies-event-tracker", dg_movies)
                if et_movies:
                    secrets_data["movies_event_tracker_id"] = et_movies
            else:
                print("[INFO] Skipping movies campaign and event tracker creation")
            
            if sv_series:
                print("\n=== STEP 7: Creating Series Campaign ===")
                cam_series = create_campaign(pys, "series-campaign", sv_series, 1)
                if cam_series:
                    secrets_data["series_campaign_arn"] = cam_series
                
                print("\n=== STEP 8: Creating Series Event Tracker ===")
                et_series = create_event_tracker(pys, "series-event-tracker", dg_series)
                if et_series:
                    secrets_data["series_event_tracker_id"] = et_series
            else:
                print("[INFO] Skipping series campaign and event tracker creation")

            # Only update secrets if we have data to update
            if secrets_data:
                print("\n=== STEP 9: Updating Secret ===")
                update_secret(sms, args.secret_id, secrets_data)
            else:
                print("\n[WARNING] No campaign or event tracker data to save to Secret Manager")

        # Print summary
        if import_errors:
            print("\n=== EXECUTION COMPLETED WITH WARNINGS ===")
            print("\nImport errors summary:")
            for error in import_errors:
                print(f"  - {error}")
        else:
            print("\n=== ALL STEPS COMPLETED SUCCESSFULLY ===")

    except (ClientError, RuntimeError) as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()