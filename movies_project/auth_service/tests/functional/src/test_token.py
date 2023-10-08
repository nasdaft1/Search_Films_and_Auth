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
