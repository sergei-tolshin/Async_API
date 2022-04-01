import asyncio
import os

import aioredis


REDIS_HOST: str = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))


async def main():
    while True:
        try:
            redis = await aioredis.create_redis(f'redis://{REDIS_HOST}:{REDIS_PORT}')
            redis.close()
            await redis.wait_closed()
            break
        except:
            await asyncio.sleep(1)

    print('close')


if __name__ == '__main__':
    asyncio.run(main())
