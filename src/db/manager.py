from typing import Optional

import orjson
from elasticsearch import NotFoundError

from db.cache import get_cache_provider, AbstractCache
from db.storage import get_storage, AbstractStorage


class DataManager:
    def __init__(self, cache_provider: AbstractCache,
                 storage: AbstractStorage):
        self.cache_provider = cache_provider
        self.storage = storage

    async def get_object(self, index: str, id: str) -> Optional[dict]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        key = await self.cache_provider.get_key(index, id)
        instance = await self.cache_provider.get_from_cache(key) or None
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
                await self.cache_provider.put_in_cache(key,
                                                       orjson.dumps(instance))
                return instance
            except NotFoundError:
                return None
        return orjson.loads(instance)

    async def search(self, index: str, query: dict):
        key = await self.cache_provider.get_key(index, query)
        queryset = await self.cache_provider.get_from_cache(key) or None
        if not queryset:
            try:
                docs = await self.storage.search(**query)
                hits = docs['hits']['hits']
                count: int = int(docs.get('hits').get('total').get('value', 0))
                objects = [hit['_source'] for hit in hits]
                data: dict = {'count': count, 'obj': objects}
                await self.cache_provider.put_in_cache(key,
                                                       orjson.dumps(data))
                return data
            except NotFoundError:
                return None
        return orjson.loads(queryset)


async def get_data_manager() -> DataManager:
    cache_provider = await get_cache_provider()
    storage = await get_storage()
    return DataManager(cache_provider, storage)
