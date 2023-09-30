import logging
from contextlib import asynccontextmanager
from logging import config as logging_config

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from fastapi_cache.decorator import cache
from api.v1 import films, genres, persons
from core import logger
from core.config import config
from db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = aioredis.from_url(f'redis://{config.redis_host}:{config.redis_port}')
    FastAPICache.init(RedisBackend(redis.redis), prefix="fastapi-cache", expire=config.cache_expire_time)
    elastic.es = AsyncElasticsearch(hosts=[f'{config.elastic_host}:{config.elastic_port}'])
    yield
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()


# Применяем настройки логирования
logging_config.dictConfig(logger.LOGGING)
app = FastAPI(
    title=config.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


# app.include_router(films.router, prefix='/api/v1/films')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=logger.LOGGING,
        log_level=logging.DEBUG,
    )
