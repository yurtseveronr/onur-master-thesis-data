from app.repositories.favorites_repository import FavoritesRepository

class FavoritesService:
    @staticmethod
    def get_favorite_movies(email: str):
        return FavoritesRepository.get_favorite_movies(email)

    @staticmethod
    def get_favorite_series(email: str):
        return FavoritesRepository.get_favorite_series(email)

    @staticmethod
    def add_favorite_movie(email: str, title: str, imdb_id: str = None):
        return FavoritesRepository.add_favorite_movie(email, title, imdb_id)

    @staticmethod
    def add_favorite_series(email: str, title: str, imdb_id: str = None):
        return FavoritesRepository.add_favorite_series(email, title, imdb_id)

    @staticmethod
    def delete_favorite_movie(email: str, title: str):
        return FavoritesRepository.delete_favorite_movie(email, title)

    @staticmethod
    def delete_favorite_series(email: str, title: str):
        return FavoritesRepository.delete_favorite_series(email, title)
