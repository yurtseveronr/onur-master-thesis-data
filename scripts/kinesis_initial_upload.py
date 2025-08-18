# kinesis_initial_import.py
import boto3
import json
import csv
import time
from datetime import datetime, timezone
from pathlib import Path
from botocore.exceptions import ClientError

REGION = "us-east-1"
STREAM_NAME = "onur-master-events-stream"
MOVIES_CSV = "initial_data/kinesis_movies_events.csv"
SERIES_CSV = "initial_data/kinesis_series_events.csv"

REQUIRED_FIELDS = ["event_type", "user_id", "imdbID", "title"]
DELAY_SEC = 3  

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

def read_csv(path: Path):
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    for r in rows:
        r.pop("time", None)
    return rows

def send_record(client, row):
    payload = {
        "event_type": row["event_type"],
        "user_id": row["user_id"],
        "imdbID": row["imdbID"],
        "title": row["title"],
        "time": now_iso()
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    print(data)
    try:
        client.put_record(
            StreamName=STREAM_NAME,
            Data=data,
            PartitionKey=row["user_id"] or row["imdbID"]
        )
        return True
    except ClientError as e:
        print(f"❌ Error sending record: {e}")
        return False

def process_file(client, path):
    print(f"\n📂 {path}")
    rows = read_csv(Path(path))
    total = 0
    for row in rows:
        if send_record(client, row):
            total += 1
        time.sleep(DELAY_SEC)  
    print(f"✅ {total}/{len(rows)} sent from {path}")
    return total

def main():
    client = boto3.client("kinesis", region_name=REGION)
    total = 0

    total += process_file(client, MOVIES_CSV)
    time.sleep(DELAY_SEC) 
    total += process_file(client, SERIES_CSV)

    print(f"\n🎉 DONE. Total events sent: {total}")

if __name__ == "__main__":
    main()
