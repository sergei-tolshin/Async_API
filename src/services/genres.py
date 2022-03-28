from functools import lru_cache
from typing import Optional

import orjson
from aioredis import Redis
from core.paginator import get_pagination
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.genre import GenreElasticModel

from .base import BaseService


class GenreService(BaseService):
    def __init__(self, redis, elastic):
        super().__init__(redis, elastic)
        self.index = 'genres'
        self.search_fields = ['name']

    async def get_list(self, params: dict) -> Optional[dict]:
        # Получает список жанров
        query = await self._parse_params(params)
        key = await self._hash_key(index=self.index, params=query)
        data = await self._get_data_from_cache(key)
        if not data:
            data: Optional[dict] = await self._get_data_from_elastic(
                GenreElasticModel, query=query, key=key)
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


@ lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
