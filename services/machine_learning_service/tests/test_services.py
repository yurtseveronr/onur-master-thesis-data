# tests/test_personalize_service.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.personalize_service import PersonalizeService
from app.models.schemas import RecommendationItem


class TestPersonalizeService:
    
    def setup_method(self):
        """Setup for each test method"""
        self.personalize_service = PersonalizeService()

    @pytest.mark.asyncio
    @patch('app.services.personalize_service.settings')
    async def test_get_recommendations_success_movies(self, mock_settings):
        """Test successful movie recommendations"""
        # Setup
        mock_settings.movies_campaign_arn = "arn:aws:personalize:us-east-1:123:campaign/movies"
        
        # Mock AWS response
        mock_response = {
            'itemList': [
                {'itemId': 'tt0111161', 'score': 0.95},
                {'itemId': 'tt0068646', 'score': 0.89},
                {'itemId': 'tt0071562', 'score': 0.85}
            ]
        }
        
        with patch.object(self.personalize_service.runtime_client, 'get_recommendations', return_value=mock_response):
            # Execute
            result = await self.personalize_service.get_recommendations(
                content_type='movies',
                user_id='test_user',
                num_results=3
            )
            
            # Assert
            assert len(result) == 3
            assert isinstance(result[0], RecommendationItem)
            assert result[0].item_id == 'tt0111161'
            assert result[0].score == 0.95

    @pytest.mark.asyncio
    @patch('app.services.personalize_service.settings')
    async def test_get_recommendations_success_series(self, mock_settings):
        """Test successful series recommendations"""
        # Setup
        mock_settings.series_campaign_arn = "arn:aws:personalize:us-east-1:123:campaign/series"
        
        # Mock AWS response
        mock_response = {
            'itemList': [
                {'itemId': 'tt0903747', 'score': 0.92},
                {'itemId': 'tt0944947', 'score': 0.88}
            ]
        }
        
        with patch.object(self.personalize_service.runtime_client, 'get_recommendations', return_value=mock_response):
            # Execute
            result = await self.personalize_service.get_recommendations(
                content_type='series',
                user_id='test_user',
                num_results=2
            )
            
            # Assert
            assert len(result) == 2
            assert result[0].item_id == 'tt0903747'
            assert result[1].score == 0.88

    @pytest.mark.asyncio
    async def test_get_recommendations_failure(self):
        """Test recommendation failure"""
        # Mock AWS exception
        with patch.object(self.personalize_service.runtime_client, 'get_recommendations', side_effect=Exception("AWS Error")):
            # Execute & Assert
            with pytest.raises(Exception) as exc_info:
                await self.personalize_service.get_recommendations(
                    content_type='movies',
                    user_id='test_user'
                )
            assert "Error getting recommendations" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('app.services.personalize_service.db')
    async def test_create_event_success_with_existing_tracker(self, mock_db):
        """Test successful event creation with existing tracker"""
        # Setup - Create a simple mock object instead of TrackerInfo
        mock_tracker = Mock()
        mock_tracker.tracker_arn = 'arn:aws:personalize:us-east-1:123:event-tracker/abc123'
        mock_db.get_tracker.return_value = mock_tracker
        
        # Mock describe_event_tracker response
        mock_describe_response = {
            'eventTracker': {
                'trackingId': 'test-tracking-id-123'
            }
        }
        
        with patch.object(self.personalize_service.personalize_client, 'describe_event_tracker', return_value=mock_describe_response), \
             patch.object(self.personalize_service.events_client, 'put_events') as mock_put_events:
            
            # Execute
            result = await self.personalize_service.create_event(
                content_type='movies',
                user_id='test_user',
                item_id='tt0111161',
                event_type='VIEW'
            )
            
            # Assert
            assert 'test_user_tt0111161_' in result
            mock_put_events.assert_called_once()
            call_args = mock_put_events.call_args
            assert call_args[1]['trackingId'] == 'test-tracking-id-123'
            assert call_args[1]['userId'] == 'test_user'
            assert len(call_args[1]['eventList']) == 1
            assert call_args[1]['eventList'][0]['itemId'] == 'tt0111161'
            assert call_args[1]['eventList'][0]['eventType'] == 'VIEW'

    @pytest.mark.asyncio
    @patch('app.services.personalize_service.db')
    @patch('app.services.personalize_service.settings')
    async def test_create_event_success_create_new_tracker(self, mock_settings, mock_db):
        """Test successful event creation with new tracker creation"""
        # Setup
        mock_db.get_tracker.return_value = None
        mock_settings.movies_dataset_arn = "arn:aws:personalize:us-east-1:123:dataset/movies"
        
        # Mock list_event_trackers (empty)
        mock_list_response = {'eventTrackers': []}
        
        # Mock create_event_tracker
        mock_create_response = {
            'eventTrackerArn': 'arn:aws:personalize:us-east-1:123:event-tracker/new123',
            'trackingId': 'new-tracking-id-456'
        }
        
        # Mock describe_event_tracker (ACTIVE status)
        mock_describe_response = {
            'eventTracker': {
                'status': 'ACTIVE'
            }
        }
        
        with patch.object(self.personalize_service.personalize_client, 'list_event_trackers', return_value=mock_list_response), \
             patch.object(self.personalize_service.personalize_client, 'create_event_tracker', return_value=mock_create_response), \
             patch.object(self.personalize_service.personalize_client, 'describe_event_tracker', return_value=mock_describe_response), \
             patch.object(self.personalize_service.events_client, 'put_events') as mock_put_events, \
             patch('time.sleep'):  # Mock sleep to speed up test
            
            # Execute
            result = await self.personalize_service.create_event(
                content_type='movies',
                user_id='test_user',
                item_id='tt0111161'
            )
            
            # Assert
            assert 'test_user_tt0111161_' in result
            mock_put_events.assert_called_once()
            mock_db.create_tracker.assert_called_once_with('movies', 'arn:aws:personalize:us-east-1:123:event-tracker/new123')

    @pytest.mark.asyncio
    @patch('app.services.personalize_service.db')
    @patch('app.services.personalize_service.settings')
    async def test_create_event_success_use_existing_listed_tracker(self, mock_settings, mock_db):
        """Test successful event creation using existing tracker from list"""
        # Setup
        mock_db.get_tracker.return_value = None
        mock_settings.series_dataset_arn = "arn:aws:personalize:us-east-1:123:dataset/series"
        
        # Mock list_event_trackers (has existing tracker)
        mock_list_response = {
            'eventTrackers': [
                {
                    'eventTrackerArn': 'arn:aws:personalize:us-east-1:123:event-tracker/existing123'
                }
            ]
        }
        
        # Mock describe_event_tracker
        mock_describe_response = {
            'eventTracker': {
                'trackingId': 'existing-tracking-id-789'
            }
        }
        
        with patch.object(self.personalize_service.personalize_client, 'list_event_trackers', return_value=mock_list_response), \
             patch.object(self.personalize_service.personalize_client, 'describe_event_tracker', return_value=mock_describe_response), \
             patch.object(self.personalize_service.events_client, 'put_events') as mock_put_events:
            
            # Execute
            result = await self.personalize_service.create_event(
                content_type='series',
                user_id='test_user',
                item_id='tt0903747'
            )
            
            # Assert
            assert 'test_user_tt0903747_' in result
            mock_put_events.assert_called_once()
            call_args = mock_put_events.call_args
            assert call_args[1]['trackingId'] == 'existing-tracking-id-789'

    @pytest.mark.asyncio
    @patch('app.services.personalize_service.db')
    async def test_create_event_success_with_existing_tracker_describe_error(self, mock_db):
        """Test event creation when existing tracker describe fails, falls back to listing"""
        # Setup - Existing tracker but describe fails
        mock_tracker = Mock()
        mock_tracker.tracker_arn = 'arn:aws:personalize:us-east-1:123:event-tracker/abc123'
        mock_db.get_tracker.return_value = mock_tracker
        
        # Mock list_event_trackers (has existing tracker)
        mock_list_response = {
            'eventTrackers': [
                {
                    'eventTrackerArn': 'arn:aws:personalize:us-east-1:123:event-tracker/fallback123'
                }
            ]
        }
        
        # Mock successful describe for fallback tracker
        mock_describe_response = {
            'eventTracker': {
                'trackingId': 'fallback-tracking-id'
            }
        }
        
        with patch.object(self.personalize_service.personalize_client, 'describe_event_tracker') as mock_describe, \
             patch.object(self.personalize_service.personalize_client, 'list_event_trackers', return_value=mock_list_response), \
             patch.object(self.personalize_service, '_get_dataset_arn', return_value='arn:aws:personalize:us-east-1:123:dataset/movies'), \
             patch.object(self.personalize_service.events_client, 'put_events') as mock_put_events:
            
            # First call (describe existing tracker) fails, second call (describe fallback) succeeds
            mock_describe.side_effect = [Exception("Describe failed"), mock_describe_response]
            
            # Execute
            result = await self.personalize_service.create_event(
                content_type='movies',
                user_id='test_user',
                item_id='tt0111161'
            )
            
            # Assert
            assert 'test_user_tt0111161_' in result
            mock_put_events.assert_called_once()
            call_args = mock_put_events.call_args
            assert call_args[1]['trackingId'] == 'fallback-tracking-id'
            mock_db.create_tracker.assert_called_once_with('movies', 'arn:aws:personalize:us-east-1:123:event-tracker/fallback123')

    @pytest.mark.asyncio
    @patch('app.services.personalize_service.db')
    @patch('app.services.personalize_service.settings')
    async def test_create_event_tracker_creation_failed_status(self, mock_settings, mock_db):
        """Test event creation when new tracker creation fails"""
        # Setup
        mock_db.get_tracker.return_value = None
        mock_settings.movies_dataset_arn = "arn:aws:personalize:us-east-1:123:dataset/movies"
        
        # Mock list_event_trackers (empty)
        mock_list_response = {'eventTrackers': []}
        
        # Mock create_event_tracker
        mock_create_response = {
            'eventTrackerArn': 'arn:aws:personalize:us-east-1:123:event-tracker/failed123',
            'trackingId': 'failed-tracking-id'
        }
        
        # Mock describe_event_tracker (CREATE FAILED status)
        mock_describe_response = {
            'eventTracker': {
                'status': 'CREATE FAILED'
            }
        }
        
        with patch.object(self.personalize_service.personalize_client, 'list_event_trackers', return_value=mock_list_response), \
             patch.object(self.personalize_service.personalize_client, 'create_event_tracker', return_value=mock_create_response), \
             patch.object(self.personalize_service.personalize_client, 'describe_event_tracker', return_value=mock_describe_response):
            
            # Execute & Assert
            with pytest.raises(Exception) as exc_info:
                await self.personalize_service.create_event(
                    content_type='movies',
                    user_id='test_user',
                    item_id='tt0111161'
                )
            assert "Event tracker creation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('app.services.personalize_service.db')
    @patch('app.services.personalize_service.settings')
    async def test_create_event_tracker_pending_then_active(self, mock_settings, mock_db):
        """Test event creation when tracker goes from PENDING to ACTIVE"""
        # Setup
        mock_db.get_tracker.return_value = None
        mock_settings.series_dataset_arn = "arn:aws:personalize:us-east-1:123:dataset/series"
        
        # Mock list_event_trackers (empty)
        mock_list_response = {'eventTrackers': []}
        
        # Mock create_event_tracker
        mock_create_response = {
            'eventTrackerArn': 'arn:aws:personalize:us-east-1:123:event-tracker/pending123',
            'trackingId': 'pending-tracking-id'
        }
        
        # Mock describe_event_tracker (first PENDING, then ACTIVE)
        mock_describe_responses = [
            {'eventTracker': {'status': 'CREATE PENDING'}},
            {'eventTracker': {'status': 'ACTIVE'}}
        ]
        
        with patch.object(self.personalize_service.personalize_client, 'list_event_trackers', return_value=mock_list_response), \
             patch.object(self.personalize_service.personalize_client, 'create_event_tracker', return_value=mock_create_response), \
             patch.object(self.personalize_service.personalize_client, 'describe_event_tracker', side_effect=mock_describe_responses), \
             patch.object(self.personalize_service.events_client, 'put_events') as mock_put_events, \
             patch('time.sleep'):  # Mock sleep to speed up test
            
            # Execute
            result = await self.personalize_service.create_event(
                content_type='series',
                user_id='test_user',
                item_id='tt0903747'
            )
            
            # Assert
            assert 'test_user_tt0903747_' in result
            mock_put_events.assert_called_once()
            mock_db.create_tracker.assert_called_once_with('series', 'arn:aws:personalize:us-east-1:123:event-tracker/pending123')

    @pytest.mark.asyncio
    async def test_get_recommendations_empty_response(self):
        """Test recommendations with empty response"""
        # Setup
        mock_response = {'itemList': []}
        
        with patch.object(self.personalize_service.runtime_client, 'get_recommendations', return_value=mock_response), \
             patch('app.services.personalize_service.settings') as mock_settings:
            mock_settings.movies_campaign_arn = "arn:aws:personalize:us-east-1:123:campaign/movies"
            
            # Execute
            result = await self.personalize_service.get_recommendations(
                content_type='movies',
                user_id='test_user'
            )
            
            # Assert
            assert len(result) == 0
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_recommendations_missing_score(self):
        """Test recommendations when score is missing"""
        # Setup
        mock_response = {
            'itemList': [
                {'itemId': 'tt0111161'},  # No score field
                {'itemId': 'tt0068646', 'score': 0.89}
            ]
        }
        
        with patch.object(self.personalize_service.runtime_client, 'get_recommendations', return_value=mock_response), \
             patch('app.services.personalize_service.settings') as mock_settings:
            mock_settings.movies_campaign_arn = "arn:aws:personalize:us-east-1:123:campaign/movies"
            
            # Execute
            result = await self.personalize_service.get_recommendations(
                content_type='movies',
                user_id='test_user'
            )
            
            # Assert
            assert len(result) == 2
            assert result[0].score == 0.0  # Default score
            assert result[1].score == 0.89

    @pytest.mark.asyncio
    async def test_create_event_with_custom_event_type(self):
        """Test event creation with custom event type"""
        # Setup
        mock_tracker = Mock()
        mock_tracker.tracker_arn = 'arn:aws:personalize:us-east-1:123:event-tracker/abc123'
        
        mock_describe_response = {
            'eventTracker': {
                'trackingId': 'test-tracking-id-123'
            }
        }
        
        with patch('app.services.personalize_service.db') as mock_db, \
             patch.object(self.personalize_service.personalize_client, 'describe_event_tracker', return_value=mock_describe_response), \
             patch.object(self.personalize_service.events_client, 'put_events') as mock_put_events:
            
            mock_db.get_tracker.return_value = mock_tracker
            
            # Execute
            result = await self.personalize_service.create_event(
                content_type='movies',
                user_id='test_user',
                item_id='tt0111161',
                event_type='LIKE'  # Custom event type
            )
            
            # Assert
            assert 'test_user_tt0111161_' in result
            call_args = mock_put_events.call_args
            assert call_args[1]['eventList'][0]['eventType'] == 'LIKE'

    def test_get_campaign_arn_movies(self):
        """Test getting campaign ARN for movies"""
        with patch('app.services.personalize_service.settings') as mock_settings:
            mock_settings.movies_campaign_arn = "arn:aws:personalize:us-east-1:123:campaign/movies"
            
            result = self.personalize_service._get_campaign_arn('movies')
            assert result == "arn:aws:personalize:us-east-1:123:campaign/movies"

    def test_get_campaign_arn_series(self):
        """Test getting campaign ARN for series"""
        with patch('app.services.personalize_service.settings') as mock_settings:
            mock_settings.series_campaign_arn = "arn:aws:personalize:us-east-1:123:campaign/series"
            
            result = self.personalize_service._get_campaign_arn('series')
            assert result == "arn:aws:personalize:us-east-1:123:campaign/series"

    def test_get_campaign_arn_invalid(self):
        """Test getting campaign ARN with invalid content type"""
        with pytest.raises(ValueError) as exc_info:
            self.personalize_service._get_campaign_arn('invalid')
        assert "Invalid content type" in str(exc_info.value)

    def test_get_dataset_arn_movies(self):
        """Test getting dataset ARN for movies"""
        with patch('app.services.personalize_service.settings') as mock_settings:
            mock_settings.movies_dataset_arn = "arn:aws:personalize:us-east-1:123:dataset/movies"
            
            result = self.personalize_service._get_dataset_arn('movies')
            assert result == "arn:aws:personalize:us-east-1:123:dataset/movies"

    def test_get_dataset_arn_series(self):
        """Test getting dataset ARN for series"""
        with patch('app.services.personalize_service.settings') as mock_settings:
            mock_settings.series_dataset_arn = "arn:aws:personalize:us-east-1:123:dataset/series"
            
            result = self.personalize_service._get_dataset_arn('series')
            assert result == "arn:aws:personalize:us-east-1:123:dataset/series"

    def test_get_dataset_arn_invalid(self):
        """Test getting dataset ARN with invalid content type"""
        with pytest.raises(ValueError) as exc_info:
            self.personalize_service._get_dataset_arn('invalid')
        assert "Invalid content type" in str(exc_info.value)