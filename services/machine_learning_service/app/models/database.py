from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import json
import os

class EventTracker(BaseModel):
    content_type: str
    tracker_arn: str
    created_at: datetime
    updated_at: datetime

class InMemoryDB:
    """Simple in-memory database for event trackers"""
    
    def __init__(self):
        self.data_file = "event_trackers.json"
        self.trackers: Dict[str, EventTracker] = {}
        self.load_data()
    
    def load_data(self):
        """Load data from file if exists"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for content_type, tracker_data in data.items():
                        self.trackers[content_type] = EventTracker(
                            content_type=content_type,
                            tracker_arn=tracker_data['tracker_arn'],
                            created_at=datetime.fromisoformat(tracker_data['created_at']),
                            updated_at=datetime.fromisoformat(tracker_data['updated_at'])
                        )
            except Exception as e:
                print(f"Error loading data: {e}")
    
    def save_data(self):
        """Save data to file"""
        try:
            data = {}
            for content_type, tracker in self.trackers.items():
                data[content_type] = {
                    'tracker_arn': tracker.tracker_arn,
                    'created_at': tracker.created_at.isoformat(),
                    'updated_at': tracker.updated_at.isoformat()
                }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def get_tracker(self, content_type: str) -> Optional[EventTracker]:
        """Get event tracker by content type"""
        return self.trackers.get(content_type)
    
    def create_tracker(self, content_type: str, tracker_arn: str) -> EventTracker:
        """Create new event tracker"""
        now = datetime.now()
        tracker = EventTracker(
            content_type=content_type,
            tracker_arn=tracker_arn,
            created_at=now,
            updated_at=now
        )
        self.trackers[content_type] = tracker
        self.save_data()
        return tracker

# Global database instance
db = InMemoryDB()
