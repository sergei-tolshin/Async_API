import json
from hashlib import sha256
from typing import Optional, Union

import orjson
from aioredis import Redis
from core import config
from elasticsearch import AsyncElasticsearch, NotFoundError
from models import film, genre, person

Models: tuple = (genre.GenreElasticModel, person.PersonElasticModel)
models = Union[Models]


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.count = {}

    async def _hash_key(self, index: str, params: str) -> str:
        # Формирует хеш ключа запроса
        str_params = json.dumps(params)
        hash = sha256(str_params.encode()).hexdigest()
        return f'{index}:{hash}'

    async def _parse_params(self, query_params: dict) -> dict:
        # Парсит параметры и формирует запрос в elastic
        _index = query_params.get('_index')
        query_body = query_params.get('query_body')
        _filter = query_params.get('filter[genre]')
        search_text = query_params.get('search_text')
        page_number = int(query_params.get('page[number]'))
        page_size = int(query_params.get('page[size]'))
        sort = query_params.get('sort')

        if not _index:
            _index = self.index

        if not query_body:
            query_body: dict = {'query': {'match_all': {}}}

        if _filter:
            query_body = {
                'query': {
                    'nested': {
                        'path': 'genre',
                        'query': {
                            'bool': {
                                'must': [
                                    {'term': {'genre.id': _filter}},
                                ]
                            }
                        }
                    }
                }
            }

        if search_text:
            query_body: dict = {
                'query': {
                    'multi_match': {
                        'query': search_text,
                        'fuzziness': 'auto',
                        'fields': self.search_fields
                    }
                }
            }

        sort_field = sort[0] if not isinstance(sort, str) and sort else sort
        if sort_field:
            order = 'desc' if sort_field.startswith('-') else 'asc'
            sort_field = f"{sort_field.removeprefix('-')}:{order}"

        query = {
            'index': _index,
            'body': query_body,
            'sort': sort_field,
            'size': page_size,
            'from_': (page_number - 1) * page_size
        }

        query = {key: value for key, value in query.items()
                 if value is not None}

        return query

    async def _get_data_from_elastic(
        self,
        model: Models,
        id: str = None,
        query: dict = None,
        key: str = None,
    ) -> Optional[Union[models, dict]]:
        # Ищет данные в elastic по id объекта или по сформированному запросу
        try:
            if id:
                doc = await self.elastic.get(self.index, id)
                return model(**doc['_source'])

            docs = await self.elastic.search(**query)
            hits = docs['hits']['hits']
            count: int = int(docs.get('hits').get('total').get('value', 0))
            objects = [model(**hit['_source']) for hit in hits]
            data: dict = {'count': count, 'obj': [_.dict() for _ in objects]}
            await self._put_data_to_cache(key, orjson.dumps(data))

            return data
        except NotFoundError:
            return None

    async def _get_data_from_cache(self, key: str) -> Optional[bytes]:
        # Пытаемся получить данные из кеша, используя команду get
        return await self.redis.get(key) or None

    async def _put_data_to_cache(self, key: str, value: Union[bytes, str]):
        # Сохраняем данные, используя команду set
        await self.redis.set(key, value, expire=config.CACHE_EXPIRE_IN_SECONDS)

    # get_by_id возвращает экземпляр.
    # Он опционален, так как экземпляр может отсутствовать в базе
    async def get_by_id(self,
                        model: Models,
                        id: str,
                        ) -> Optional[models]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        instance = await self._get_data_from_cache(id)
        if not instance:
            # Если экземпляра нет в кеше, то ищем его в Elasticsearch
            instance = await self._get_data_from_elastic(model, id)
            if not instance:
                # Если он отсутствует в Elasticsearch, значит,
                # экземпляра вообще нет в базе
                return None
            # Сохраняем экземпляр в кеш
            await self._put_data_to_cache(instance.id, instance.json())
            return instance
        return model.parse_raw(instance)
