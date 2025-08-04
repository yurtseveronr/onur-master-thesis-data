from pydantic import BaseModel, EmailStr
from typing import List

class FavoriteMovies(BaseModel):
    email: EmailStr
    movies: List[str]  # IMDb ID listesi

class FavoriteSeries(BaseModel):
    email: EmailStr
    series: List[str]  # IMDb ID listesi
