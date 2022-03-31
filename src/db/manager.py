from hashlib import sha256
from typing import Optional, Union

import orjson
from aioredis import Redis
from core import config
from elasticsearch import NotFoundError

from db.redis import get_redis
from db.storage import AbstractStorage, get_storage


class DataManager:
    def __init__(self, redis: Redis, storage: AbstractStorage):
        self.redis = redis
        self.storage = storage
        self.request = None

    def _hash_key(self, index: str, key: Union[str, dict]) -> str:
        # Формирует хеш ключа запроса
        key: bytes = orjson.dumps(key)
        hash = sha256(key).hexdigest()
        return f'{index}:{hash}'

    async def get_object(self, index: str, id: str) -> Optional[dict]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        instance = await self.redis.get(self._hash_key(index, id)) or None
        if not instance:
            # Если экземпляра нет в кеше, то ищем его в базе
            try:
                doc = await self.storage.get(index, id)
                if not doc:
                    # Если он отсутствует в базе, значит,
                    # экземпляра вообще нет в базе
                    return None
                # Сохраняем экземпляр в кеш
                instance = doc['_source']
                await self.redis.set(self._hash_key(index, id),
                                     orjson.dumps(instance),
                                     expire=config.CACHE_EXPIRE_IN_SECONDS)
                return instance
            except NotFoundError:
                return None
        return orjson.loads(instance)

    async def search(self, index: str, query: dict):
        key = {
            "path": self.request.url.path,
            "params": dict(self.request.query_params.items())
        }
        queryset = await self.redis.get(self._hash_key(index, key)) or None
        if not queryset:
            try:
                docs = await self.storage.search(**query)
                hits = docs['hits']['hits']
                count: int = int(docs.get('hits').get('total').get('value', 0))
                objects = [hit['_source'] for hit in hits]
                data: dict = {'count': count, 'results': objects}
                await self.redis.set(self._hash_key(index, key),
                                     orjson.dumps(data),
                                     expire=config.CACHE_EXPIRE_IN_SECONDS)
                return data
            except NotFoundError:
                return None
        return orjson.loads(queryset)


async def get_data_manager() -> DataManager:
    redis = await get_redis()
    storage = await get_storage()
    return DataManager(redis, storage)
