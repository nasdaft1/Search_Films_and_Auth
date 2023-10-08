import logging
from contextlib import asynccontextmanager
from logging import config as logging_config

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination
from redis import asyncio as aioredis

from api.v1 import users, roles, auth
from core import logger
from core.config import config
from db import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.con_redis = aioredis.from_url(f'redis://{config.redis_host}:{config.redis_port}')
    FastAPICache.init(RedisBackend(redis.con_redis), prefix='fastapi-cache', expire=config.cache_expire_time)
    yield
    # Отключаемся от баз при выключении сервера
    await redis.con_redis.close()


# Применяем настройки логирования
logging_config.dictConfig(logger.LOGGING)
app = FastAPI(
    title=config.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(users.router, prefix='/api/v1/users')
app.include_router(roles.router, prefix='/api/v1/roles')
app.include_router(auth.router, prefix='/api/v1/auth')

add_pagination(app)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=logger.LOGGING,
        log_level=logging.DEBUG,
    )
