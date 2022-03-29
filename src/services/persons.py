from functools import lru_cache

from db.manager import DataManager, get_data_manager
from fastapi import Depends
from models.person import PersonElasticModel

from .base import BaseService
from .mixins import ListModelMixin, RetrieveModelMixin


class PersonService(RetrieveModelMixin, ListModelMixin, BaseService):
    index = 'persons'
    model = PersonElasticModel
    search_fields = ['full_name']


@lru_cache()
def get_person_service(
        data_manager: DataManager = Depends(get_data_manager),
) -> PersonService:
    return PersonService(data_manager)
