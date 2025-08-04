# test_unit.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routes.favorites_routes import router  # favorites_routes.py dosyası
from app.services.favorites_service import FavoritesService
from app.repositories.favorites_repository import FavoritesRepository

# Test app setup
app = FastAPI()
app.include_router(router, prefix="/api")
client = TestClient(app)

# Test data
TEST_EMAIL = "test@example.com"
TEST_MOVIE_TITLE = "Test Movie"
TEST_SERIES_TITLE = "Test Series"
TEST_IMDB_ID = "tt1234567"

class TestFavoritesRepository:
    """Test FavoritesRepository class"""
    
    @patch('app.repositories.favorites_repository.dynamodb')
    def test_get_imdb_id_from_title_success(self, mock_dynamodb):
        """Test successful IMDB ID retrieval"""
        # Mock DynamoDB response
        mock_dynamodb.scan.return_value = {
            'Items': [{'imdbID': {'S': TEST_IMDB_ID}}]
        }
        
        result = FavoritesRepository.get_imdb_id_from_title(TEST_MOVIE_TITLE, "movies")
        
        assert result == TEST_IMDB_ID
        mock_dynamodb.scan.assert_called_once()
    
    @patch('app.repositories.favorites_repository.dynamodb')
    def test_get_imdb_id_from_title_not_found(self, mock_dynamodb):
        """Test IMDB ID not found"""
        # Mock empty DynamoDB response
        mock_dynamodb.scan.return_value = {'Items': []}
        
        result = FavoritesRepository.get_imdb_id_from_title("Nonexistent Movie", "movies")
        
        assert result is None
        mock_dynamodb.scan.assert_called_once()
    
    @patch('app.repositories.favorites_repository.dynamodb')
    def test_get_favorite_movies_success(self, mock_dynamodb):
        """Test getting favorite movies"""
        # Mock DynamoDB response
        mock_dynamodb.query.return_value = {
            'Items': [
                {
                    'Title': {'S': TEST_MOVIE_TITLE},
                    'imdbID': {'S': TEST_IMDB_ID}
                }
            ]
        }
        
        result = FavoritesRepository.get_favorite_movies(TEST_EMAIL)
        
        assert len(result) == 1
        assert result[0]['Title'] == TEST_MOVIE_TITLE
        assert result[0]['imdbID'] == TEST_IMDB_ID
        mock_dynamodb.query.assert_called_once()
    
    @patch('app.repositories.favorites_repository.dynamodb')
    def test_get_favorite_movies_empty(self, mock_dynamodb):
        """Test getting favorite movies when empty"""
        mock_dynamodb.query.return_value = {'Items': []}
        
        result = FavoritesRepository.get_favorite_movies(TEST_EMAIL)
        
        assert result == []
        mock_dynamodb.query.assert_called_once()
    
    @patch('app.repositories.favorites_repository.dynamodb')
    def test_get_favorite_series_success(self, mock_dynamodb):
        """Test getting favorite series"""
        mock_dynamodb.query.return_value = {
            'Items': [
                {
                    'Title': {'S': TEST_SERIES_TITLE},
                    'imdbID': {'S': TEST_IMDB_ID}
                }
            ]
        }
        
        result = FavoritesRepository.get_favorite_series(TEST_EMAIL)
        
        assert len(result) == 1
        assert result[0]['Title'] == TEST_SERIES_TITLE
        mock_dynamodb.query.assert_called_once()
    
    @patch('app.repositories.favorites_repository.dynamodb')
    @patch.object(FavoritesRepository, 'get_imdb_id_from_title')
    def test_add_favorite_movie_success(self, mock_get_imdb, mock_dynamodb):
        """Test adding favorite movie successfully"""
        mock_get_imdb.return_value = TEST_IMDB_ID
        
        result = FavoritesRepository.add_favorite_movie(TEST_EMAIL, TEST_MOVIE_TITLE)
        
        assert result['message'] == f"Movie '{TEST_MOVIE_TITLE}' added to favorites!"
        mock_get_imdb.assert_called_once_with(TEST_MOVIE_TITLE, "movies")
        mock_dynamodb.put_item.assert_called_once()
    
    @patch.object(FavoritesRepository, 'get_imdb_id_from_title')
    def test_add_favorite_movie_not_found(self, mock_get_imdb):
        """Test adding favorite movie when movie not found"""
        mock_get_imdb.return_value = None
        
        result = FavoritesRepository.add_favorite_movie(TEST_EMAIL, "Nonexistent Movie")
        
        assert "error" in result
        assert "not found" in result['error']
    
    @patch('app.repositories.favorites_repository.dynamodb')
    @patch.object(FavoritesRepository, 'get_imdb_id_from_title')
    def test_add_favorite_series_success(self, mock_get_imdb, mock_dynamodb):
        """Test adding favorite series successfully"""
        mock_get_imdb.return_value = TEST_IMDB_ID
        
        result = FavoritesRepository.add_favorite_series(TEST_EMAIL, TEST_SERIES_TITLE)
        
        assert result['message'] == f"Series '{TEST_SERIES_TITLE}' added to favorites!"
        mock_get_imdb.assert_called_once_with(TEST_SERIES_TITLE, "TVSeries")
        mock_dynamodb.put_item.assert_called_once()
    
    @patch('app.repositories.favorites_repository.dynamodb')
    def test_delete_favorite_movie_success(self, mock_dynamodb):
        """Test deleting favorite movie successfully"""
        # Mock scan response (finding the movie)
        mock_dynamodb.scan.return_value = {
            'Items': [{'imdbID': {'S': TEST_IMDB_ID}}]
        }
        
        result = FavoritesRepository.delete_favorite_movie(TEST_EMAIL, TEST_MOVIE_TITLE)
        
        assert result['message'] == f"Movie '{TEST_MOVIE_TITLE}' removed from favorites!"
        mock_dynamodb.scan.assert_called_once()
        mock_dynamodb.delete_item.assert_called_once()
    
    @patch('app.repositories.favorites_repository.dynamodb')
    def test_delete_favorite_movie_not_found(self, mock_dynamodb):
        """Test deleting favorite movie when not found"""
        mock_dynamodb.scan.return_value = {'Items': []}
        
        result = FavoritesRepository.delete_favorite_movie(TEST_EMAIL, "Nonexistent Movie")
        
        assert "error" in result
        assert "not found in favorites" in result['error']

