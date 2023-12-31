from http import HTTPStatus

import pytest

from core.config import security_config
from tests.functional.fixtures.client import AsyncClient

ADMIN_ROLE = security_config.admin_role_name


@pytest.mark.parametrize('method, url, params, status_code, result', [
    ('post', '/auth/login',
     {'username': 'XXXXXX', 'password': '87654321_Af/'},
     HTTPStatus.OK, ['username', 'XXXXXX']),  # Создать пользователя

    ('post', '/users/create',
     {'username': 'Petrov1', 'password': 'Aa4523*bmII', 'full_name': 'string', 'email': 'user1@example.com'},
     HTTPStatus.CREATED, ['username', 'Petrov1']),  # Создать пользователя
    ('post', '/users/create',
     {'username': 'Petrov', 'password': 'Aa1#ydmbmII', 'full_name': 'string', 'email': 'user1@example.com'},
     HTTPStatus.CONFLICT,
     ['detail', 'Пользователь с такими данными уже существует.']),  # Создать пользователя одинакового
    ('post', '/users/create',
     {'username': 'Ivanov', 'password': 'Aa1#ydmbmII', 'full_name': 'string', 'email': 'user3@example.com'},
     HTTPStatus.CREATED,
     ['email', 'user3@example.com']),  # Создать пользователя
    ('post', '/users/create',
     {'username': 'Kulik', 'password': 'Aa1#ydmbmII', 'full_name': 'string', 'email': 'user3@example.com'},
     HTTPStatus.CONFLICT,
     ['detail', 'Пользователь с такими данными уже существует.']),
    # Создать пользователя с одинаковой почтой

    ('get', '/users/get', {'user_id': '3139049d-9c2b-45eb-b373-2f3b9454eb21'},
     HTTPStatus.OK, ['username', 'Antonov']),
    # Получить пользователя
    ('get', '/users/get', {'user_id': '00000000-0000-0000-0000-000000000000'},
     HTTPStatus.NOT_FOUND, ['id', None]),  # Получить пользователя

    ('post', '/roles/create', {'name': 'user1', 'service_name': 'string', 'description': 'string'},
     HTTPStatus.CREATED, ['name', 'user1']),
    # Создать роль
    ('post', '/roles/create', {'name': 'user2', 'service_name': 'string', 'description': 'string'},
     HTTPStatus.CONFLICT, ['name', None]),
    # Проверка уникальности service_name

    ('get', '/roles/get', {'role_id': '11ad5288-e5b2-4979-afbd-e4a121720ddb'},
     HTTPStatus.OK, ['service_name', 'admin1']),  # Получить роль
    ('put', '/roles/update', {'name': 'string2', 'service_name': 'string2', 'description': 'string2',
                              'id': '11ad5288-e5b2-4979-afbd-e4a121720ddb'},
     HTTPStatus.OK, ['id', '']),  # Изменить роль

    ('delete', '/roles/delete', {'role_id': '11ad5288-e5b2-4979-afbd-e4a121720ddb'},
     HTTPStatus.NO_CONTENT, ['id', '']),  # Удалить роль

    ('get', '/users/roles', {'user_id': '11111111-1111-1111-1111-111111111111'},
     HTTPStatus.OK, 1),  # Получить роли пользователя
    # http://127.0.0.1:8000/api/v1/roles/list?page=1&size=50

    ('get', '/users/history', {'user_id': '11111111-1111-1111-1111-111111111111'},
     HTTPStatus.OK, 4),  # Получить роли пользователя
    # http://127.0.0.1:8000/api/v1/roles/list?page=1&size=50

])
async def test_query(method, url, params, status_code, result, async_client: AsyncClient):
    """Тестирование поиска"""
    response = await async_client.request(method=method, path=url, params=params)
    print(response)
    json = response.json()
    print(response.status_code)
    # logging.info(f'Тестируем запрос параметры -> результат {query}')
    assert response.status_code == status_code
    if isinstance(json, dict):
        print(f'id = {json.get("id", None)} {method}')
        assert json.get(result[0], None) == result[1]
    if isinstance(json, list):
        assert len(json) == result


@pytest.mark.parametrize('method, url, params,  status_code, result', [
    ('get', '/users/list', {},
     HTTPStatus.OK, ['items', 4]),  # Список пользователей
    ('get', '/roles/list', {'page': 1, 'size': 50},
     HTTPStatus.OK, ['items', 2]),  # Список ролей
])
async def test_query_list(method, url, params, status_code, result, async_client: AsyncClient):
    """Проверка количество данных в списке"""
    response = await async_client.request(method=method, path=url, params=params)
    print(response)
    json = response.json()
    print(response.status_code)
    # logging.info(f'Тестируем запрос параметры -> результат {query}')
    assert response.status_code == status_code
    assert len(json.get(result[0], None)) == result[1]


@pytest.mark.parametrize('method, url, params,  status_code, result', [
    ('post', '/auth/logout', None,
     HTTPStatus.OK, 'Вы успешно вышли из системы'),  # Разлогирование
    ('get', '/roles/list', {'page': 1, 'size': 50},
     HTTPStatus.FORBIDDEN, {'detail': 'В доступе отказано авторизуйтесь'}),  # запрос при разлогиненом пользователе
])
async def test_logout_list(method, url, params, status_code, result, async_client: AsyncClient):
    """Проверка количество данных в списке"""
    response = await async_client.request(method=method, path=url, params=params)
    print(response)
    json = response.json()
    print(response.status_code)
    # logging.info(f'Тестируем запрос параметры -> результат {query}')
    assert response.status_code == status_code
    assert response.json() == result
