from typing import List, Optional
from uuid import UUID

from core.paginator import PaginationMixin

from models.base import ESBaseModel, OrjsonMixin


class PersonElasticModel(ESBaseModel):
    full_name: str
    roles: Optional[List[str]] = None
    film_ids: Optional[List[str]] = None
    actor_film_ids: Optional[List[str]] = None
    director_film_ids: Optional[List[str]] = None
    writer_film_ids: Optional[List[str]] = None


class PersonResponseModel(OrjsonMixin):
    """Модель ответа API для персонажей"""
    id: UUID
    full_name: str
    roles: Optional[List[str]]
    film_ids: Optional[List[str]]


class PersonDetailsResponseModel(PersonResponseModel):
    """Модель ответа API для одного персонажа"""
    film_ids: Optional[List[str]]
    actor_film_ids: Optional[List[str]]
    director_film_ids: Optional[List[str]]
    writer_film_ids: Optional[List[str]]


class PersonPagination(PaginationMixin):
    """Модель ответа API для результатов в пагинации"""
    results: List[PersonResponseModel] = []


class FilmResponseModel(OrjsonMixin):
    """Модель ответа API для фильмов с участием персонажа"""
    id: UUID
    title: str
    imdb_rating: Optional[float]


class PersonFilmPagination(PaginationMixin):
    """Модель ответа API для результатов в пагинации"""
    results: List[FilmResponseModel] = []
