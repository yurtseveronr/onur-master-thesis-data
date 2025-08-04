# app/services/personalize_service.py
import boto3
import time
from datetime import datetime
from typing import List, Dict, Any
from app.core.config import settings
from app.models.database import db
from app.models.schemas import RecommendationItem
import logging

logger = logging.getLogger(__name__)

class PersonalizeService:
    def __init__(self):
        self.runtime_client = boto3.client(
            'personalize-runtime',
            region_name=settings.aws_region
        )
        self.personalize_client = boto3.client(
            'personalize',
            region_name=settings.aws_region
        )
        self.events_client = boto3.client(
            'personalize-events',
            region_name=settings.aws_region
        )

    async def get_recommendations(
        self, 
        content_type: str, 
        user_id: str, 
        num_results: int = 10
    ) -> List[RecommendationItem]:
        """Get recommendations for a user using RELATED_ITEMS recipe"""
        try:
            campaign_arn = self._get_campaign_arn(content_type)
            logger.info(f"Getting recommendations for user {user_id}, content_type: {content_type}")
            
            # Both movies and series use RELATED_ITEMS recipe - need itemId
            response = self.runtime_client.get_recommendations(
                campaignArn=campaign_arn,
                itemId=user_id,  # Use itemId for RELATED_ITEMS recipe
                numResults=num_results
            )
            
            recommendations = [
                RecommendationItem(
                    item_id=item['itemId'],
                    score=item.get('score', 0.0)
                )
                for item in response.get('itemList', [])
            ]
            
            logger.info(f"Successfully retrieved {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise Exception(f"Error getting recommendations: {str(e)}")

    async def create_event(
        self, 
        content_type: str, 
        user_id: str, 
        item_id: str, 
        event_type: str = 'VIEW'
    ) -> str:
        """Create an event for user interaction"""
        try:
            tracking_id = await self._get_or_create_event_tracker(content_type)
            logger.info(f"Creating event for user {user_id}, item {item_id}, type: {event_type}")
            
            event_id = f"{user_id}_{item_id}_{int(time.time())}"
            event = {
                'eventId': event_id,
                'eventType': event_type,
                'itemId': item_id,
                'sentAt': datetime.utcnow().timestamp()
            }
            
            self.events_client.put_events(
                trackingId=tracking_id,
                userId=user_id,
                sessionId=f"session_{user_id}_{int(time.time())}",
                eventList=[event]
            )
            
            logger.info(f"Successfully created event {event_id} for user {user_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            raise Exception(f"Error creating event: {str(e)}")

    def _get_campaign_arn(self, content_type: str) -> str:
        """Get campaign ARN based on content type"""
        if content_type == 'movies':
            return settings.movies_campaign_arn
        elif content_type == 'series':
            return settings.series_campaign_arn
        else:
            raise ValueError(f"Invalid content type: {content_type}")

    def _get_dataset_arn(self, content_type: str) -> str:
        """Get dataset ARN based on content type"""
        if content_type == 'movies':
            return settings.movies_dataset_arn
        elif content_type == 'series':
            return settings.series_dataset_arn
        else:
            raise ValueError(f"Invalid content type: {content_type}")

    async def _get_or_create_event_tracker(self, content_type: str) -> str:
        """Get existing event tracker or create new one and return tracking ID"""
        try:
            # First check if event tracker exists in our database
            tracker = db.get_tracker(content_type)
            if tracker:
                logger.info(f"Using existing event tracker for {content_type}: {tracker.tracker_arn}")
                try:
                    # Get tracking ID from the tracker ARN
                    describe_response = self.personalize_client.describe_event_tracker(
                        eventTrackerArn=tracker.tracker_arn
                    )
                    tracking_id = describe_response['eventTracker']['trackingId']
                    logger.info(f"Retrieved tracking ID: {tracking_id}")
                    return tracking_id
                except Exception as describe_error:
                    logger.error(f"Error describing event tracker: {str(describe_error)}")
                    # If describe fails, continue to list trackers

            # Get dataset group ARN
            dataset_arn = self._get_dataset_arn(content_type)
            dataset_group_arn = dataset_arn.replace(':dataset/', ':dataset-group/')
            
            # List existing event trackers for this dataset group
            logger.info(f"Listing event trackers for dataset group: {dataset_group_arn}")
            response = self.personalize_client.list_event_trackers(
                datasetGroupArn=dataset_group_arn
            )
            
            # Check if any event trackers exist
            if response.get('eventTrackers'):
                # Use the first available event tracker
                existing_tracker = response['eventTrackers'][0]
                tracker_arn = existing_tracker['eventTrackerArn']
                logger.info(f"Found existing event tracker: {tracker_arn}")
                
                # Get tracking ID
                describe_response = self.personalize_client.describe_event_tracker(
                    eventTrackerArn=tracker_arn
                )
                tracking_id = describe_response['eventTracker']['trackingId']
                logger.info(f"Retrieved tracking ID: {tracking_id}")
                
                # Save to our database for future use
                db.create_tracker(content_type, tracker_arn)
                return tracking_id
            
            # No existing tracker found, create new one
            logger.info(f"No event tracker found, creating new one for {content_type}")
            
            create_response = self.personalize_client.create_event_tracker(
                name=f"{content_type}-event-tracker-{int(time.time())}",
                datasetGroupArn=dataset_group_arn
            )
            
            tracker_arn = create_response['eventTrackerArn']
            tracking_id = create_response['trackingId']
            logger.info(f"Event tracker created: {tracker_arn}, tracking ID: {tracking_id}")
            
            # Wait for event tracker to be ready
            logger.info("Waiting for event tracker to be active...")
            while True:
                describe_response = self.personalize_client.describe_event_tracker(
                    eventTrackerArn=tracker_arn
                )
                
                status = describe_response['eventTracker']['status']
                logger.info(f"Event tracker status: {status}")
                
                if status == 'ACTIVE':
                    logger.info("Event tracker is now active!")
                    break
                elif status == 'CREATE FAILED':
                    raise Exception("Event tracker creation failed")
                
                # Wait 10 seconds before checking again
                time.sleep(10)
            
            # Save to database
            db.create_tracker(content_type, tracker_arn)
            
            return tracking_id
            
        except Exception as e:
            logger.error(f"Error getting or creating event tracker: {str(e)}")
            raise Exception(f"Error getting or creating event tracker: {str(e)}")