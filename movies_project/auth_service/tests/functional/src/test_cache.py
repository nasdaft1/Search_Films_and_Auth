from http import HTTPStatus

import pytest

from tests.functional.fixtures.client import AsyncClient

base_url = 'http://127.0.0.1:8000/api/v1'


@pytest.mark.parametrize("method, url, params, status_code, result", [
    ('post', '/auth/login',
     {"username": "87654321_Af/", "password": "12345678_Af/"},
     HTTPStatus.OK, ['username', 'Petrov1']),  # Создать пользователя
])
async def test_login(method, url, params, status_code, result, async_client: AsyncClient):
    response = await async_client.request(method=method, path=url, params=params, role=None)

    assert response.status_code == status_code

    # Очистка БД REDIS и выполнение запроса
    # await redis_client.flushdb()
    # response = await async_client.get(query)
    # # response = await async_client(query)
    # logging.info(f'Тестируем запрос параметры -> результат {query}')
    #
    # # Получаем словарь ключей в БД REDIS
    # assert response.status_code == HTTPStatus.OK
    # redis_keys = await redis_client.keys('*')
    # logging.info(f'key ={redis_keys[0]}')
    #
    # # Проверяем что в БД REDIS значение единственного ключа соответствует результату запроса
    # assert len(redis_keys) == 1
    # result = await redis_client.get(redis_keys[0])
    # assert json.loads(result) == response.json()
    #
    # # Подмена кеша для анализа, что именно он используется
    # await redis_client.set(redis_keys[0], json.dumps(substitution))
    # result = await redis_client.get(redis_keys[0])
    # logging.info(f'После подмены результата кеша {result}')
    #
    # # проверка, что подмена значения запроса произошла успешно
    # response = await async_client.get(query)
    # assert response.json() == substitution
    # await redis_client.flushdb()  # очистка кеша
