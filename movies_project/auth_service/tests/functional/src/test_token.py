import asyncio

import pytest
from fastapi import HTTPException
from httpx import AsyncClient as AsynClient

from main import app
from models.base import Token
from services.token import create_token, read_token

base_url = 'http://127.0.0.1:8000/api/v1'


async def test_token_live_time():
    data = Token(user_id='', roles=['admin', 'root'])
    async with AsynClient(app=app, base_url=f'{base_url}') as ac:
        token = create_token(data, 2)
        ac.cookies.set(name='XX', value=token)

        response = await ac.get('/auth/')
        token = ac.cookies.get(name='XX')
        print(token)
        token_xx = await read_token(token)
        assert token_xx == data

        await asyncio.sleep(4)
        response = await ac.get('/auth/')
        token = ac.cookies.get(name='XX')
        print(token)
        with pytest.raises(HTTPException) as error:
            token_xx = await read_token(token)
        assert error.value.status_code == 401
        assert error.value.detail == 'Токен истек'


async def test_token_login():
    data = Token(user_id='', roles=['admin', 'root'])
    async with AsynClient(app=app, base_url=f'{base_url}') as ac:
        token = create_token(data, 2)
        ac.cookies.set(name='XX', value=token)


async def test_token_logout():
    data = Token(user_id='', roles=['admin', 'root'])
    async with AsynClient(app=app, base_url=f'{base_url}') as ac:
        token = create_token(data, 2)
        ac.cookies.set(name='XX', value=token)

#
# @pytest.mark.parametrize("method, url, params, status_code, result", [
#     ('get', '/auth/login', {}, HTTPStatus.OK, ['items', 3]),  # авторизация
#     # ('get', '/auth/logout', {'page': 1, 'size': 50}, 200, ['items', 1]),  # Список ролей
# ])
# async def test_query_list(method, url, params, status_code, result, async_client: AsyncClient):
#     """Проверка количество данных в списке"""
#     response = await async_client.request(method=method, path=url, params=params)
#     print(response)
#     json = response.json()
#     print(response.status_code)
#     # logging.info(f'Тестируем запрос параметры -> результат {query}')
#     assert response.status_code == status_code
#     assert len(json.get(result[0], None)) == result[1]
