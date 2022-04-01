import asyncio
import os

from elasticsearch import AsyncElasticsearch


ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))
es_client = AsyncElasticsearch(hosts=f'{ELASTIC_HOST}:{ELASTIC_PORT}')


async def main():
    while not await es_client.ping():
        await asyncio.sleep(1)
    await es_client.close()
    print('close')


if __name__ == '__main__':
    asyncio.run(main())
