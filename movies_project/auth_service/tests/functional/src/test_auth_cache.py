from http import HTTPStatus

import httpx
import pytest
from redis.asyncio import Redis

from core.config import security_config
from tests.functional.fixtures.client import AsyncClient

base_url = 'http://127.0.0.1:8000/api/v1'


@pytest.mark.parametrize("method, url, params, status_code", [
    ('post', '/auth/login',
     {"username": "XXXXXX", "password": "87654321_Af/"},
     HTTPStatus.OK),  # Создать пользователя
])
async def test_login(method, url, params, status_code, async_client: AsyncClient):
    """Проверка авторизации и создание cookies c token"""
    response = await async_client.request(method=method, path=url, params=params)

    assert response.status_code == status_code
    assert response.json() == {'roles': ['admin_x', 'admin'], 'username': 'XXXXXX'}
    # проверка создание токенов
    assert response.cookies.get(security_config.token_name[0]) is not None
    assert response.cookies.get(security_config.token_name[1]) is not None


@pytest.mark.parametrize("method, url, params, status_code, detail", [
    ('post', '/auth/login', {"username": "XXXXXX", "password": "187654321_Af/"},
     HTTPStatus.FORBIDDEN, {'detail': 'В доступе отказано неверный пароль'}),  # неверный логин
    ('post', '/auth/login', {"username": "1XXXXXX", "password": "87654321_Af/"},
     HTTPStatus.FORBIDDEN, {'detail': 'В доступе отказано неверный логин'}),  # неверный пароль
])
async def test_login_error(method, url, params, status_code, detail, async_client: AsyncClient):
    """Проверка авторизации и создание cookies c token"""
    response = await async_client.request(method=method, path=url, params=params)

    assert response.status_code == status_code
    assert response.json() == detail
    # проверка создание токенов
    assert response.cookies.get(security_config.token_name[0]) is None
    assert response.cookies.get(security_config.token_name[1]) is None


async def test_logout(redis_client: Redis):
    """Проверка авторизации и создание cookies c token"""
    async with httpx.AsyncClient() as session:
        response = await session.post(f'{base_url}/auth/login',
                                      json={"username": "XXXXXX", "password": "87654321_Af/"}
                                      )

        assert response.status_code == HTTPStatus.OK

        token_access = session.cookies.get(security_config.token_name[0])
        token_refresh = session.cookies.get(security_config.token_name[1])

        assert token_access is not None
        assert token_refresh is not None

        print(session.cookies.extract_cookies(response))
        session.cookies.set(name=security_config.token_name[0], value=token_access)
        session.cookies.set(name=security_config.token_name[1], value=token_refresh)

        # проверка в REDIS токены отсутствуют в blacklist перед logout
        assert await redis_client.get(str(token_access)) is None
        assert await redis_client.get(str(token_refresh)) is None

        response1 = await session.post(f'{base_url}/auth/logout')

        assert response.status_code == HTTPStatus.OK
        token_access = response.cookies.get(security_config.token_name[0])
        token_refresh = response.cookies.get(security_config.token_name[1])

        assert token_access is not None
        assert token_refresh is not None
        # проверка в REDIS если 1 то присутствует в blacklist
        assert await redis_client.get(str(token_access)) == b'1'
        assert await redis_client.get(str(token_refresh)) == b'1'

