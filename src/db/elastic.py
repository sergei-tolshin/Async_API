from .storage import AbstractStorage


class ElasticStorage(AbstractStorage):
    def __init__(self, client):
        self.client = client

    async def get(self, index: str, id: str) -> dict:
        return await self.client.get(index, id)

    async def search(self, **query) -> dict:
        return await self.client.search(**query)

    async def close(self) -> None:
        await self.client.close()
