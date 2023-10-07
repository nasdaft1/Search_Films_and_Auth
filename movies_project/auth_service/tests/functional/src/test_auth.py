from http import HTTPStatus

import pytest

from core.config import security_config
from tests.functional.fixtures.client import AsyncClient

ADMIN_ROLE = security_config.admin_role_name


@pytest.mark.parametrize("method, url, params, access_role, status_code, result", [
    ('get', '/auth/login', {"username": "string", "password": "stringst"},
     HTTPStatus.OK, ['items', 3]),  # Список пользователей
    ('get', '/roles/list', {'page': 1, 'size': 50},
     [ADMIN_ROLE],
     HTTPStatus.OK, ['items', 1]),  # Список ролей
])
async def test_query_list(method, url, params, access_role, status_code, result, async_client: AsyncClient):
    """Проверка количество данных в списке"""
    response = await async_client.request(method=method, path=url, role=access_role, params=params)
    print(response)
    json = response.json()
    print(response.status_code)
    # logging.info(f'Тестируем запрос параметры -> результат {query}')
    assert response.status_code == status_code
    assert len(json.get(result[0], None)) == result[1]
