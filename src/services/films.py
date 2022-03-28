from functools import lru_cache
from typing import List, Optional, Union
import uuid

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 15
FILM_INDEX = 'movies'
FILM_SORT_FIELDS = ['imdb_rating']
FILM_SEARCH_FIELDS = ['title', 'description']


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = FILM_INDEX
        self.sort_fields_set = FILM_SORT_FIELDS
        self.search_fields_set = FILM_SEARCH_FIELDS

    async def _convert_to_cache_key(self, data: Union[uuid.UUID, dict]) -> str:
        if isinstance(data, uuid.UUID):
            return f'{self.index}:{data}'
        key_suffix = '&'.join(
            f'{key}={value}' for key, value in sorted(data.items())
        )
        return f'{self.index}:{key_suffix}'

    async def _parse_params(self, query_params: dict) -> dict:

        _filter = query_params.get('filter[genre]')
        search_text = query_params.get('query')
        page_number = int(query_params.get('page[number]'))
        size = int(query_params.get('page[size]'))

        sort_order = query_params.get('sort')

        if sort_order:
            sort_direction = 'desc' if sort_order[0] == '-' else 'asc'
            sort_field = sort_order[1:] if sort_order[0] == '-' else sort_order
            if sort_field not in self.sort_fields_set:
                sort_order = None
            else:
                sort_order = f'{sort_field}:{sort_direction}'

        es_query = {'query': {'match_all': {}}}
        if _filter:

            es_query = {
                "query": {
                    "nested": {
                        "path": "genre",
                        "query": {
                            "bool": {
                                "must": [
                                    {"term": {"genre.id": _filter}},
                                ]
                            }
                        }
                     }
                }
            }

        if search_text:
            es_query = {
                'query': {
                    'multi_match': {
                        'query': search_text,
                        'fields': self.search_fields_set
                    }
                }
            }

        query = {
            'index': self.index,
            'body': es_query,
            'sort': sort_order,
            'size': size,
            'from_': (page_number - 1) * size
        }

        query = {key: value for key, value in query.items()
                 if value is not None}

        return query

    async def get_by_id(self, film_id: str) -> Optional[Film]:

        key = await self._convert_to_cache_key(film_id)
        film = await self._film_from_cache(key)
        if not film:

            film = await self._get_film_from_elastic(film_id=film_id)
            if not film:
                return None

            await self._put_film_to_cache(key, film)

        return film

    async def get_films(self, query_params: dict) -> Optional[List[Film]]:

        query = await self._parse_params(query_params)

        key = await self._convert_to_cache_key(query)

        films = await self._film_from_cache(key, many=True)

        if not films:

            films = await self._get_film_from_elastic(query=query)
            if not films:
                return None

            await self._put_film_to_cache(key, films, many=True)

        return films

    async def _get_film_from_elastic(self,
                                     film_id: uuid.UUID = None,
                                     query: dict = None
                                     ) -> Optional[Union[List[Film], Film]]:

        if film_id:
            try:
                doc = await self.elastic.get(self.index, film_id)
            except NotFoundError:
                return None
            return Film(**doc['_source'])

        result = await self.elastic.search(**query)
        hits = result['hits']['hits']

        if not hits:
            return None
        return [Film(**hit['_source']) for hit in hits]

    async def _film_from_cache(self, key: str,
                               many: bool = False) -> Optional[Film]:
        if many:
            films = await self.redis.lrange(key, 0, -1)
            if not films:
                return None
            return (Film.parse_raw(film) for film in films)

        film = await self.redis.get(key)
        if not film:
            return None

        film = Film.parse_raw(film)
        return film

    async def _put_film_to_cache(self, key: str,
                                 data: Union[Film, List[Film]],
                                 many: bool = False):
        if many:
            transaction = self.redis.multi_exec()
            for film in data:
                transaction.rpush(key, film.json())
            await transaction.execute()
            await self.redis.expire(key, FILM_CACHE_EXPIRE_IN_SECONDS)
        else:
            await self.redis.set(key, data.json(),
                                 expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
