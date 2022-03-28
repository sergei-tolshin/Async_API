from typing import List, Optional
from uuid import UUID

from core.paginator import PaginationMixin

from models.base import ESBaseModel, OrjsonMixin


class GenreElasticModel(ESBaseModel):
    name: str
    description: Optional[str] = None


class GenreResponseModel(OrjsonMixin):
    """Модель ответа API для жанров"""
    id: UUID
    name: str


class GenreDetailsResponseModel(GenreResponseModel):
    """Модель ответа API подробная"""
    description: Optional[str]


class GenrePagination(PaginationMixin):
    """Модель ответа API для результатов в пагинации"""
    results: List[GenreResponseModel] = []
