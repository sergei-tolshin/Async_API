from abc import ABC, abstractmethod
from typing import Optional, Union


class BaseCacheProvider(ABC):

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


cache_provider: Optional[BaseCacheProvider] = None


async def get_cache_provider() -> BaseCacheProvider:
    return cache_provider