class TestFavoritesService:
    """Test FavoritesService class"""
    
    @patch.object(FavoritesRepository, 'get_favorite_movies')
    def test_get_favorite_movies(self, mock_repo):
        """Test service get favorite movies"""
        expected_movies = [{'Title': TEST_MOVIE_TITLE, 'imdbID': TEST_IMDB_ID}]
        mock_repo.return_value = expected_movies
        
        result = FavoritesService.get_favorite_movies(TEST_EMAIL)
        
        assert result == expected_movies
        mock_repo.assert_called_once_with(TEST_EMAIL)
    
    @patch.object(FavoritesRepository, 'get_favorite_series')
    def test_get_favorite_series(self, mock_repo):
        """Test service get favorite series"""
        expected_series = [{'Title': TEST_SERIES_TITLE, 'imdbID': TEST_IMDB_ID}]
        mock_repo.return_value = expected_series
        
        result = FavoritesService.get_favorite_series(TEST_EMAIL)
        
        assert result == expected_series
        mock_repo.assert_called_once_with(TEST_EMAIL)
    
    @patch.object(FavoritesRepository, 'add_favorite_movie')
    def test_add_favorite_movie(self, mock_repo):
        """Test service add favorite movie"""
        expected_response = {'message': f"Movie '{TEST_MOVIE_TITLE}' added to favorites!"}
        mock_repo.return_value = expected_response
        
        result = FavoritesService.add_favorite_movie(TEST_EMAIL, TEST_MOVIE_TITLE)
        
        assert result == expected_response
        mock_repo.assert_called_once_with(TEST_EMAIL, TEST_MOVIE_TITLE)
    
    @patch.object(FavoritesRepository, 'add_favorite_series')
    def test_add_favorite_series(self, mock_repo):
        """Test service add favorite series"""
        expected_response = {'message': f"Series '{TEST_SERIES_TITLE}' added to favorites!"}
        mock_repo.return_value = expected_response
        
        result = FavoritesService.add_favorite_series(TEST_EMAIL, TEST_SERIES_TITLE)
        
        assert result == expected_response
        mock_repo.assert_called_once_with(TEST_EMAIL, TEST_SERIES_TITLE)
    
    @patch.object(FavoritesRepository, 'delete_favorite_movie')
    def test_delete_favorite_movie(self, mock_repo):
        """Test service delete favorite movie"""
        expected_response = {'message': f"Movie '{TEST_MOVIE_TITLE}' removed from favorites!"}
        mock_repo.return_value = expected_response
        
        result = FavoritesService.delete_favorite_movie(TEST_EMAIL, TEST_MOVIE_TITLE)
        
        assert result == expected_response
        mock_repo.assert_called_once_with(TEST_EMAIL, TEST_MOVIE_TITLE)
    
    @patch.object(FavoritesRepository, 'delete_favorite_series')
    def test_delete_favorite_series(self, mock_repo):
        """Test service delete favorite series"""
        expected_response = {'message': f"Series '{TEST_SERIES_TITLE}' removed from favorites!"}
        mock_repo.return_value = expected_response
        
        result = FavoritesService.delete_favorite_series(TEST_EMAIL, TEST_SERIES_TITLE)
        
        assert result == expected_response
        mock_repo.assert_called_once_with(TEST_EMAIL, TEST_SERIES_TITLE)

