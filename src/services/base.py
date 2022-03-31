from abc import ABC, abstractmethod
from typing import List, Optional

from db.manager import DataManager

from .utils import RequestParams


class AbstractService(ABC):
    @property
    def index(self):
        raise NotImplementedError

    @property
    def model(self):
        raise NotImplementedError

    @property
    def search_fields(self):
        raise NotImplementedError

    @abstractmethod
    async def get_serializer(self, instance):
        pass

    @abstractmethod
    async def get_query(self, params):
        pass


class BaseService(AbstractService):
    search_fields: Optional[List] = []

    def __init__(self, data_manager: DataManager):
        self.request = None
        self.paginator = None
        self.data_manager: DataManager = data_manager

    async def get_serializer(self, instance):
        serializer_class = self.model
        return serializer_class(**instance)

    async def get_query(self, params):
        request_params = RequestParams()
        query = await request_params.get_query(params, self.index,
                                               self.search_fields)
        return query
