from abc import ABC, abstractmethod
from typing import Optional, Union


class AbstractCache(ABC):

    @abstractmethod
    async def put_in_cache(self, key: str, data: Union[str, bytes]) -> None:
        pass

    @abstractmethod
    async def get_from_cache(self, key: str) -> Union[str, bytes]:
        pass

    @abstractmethod
    async def get_key(self, prefix: str, query: Union[str, dict]) -> str:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass


cache_provider: Optional[AbstractCache] = None


async def get_cache_provider() -> AbstractCache:
    return cache_provider
