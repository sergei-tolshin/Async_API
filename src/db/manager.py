from typing import Optional

import orjson
from elasticsearch import NotFoundError

from db.cache import get_cache, AbstractCache
from db.storage import get_storage, AbstractStorage


class DataManager:
    def __init__(self, cache: AbstractCache, storage: AbstractStorage):
        self.cache = cache
        self.storage = storage
        self.request = None

    async def get_object(self, index: str, id: str) -> Optional[dict]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        key = await self.cache.get_key(index, id)
        instance = await self.cache.get(key) or None
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
                await self.cache.set(key, orjson.dumps(instance))
                return instance
            except NotFoundError:
                return None
        return orjson.loads(instance)

    async def search(self, index: str, query: dict):
        request = {
            "path": self.request.url.path,
            "params": dict(self.request.query_params.items())
        }
        key = await self.cache.get_key(index, request)
        queryset = await self.cache.get(key) or None
        if not queryset:
            try:
                docs = await self.storage.search(**query)
                hits = docs['hits']['hits']
                count: int = int(docs.get('hits').get('total').get('value', 0))
                objects = [hit['_source'] for hit in hits]
                data: dict = {'count': count, 'results': objects}
                await self.cache.set(key, orjson.dumps(data))
                return data
            except NotFoundError:
                return None
        return orjson.loads(queryset)


async def get_data_manager() -> DataManager:
    cache = await get_cache()
    storage = await get_storage()
    return DataManager(cache, storage)