class TestFavoritesAPI:
    """Test FastAPI endpoints"""
    
    @patch.object(FavoritesService, 'get_favorite_movies')
    def test_get_favorite_movies_endpoint(self, mock_service):
        """Test GET /favorites/movies/{email} endpoint"""
        expected_movies = [{'Title': TEST_MOVIE_TITLE, 'imdbID': TEST_IMDB_ID}]
        mock_service.return_value = expected_movies
        
        response = client.get(f"/api/favorites/movies/{TEST_EMAIL}")
        
        assert response.status_code == 200
        assert response.json() == expected_movies
        mock_service.assert_called_once_with(TEST_EMAIL)
    
    @patch.object(FavoritesService, 'get_favorite_series')
    def test_get_favorite_series_endpoint(self, mock_service):
        """Test GET /favorites/series/{email} endpoint"""
        expected_series = [{'Title': TEST_SERIES_TITLE, 'imdbID': TEST_IMDB_ID}]
        mock_service.return_value = expected_series
        
        response = client.get(f"/api/favorites/series/{TEST_EMAIL}")
        
        assert response.status_code == 200
        assert response.json() == expected_series
        mock_service.assert_called_once_with(TEST_EMAIL)
    
    @patch.object(FavoritesService, 'add_favorite_movie')
    def test_add_favorite_movie_endpoint(self, mock_service):
        """Test POST /favorites/movies/{email}/{title} endpoint"""
        expected_response = {'message': f"Movie '{TEST_MOVIE_TITLE}' added to favorites!"}
        mock_service.return_value = expected_response
        
        response = client.post(f"/api/favorites/movies/{TEST_EMAIL}/{TEST_MOVIE_TITLE}")
        
        assert response.status_code == 200
        assert response.json() == expected_response
        mock_service.assert_called_once_with(TEST_EMAIL, TEST_MOVIE_TITLE)
    
    @patch.object(FavoritesService, 'add_favorite_series')
    def test_add_favorite_series_endpoint(self, mock_service):
        """Test POST /favorites/series/{email}/{title} endpoint"""
        expected_response = {'message': f"Series '{TEST_SERIES_TITLE}' added to favorites!"}
        mock_service.return_value = expected_response
        
        response = client.post(f"/api/favorites/series/{TEST_EMAIL}/{TEST_SERIES_TITLE}")
        
        assert response.status_code == 200
        assert response.json() == expected_response
        mock_service.assert_called_once_with(TEST_EMAIL, TEST_SERIES_TITLE)
    
    @patch.object(FavoritesService, 'delete_favorite_movie')
    def test_delete_favorite_movie_endpoint(self, mock_service):
        """Test DELETE /favorites/movies/{email}/{title} endpoint"""
        expected_response = {'message': f"Movie '{TEST_MOVIE_TITLE}' removed from favorites!"}
        mock_service.return_value = expected_response
        
        response = client.delete(f"/api/favorites/movies/{TEST_EMAIL}/{TEST_MOVIE_TITLE}")
        
        assert response.status_code == 200
        assert response.json() == expected_response
        mock_service.assert_called_once_with(TEST_EMAIL, TEST_MOVIE_TITLE)
    
    @patch.object(FavoritesService, 'delete_favorite_series')
    def test_delete_favorite_series_endpoint(self, mock_service):
        """Test DELETE /favorites/series/{email}/{title} endpoint"""
        expected_response = {'message': f"Series '{TEST_SERIES_TITLE}' removed from favorites!"}
        mock_service.return_value = expected_response
        
        response = client.delete(f"/api/favorites/series/{TEST_EMAIL}/{TEST_SERIES_TITLE}")
        
        assert response.status_code == 200
        assert response.json() == expected_response
        mock_service.assert_called_once_with(TEST_EMAIL, TEST_SERIES_TITLE)
    
    def test_url_decode_in_endpoints(self):
        """Test URL decoding in endpoints"""
        encoded_title = "The%20Lord%20of%20the%20Rings"
        expected_title = "The Lord of the Rings"
        
        with patch.object(FavoritesService, 'add_favorite_movie') as mock_service:
            mock_service.return_value = {'message': 'Added'}
            
            response = client.post(f"/api/favorites/movies/{TEST_EMAIL}/{encoded_title}")
            
            # Verify that the title was properly decoded
            mock_service.assert_called_once_with(TEST_EMAIL, expected_title)
            assert response.status_code == 200