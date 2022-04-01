import asyncio
import logging

import aioredis
import backoff

logging.getLogger('backoff').addHandler(logging.StreamHandler())


@backoff.on_predicate(backoff.fibo, max_value=10)
@backoff.on_exception(backoff.expo, ConnectionRefusedError, max_time=300)
async def wait_for_redis():
    redis_client = await aioredis.create_redis_pool(
        ('127.0.0.1', 6379), minsize=10, maxsize=20
    )
    if await redis_client.ping():
        redis_client.close()
        await redis_client.wait_closed()
        return True


loop = asyncio.get_event_loop()
loop.run_until_complete(wait_for_redis())
loop.close()
