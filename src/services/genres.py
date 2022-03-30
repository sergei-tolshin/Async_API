from functools import lru_cache

from core import config
from db.manager import DataManager, get_data_manager
from fastapi import Depends
from models.genre import GenreElasticModel

from .base import BaseService
from .mixins import ListModelMixin, RetrieveModelMixin


class GenreService(RetrieveModelMixin, ListModelMixin, BaseService):
    index = config.ELASTIC_INDEX['genres']
    model = GenreElasticModel


@lru_cache()
def get_genre_service(
        data_manager: DataManager = Depends(get_data_manager),
) -> GenreService:
    return GenreService(data_manager)
