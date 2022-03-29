from typing import List, Optional
from uuid import UUID

from models.base import ESBaseModel, OrjsonMixin
from core.paginator import PaginationMixin


class Person(ESBaseModel):
    name: str


class Genre(ESBaseModel):
    name: str


class FilmElasticModel(ESBaseModel):
    title: str
    imdb_rating: Optional[float]
    film_type: Optional[str]
    description: Optional[str] = None
    genre: Optional[List[Genre]]
    directors: Optional[List[Person]] = None
    actors: Optional[List[Person]] = None
    writers: Optional[List[Person]] = None
    directors_names: Optional[List[str]] = None
    actors_names: Optional[List[str]] = None
    writers_names: Optional[List[str]] = None


class FilmResponseModel(OrjsonMixin):
    """Модель ответа API для фильмов"""
    id: UUID
    title: str
    imdb_rating: Optional[float]


class FilmDetailsResponseModel(FilmResponseModel):
    """Модель ответа API для фильмов"""
    film_type: Optional[str]
    description: Optional[str] = None
    genre: Optional[List]
    directors: Optional[List] = None
    actors: Optional[List] = None
    writers: Optional[List] = None


class FilmPagination(PaginationMixin):
    """Модель ответа API для результатов в пагинации"""
    results: List[FilmResponseModel] = []
