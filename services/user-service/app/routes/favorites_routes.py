from fastapi import APIRouter
from urllib.parse import unquote
from app.services.favorites_service import FavoritesService
#FAST_API ROUTES
router = APIRouter()

@router.get("/favorites/movies/{email}")
async def get_favorite_movies(email: str):
    return FavoritesService.get_favorite_movies(email)

@router.get("/favorites/series/{email}")
async def get_favorite_series(email: str):
    return FavoritesService.get_favorite_series(email)

@router.post("/favorites/movies/{email}/{title}")
async def add_favorite_movie(email: str, title: str, imdb_id: str = None):
    decoded_title = unquote(title)
    return FavoritesService.add_favorite_movie(email, decoded_title, imdb_id)

@router.post("/favorites/series/{email}/{title}")
async def add_favorite_series(email: str, title: str):
    decoded_title = unquote(title)
    return FavoritesService.add_favorite_series(email, decoded_title)

@router.delete("/favorites/movies/{email}/{title}")
async def delete_favorite_movie(email: str, title: str):
    decoded_title = unquote(title)
    return FavoritesService.delete_favorite_movie(email, decoded_title)

@router.delete("/favorites/series/{email}/{title}")
async def delete_favorite_series(email: str, title: str):
    decoded_title = unquote(title)
    return FavoritesService.delete_favorite_series(email, decoded_title)
