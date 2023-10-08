from typing import Any

from redis.asyncio import Redis

con_redis: Redis | None = None


async def set_value(key: Any, value: Any, time_live: int | None = None):
    """Передача данных в REDIS time_live- в секундах"""
    await con_redis.set(key, value, ex=time_live)


async def get_value(key):
    return await con_redis.get(key)
