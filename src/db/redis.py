from hashlib import sha256
from typing import Optional, Union

import orjson
from aioredis import Redis
from core import config

from db.cache import AbstractCache


class RedisCache(AbstractCache):

    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, key: str, data: Union[str, bytes]) -> None:
        await self.redis.set(key, data, expire=config.CACHE_EXPIRE_IN_SECONDS)

    async def get(self, key: str) -> Optional[bytes]:
        return await self.redis.get(key) or None

    async def get_key(self, prefix: str, query: Union[str, dict]) -> str:
        str_params: bytes = orjson.dumps(query)
        _hash = sha256(str_params).hexdigest()
        return f'{prefix}:{_hash}'

    async def close(self) -> None:
        await self.redis.close()
