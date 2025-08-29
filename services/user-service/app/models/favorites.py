from pydantic import BaseModel, EmailStr
from typing import List

class FavoriteMovies(BaseModel):
    email: EmailStr
    movies: List[str] 

class FavoriteSeries(BaseModel):
    email: EmailStr
    series: List[str]  
