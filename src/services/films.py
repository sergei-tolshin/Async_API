from functools import lru_cache

from db.manager import DataManager, get_data_manager
from fastapi import Depends
from models.film import FilmElasticModel

from .base import BaseService
from .mixins import ListModelMixin, RetrieveModelMixin


class FilmService(RetrieveModelMixin, ListModelMixin, BaseService):
    index = 'movies'
    model = FilmElasticModel
    search_fields = ['title', 'description']


@lru_cache()
def get_film_service(
        data_manager: DataManager = Depends(get_data_manager),
) -> FilmService:
    return FilmService(data_manager)
