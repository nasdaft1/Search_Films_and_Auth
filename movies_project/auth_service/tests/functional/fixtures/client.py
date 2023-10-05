from dataclasses import dataclass
from uuid import UUID

import aiohttp
import pytest_asyncio
from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError
from tests.db import engine, async_session
from models.db import Base, User, Role
from core.config import security_config
from werkzeug.security import generate_password_hash

from ..config import config


@pytest_asyncio.fixture(scope='session')
async def client_session() -> aiohttp.ClientSession:
    """Создадим экземпляр сессии aiohttp, для всей сессии."""
    async with aiohttp.ClientSession() as session:
        yield session


@dataclass
class Response:
    status_code: int
    _json: dict

    def json(self) -> dict:
        return self._json


class AsyncClient:

    def __init__(self, base_url: str, session: ClientSession) -> None:
        self.base_url = base_url.rstrip('/')
        self.session = session

    async def request(self, method: str, path: str, params: dict | None = None) -> Response:
        url = self.base_url + '/' + path.lstrip('/')
        data = None
        if method in ['post', 'put']:
            print('POST or PUT')
            data = params
            params = None
        async with self.session.request(method=method, url=url, json=data,
                                        params=params, allow_redirects=True) as response:
            print(f'{url=}')
            try:
                result = await response.json()
            except (ContentTypeError, Exception):
                return Response(_json={}, status_code=response.status)
            return Response(_json=result, status_code=response.status)


@pytest_asyncio.fixture
async def async_client(client_session: aiohttp.ClientSession) -> AsyncClient:
    return AsyncClient(base_url=config.base_url, session=client_session)


@pytest_asyncio.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        user = User(
            id=UUID('3139049d-9c2b-45eb-b373-2f3b9454eb21'),
            username='Antonov',
            password_hash=generate_password_hash(
                '12345678_Af/',
                method=security_config.hashing_method.lower(),
                salt_length=security_config.hashing_salt_length),
            email='xxx@mail.ru',
            full_name='asd')
        session.add(user)

        role = Role(
            id=UUID('11ad5288-e5b2-4979-afbd-e4a121720ddb'),
            name='admin',
            service_name='admin1'
        )
        session.add(role)

        await session.commit()

    yield
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    # logging.info(f'Удаление бд с  ')
