from functools import lru_cache
from typing import Optional

import orjson
from aioredis import Redis
from core.paginator import get_pagination
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from models.person import PersonElasticModel

from .base import BaseService


class PersonService(BaseService):
    def __init__(self, redis, elastic):
        super().__init__(redis, elastic)
        self.index = 'persons'
        self.search_fields = ['full_name']

    async def get_list(self, params: dict) -> Optional[dict]:
        # Получает список персонажей
        query = await self._parse_params(params)
        key = await self._hash_key(index=self.index, params=query)
        data = await self._get_data_from_cache(key)
        if not data:
            data: Optional[dict] = await self._get_data_from_elastic(
                PersonElasticModel, query=query, key=key)
            if not data:
                return None
        else:
            data = orjson.loads(data)

        page_obj = get_pagination(
            count=data['count'],
            page=int((query.get('from_')/query.get('size'))+1),
            page_size=query.get('size'),
            objects=data['obj'],
        )
        return page_obj

    async def get_films(self, id: str, params: dict) -> Optional[dict]:
        # Получает список фильмов персонажа
        query = await self._parse_params(params)
        key = await self._hash_key(index=self.index, params=query)
        data = await self._get_data_from_cache(key)
        if not data:
            data: Optional[dict] = await self._get_data_from_elastic(
                Film, query=query, key=key)
            if not data:
                return None
        else:
            data = orjson.loads(data)

        page_obj = get_pagination(
            count=data['count'],
            page=int((query.get('from_')/query.get('size'))+1),
            page_size=query.get('size'),
            objects=data['obj'],
        )
        return page_obj


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
