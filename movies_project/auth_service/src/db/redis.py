from redis.asyncio import Redis


con_redis: Redis | None = None


async def set_value(key, value):
    await con_redis.set(key, value)


async def get_value(key):
    return await con_redis.get(key)
