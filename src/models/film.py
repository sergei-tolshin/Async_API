from typing import List, Optional
from uuid import UUID

from models.base import ESBaseModel, OrjsonMixin


class Person(ESBaseModel):
    name: str


class Genre(ESBaseModel):
    name: str


class Film(ESBaseModel):
    title: str
    imdb_rating: Optional[float]
    film_type: Optional[str]
    description: Optional[str]
    genre: Optional[List[Genre]]
    directors: Optional[List[Person]]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]
    directors_names: Optional[List[str]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]


class FilmResponseModel(OrjsonMixin):
    """Модель ответа API для фильмов"""
    id: UUID
    title: str
    imdb_rating: Optional[float]
    film_type: Optional[str]
    description: Optional[str]
    genre: Optional[List]
    directors: Optional[List]
    actors: Optional[List]
    writers: Optional[List]
